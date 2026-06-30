# Programming Speed

Benchmark tool comparing programming language execution speed across test cases.

## What It Does

- Discovers test files in `src/tests/` (grouped by filename stem)
- Auto-detects all available compilers/interpreters on PATH
- Runs each test 10 times per toolchain, takes median timing
- Generates dark-themed horizontal bar chart PNGs in `results/`
- Outputs `results.json` with full rankings for the website

## Supported Languages

| Language | Extensions | Toolchains |
|----------|-----------|------------|
| C | `.c` | gcc, clang, tcc |
| C++ | `.cpp` | g++, clang++ |
| Python | `.py` | python, python3, pypy, pypy3 |
| JavaScript | `.js` | node, deno, bun |
| VDX | `.vdx` | vdx |

Only toolchains installed on the system are benchmarked.

## Usage

```bash
# Download language icons (first time only)
python download_icon.py

# Run benchmarks
python benchmark.py
```

Output goes to `results/`:
- `<test>_benchmark.png` — per-test bar chart
- `combined_benchmark.png` — all tests combined
- `results.json` — machine-readable results

## Adding Tests

Create files in `src/tests/` with the same stem but different extensions:

```
src/tests/mytest.c
src/tests/mytest.cpp
src/tests/mytest.py
src/tests/mytest.js
src/tests/mytest.vdx
```

The benchmark script auto-discovers them.

## Website

Static results showcase in `src/website/`. Deploy to Vercel:

```bash
cd src/website
npx vercel
```

The website loads `results.json` and displays rankings with charts.

## Project Structure

```
programmation-speed/
├── benchmark.py          # Main benchmark script
├── download_icon.py      # Download language icons
├── icons/                # Language logo PNGs
├── results/              # Generated charts + JSON
├── src/
│   ├── tests/            # Test files per language
│   └── website/          # Static results website
└── docs/                 # Documentation
```
