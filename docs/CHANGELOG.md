# Changelog

## v0.2.0 — 2026-06-30

- Added VDX language support
- Auto-detect all available toolchains per language (gcc, clang, g++, clang++, pypy, deno, bun, etc.)
- Dark theme horizontal bar charts with language icons
- `download_icon.py` — auto-download and crop language icons from devicon CDN
- `results.json` output for website consumption
- Static results showcase website (`src/website/`)

## v0.1.0 — 2026-06-30

- Initial benchmark script with C, C++, Python, JavaScript support
- Test cases: hello world, count to 10 (3 nested loops)
- Matplotlib Agg backend (no GUI window)
- Bar chart PNGs saved to `results/`
