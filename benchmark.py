#!/usr/bin/env python3
"""Benchmark programming language speed across test cases.

Discovers test files in src/tests/, auto-detects ALL available
compilers/interpreters per language, runs each test with every
detected toolchain, and saves bar chart PNGs to results/.
Uses matplotlib with the Agg backend (no GUI window opens).
"""

import re
import shutil
import subprocess
import time
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend — save only, no window
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# ── Configuration ──────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.resolve()
TESTS_DIR = ROOT / "src" / "tests"
RESULTS_DIR = ROOT / "results"
ICONS_DIR = ROOT / "icons"
RUNS = 10  # Number of timed runs per test (median is used)

# Dark theme colors
BG_COLOR = "#1e1e2e"
PANEL_COLOR = "#2a2a3e"
TEXT_COLOR = "#e0e0e0"
GRID_COLOR = "#3a3a5e"
TITLE_COLOR = "#ffffff"

# Bright bar colors for dark theme
BAR_COLORS = [
    "#7aa2f7", "#9ece6a", "#f7768e", "#bb9af7",
    "#e0af68", "#7dcfff", "#ff9e64", "#b4befe",
    "#cba6f7", "#f38ba8", "#a6e3a1", "#94e2d5",
]

# Map file extension → icon filename in icons/
EXT_TO_ICON = {
    ".c": "c",
    ".cpp": "cpp",
    ".py": "python",
    ".js": "javascript",
    ".vdx": "vdx",
}


def load_icon(ext, size=0.08):
    """Load a PNG icon for a language extension. Returns OffsetImage or None."""
    icon_name = EXT_TO_ICON.get(ext)
    if not icon_name:
        return None
    icon_path = ICONS_DIR / f"{icon_name}.png"
    if not icon_path.exists():
        return None
    img = Image.open(icon_path)
    # Convert to RGBA if needed
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return OffsetImage(img, zoom=size)

# ── Toolchain registry ─────────────────────────────────────────────────────
# Each entry: toolchain id -> (compile_cmd_fn | None, run_cmd_fn)
# compile_cmd_fn(src, out) -> list[str]   (None = interpreted)
# run_cmd_fn(target) -> list[str]
# The toolchain is only used if its binary is found on PATH.

TOOLCHAINS = {
    ".c": [
        {
            "id": "gcc",
            "compile": lambda src, out: ["gcc", "-O2", "-o", out, src],
            "run": lambda exe: [exe],
        },
        {
            "id": "clang",
            "compile": lambda src, out: ["clang", "-O2", "-o", out, src],
            "run": lambda exe: [exe],
        },
        {
            "id": "tcc",
            "compile": lambda src, out: ["tcc", "-O2", "-o", out, src],
            "run": lambda exe: [exe],
        },
    ],
    ".cpp": [
        {
            "id": "g++",
            "compile": lambda src, out: ["g++", "-O2", "-o", out, src],
            "run": lambda exe: [exe],
        },
        {
            "id": "clang++",
            "compile": lambda src, out: ["clang++", "-O2", "-o", out, src],
            "run": lambda exe: [exe],
        },
    ],
    ".py": [
        {"id": "python", "compile": None, "run": lambda src: ["python", src]},
        {"id": "python3", "compile": None, "run": lambda src: ["python3", src]},
        {"id": "pypy", "compile": None, "run": lambda src: ["pypy", src]},
        {"id": "pypy3", "compile": None, "run": lambda src: ["pypy3", src]},
    ],
    ".js": [
        {"id": "node", "compile": None, "run": lambda src: ["node", src]},
        {"id": "deno", "compile": None, "run": lambda src: ["deno", "run", src]},
        {"id": "bun", "compile": None, "run": lambda src: ["bun", src]},
    ],
    ".vdx": [
        {"id": "vdx", "compile": None, "run": lambda src: ["vdx", src], "fallback_version": "0.1.2"},
    ],
}



# ── Toolchain detection ────────────────────────────────────────────────────


def is_available(binary):
    """Return True if *binary* is found on PATH."""
    return shutil.which(binary) is not None


def get_version(binary):
    """Try to extract a short version string for a compiler/interpreter."""
    # -dumpversion gives clean "16.1.0" for gcc/g++; try it first
    for args in (["-dumpversion"], ["--version"], ["-v"]):
        try:
            r = subprocess.run(
                [binary] + args,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode != 0:
                continue
            text = (r.stdout + r.stderr).strip()
            if not text:
                continue
            first_line = text.splitlines()[0]
            # Try to pull a version number (x.y.z pattern) from the line
            m = re.search(r"\d+\.\d+(?:\.\d+)?", first_line)
            if m:
                return m.group()
            # Fallback: first token containing a digit
            for token in first_line.replace(",", " ").split():
                if any(c.isdigit() for c in token):
                    return token
            return first_line[:20]
        except Exception:
            continue
    return "?"


def detect_toolchains():
    """Detect all available toolchains per extension.

    A toolchain is only included if its binary is on PATH AND can
    successfully respond to --version / -dumpversion (filters out
    Windows Store stubs like python3 that exist but don't work).

    Returns: {ext: [{id, compile, run, version}]}
    """
    available = {}
    for ext, chain_list in TOOLCHAINS.items():
        chains = []
        for tc in chain_list:
            if not is_available(tc["id"]):
                continue
            version = get_version(tc["id"])
            if version == "?":
                # Use fallback version if provided (e.g. vdx has no --version flag)
                version = tc.get("fallback_version", "?")
            if version == "?":
                # Binary exists on PATH but failed to run — skip stubs
                continue
            chains.append({
                "id": tc["id"],
                "compile": tc["compile"],
                "run": tc["run"],
                "version": version,
            })
        if chains:
            available[ext] = chains
    return available


def toolchain_label(ext, tc):
    """Human-readable label, e.g. 'C / gcc 16.1.0' or 'Python / python 3.12.10'."""
    lang = {".c": "C", ".cpp": "C++", ".py": "Python", ".js": "JS", ".vdx": "VDX"}[ext]
    return f"{lang} / {tc['id']} {tc['version']}"


# ── Core logic ─────────────────────────────────────────────────────────────


def discover_tests(supported_exts):
    """Scan src/tests/ and group files by test name (filename stem).

    Returns: {test_name: {extension: Path}}
    """
    groups = {}
    if not TESTS_DIR.exists():
        return groups
    for f in sorted(TESTS_DIR.iterdir()):
        if f.is_file() and f.suffix in supported_exts:
            groups.setdefault(f.stem, {})[f.suffix] = f
    return groups


def compile_test(src_path, tc, suffix_tag):
    """Compile a source file with a given toolchain. Returns exe path or None."""
    out_path = src_path.with_name(f"{src_path.stem}_{suffix_tag}.exe")
    cmd = tc["compile"](str(src_path), str(out_path))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except (FileNotFoundError, OSError) as e:
        print(f"    ✗ Cannot execute compiler: {e}")
        return None
    if result.returncode != 0:
        print(f"    ✗ Compile error: {result.stderr.strip()}")
        return None
    return str(out_path)


def run_test(target, tc, runs=RUNS):
    """Run a test *runs* times. Returns list of elapsed seconds (empty on error)."""
    run_cmd = tc["run"](target)
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        try:
            result = subprocess.run(run_cmd, capture_output=True, text=True)
        except (FileNotFoundError, OSError) as e:
            print(f"    ✗ Cannot execute: {e}")
            return []
        elapsed = time.perf_counter() - start
        if result.returncode != 0:
            print(f"    ✗ Run error: {result.stderr.strip()}")
            return []
        times.append(elapsed)
    return times


def cleanup_exe(test_name):
    """Remove compiled .exe files for a given test name."""
    for exe in TESTS_DIR.glob(f"{test_name}*.exe"):
        try:
            exe.unlink()
        except OSError:
            pass


# ── Plotting ───────────────────────────────────────────────────────────────


def _style_dark(ax, fig):
    """Apply dark theme styling to figure and axes."""
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(PANEL_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.title.set_color(TITLE_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)


def plot_single_test(test_name, results):
    """Save a horizontal bar chart for one test group to results/<test>_benchmark.png."""
    if not results:
        return

    # Sort fastest first (smallest median at top)
    langs = sorted(results.keys(), key=lambda l: results[l]["median"], reverse=True)
    medians_ms = [results[l]["median"] * 1000 for l in langs]
    mins_ms = [results[l]["min"] * 1000 for l in langs]

    fig, ax = plt.subplots(figsize=(10, max(4, len(langs) * 0.8 + 1.5)))
    _style_dark(ax, fig)

    y_pos = range(len(langs))
    colors = [BAR_COLORS[i % len(BAR_COLORS)] for i in range(len(langs))]

    # Horizontal bars — median (full) and min (overlay, slightly shorter bar height)
    bars = ax.barh(y_pos, medians_ms, color=colors, height=0.55, label="Median")
    ax.barh(y_pos, mins_ms, color=colors, height=0.25, alpha=0.35, label="Min")

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(langs, fontsize=10)
    ax.set_xlabel("Time (ms)", fontsize=11)
    ax.set_title(f"Benchmark: {test_name}", fontsize=14, fontweight="bold", pad=12)
    ax.legend(facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    ax.grid(axis="x", color=GRID_COLOR, alpha=0.4)
    ax.invert_yaxis()  # Fastest at top

    # Value labels at end of bars
    x_max = max(medians_ms) if medians_ms else 1
    for bar, val in zip(bars, medians_ms):
        ax.text(
            bar.get_width() + x_max * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f} ms",
            ha="left",
            va="center",
            fontsize=9,
            color=TEXT_COLOR,
        )

    # Place icons next to y-axis labels (left side)
    for i, lang in enumerate(langs):
        ext = results[lang].get("ext", "")
        icon = load_icon(ext, size=0.25)
        if icon:
            ab = AnnotationBbox(
                icon,
                (-x_max * 0.04, i),
                frameon=False,
                xycoords=("data", "data"),
                box_alignment=(1, 0.5),
            )
            ax.add_artist(ab)

    ax.set_xlim(left=-x_max * 0.20)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f"{test_name}_benchmark.png", dpi=150)
    plt.close(fig)
    print(f"  → Saved: results/{test_name}_benchmark.png")


def plot_combined(all_results):
    """Save a grouped horizontal bar chart to results/combined_benchmark.png.

    Each test group is independently sorted by that test's median time
    (fastest first), so the ordering is always correct per test.
    """
    test_names = list(all_results.keys())
    n_tests = len(test_names)

    # Sort languages within each test by that test's median (fastest first)
    test_langs = {}
    for tn in test_names:
        test_langs[tn] = sorted(
            all_results[tn].keys(),
            key=lambda l: all_results[tn][l]["median"],
        )

    n_langs = max(len(langs) for langs in test_langs.values())
    group_height = 0.8
    bar_height = group_height / max(n_langs, 1)

    fig, ax = plt.subplots(
        figsize=(12, max(5, n_tests * n_langs * 0.35 + 2))
    )
    _style_dark(ax, fig)

    y_positions = []
    y_labels = []
    icon_exts = []

    for ti, test_name in enumerate(test_names):
        langs = test_langs[test_name]
        for li, lang in enumerate(langs):
            y = ti * (group_height + 0.4) + (li - len(langs) / 2 + 0.5) * bar_height
            y_positions.append(y)
            y_labels.append(f"{test_name} — {lang}")
            ext = all_results[test_name].get(lang, {}).get("ext", "")
            icon_exts.append(ext)

            val = all_results[test_name].get(lang, {}).get("median", 0) * 1000
            color = BAR_COLORS[li % len(BAR_COLORS)]
            ax.barh(y, val, height=bar_height * 0.9, color=color, alpha=0.9)

            if val > 0:
                ax.text(
                    val + 0.5,
                    y,
                    f"{val:.1f}",
                    ha="left",
                    va="center",
                    fontsize=8,
                    color=TEXT_COLOR,
                )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=9)
    ax.set_xlabel("Time (ms)", fontsize=11)
    ax.set_title("Programming Language Speed Comparison", fontsize=14, fontweight="bold", pad=12)
    ax.grid(axis="x", color=GRID_COLOR, alpha=0.4)
    ax.invert_yaxis()

    # Place icons next to y-axis labels
    x_max = ax.get_xlim()[1]
    for i, (y, ext) in enumerate(zip(y_positions, icon_exts)):
        if not y_labels[i]:
            continue
        icon = load_icon(ext, size=0.20)
        if icon:
            ab = AnnotationBbox(
                icon,
                (-x_max * 0.04, y),
                frameon=False,
                xycoords=("data", "data"),
                box_alignment=(1, 0.5),
            )
            ax.add_artist(ab)

    ax.set_xlim(left=-x_max * 0.20)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "combined_benchmark.png", dpi=150)
    plt.close(fig)
    print(f"  → Saved: results/combined_benchmark.png")


# ── Main ───────────────────────────────────────────────────────────────────


def benchmark_all():
    """Run all benchmarks and generate charts."""
    RESULTS_DIR.mkdir(exist_ok=True)

    # Detect available toolchains
    available = detect_toolchains()
    if not available:
        print("No compilers/interpreters found on PATH.")
        return

    print("Detected toolchains:")
    for ext, chains in available.items():
        labels = [f"{c['id']} {c['version']}" for c in chains]
        print(f"  {ext}: {', '.join(labels)}")
    print()

    supported_exts = set(available.keys())
    groups = discover_tests(supported_exts)

    if not groups:
        print("No test files found in src/tests/")
        return

    print(f"Found {len(groups)} test group(s): {', '.join(sorted(groups))}")
    print(f"Running {RUNS} iterations per test for median timing\n")

    all_results = {}

    for test_name, files in sorted(groups.items()):
        print(f"=== {test_name} ===")
        test_results = {}

        for ext, src_path in sorted(files.items()):
            chains = available.get(ext, [])
            for tc in chains:
                label = toolchain_label(ext, tc)
                print(f"  {label}  ({src_path.name})")

                # Compile if needed
                target = str(src_path)
                if tc["compile"] is not None:
                    suffix_tag = tc["id"].replace("+", "pp")
                    exe = compile_test(src_path, tc, suffix_tag)
                    if exe is None:
                        continue
                    target = exe

                # Benchmark
                times = run_test(target, tc)
                if not times:
                    continue

                med = statistics.median(times)
                mn = min(times)
                test_results[label] = {"median": med, "min": mn, "all": times, "ext": ext}
                print(f"    median: {med*1000:.3f} ms | min: {mn*1000:.3f} ms")

        all_results[test_name] = test_results
        plot_single_test(test_name, test_results)
        cleanup_exe(test_name)

    if all_results:
        plot_combined(all_results)

    print(f"\nDone. Charts saved to {RESULTS_DIR}/")


if __name__ == "__main__":
    benchmark_all()
