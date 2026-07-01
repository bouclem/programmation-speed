// ── Language icon mapping ──────────────────────────────────────
const EXT_TO_ICON = {
  ".c": "c",
  ".cpp": "cpp",
  ".py": "python",
  ".js": "javascript",
  ".vdx": "vdx",
  ".go": "go",
  ".zig": "zig",
  ".rs": "rust",
};

// ── Language display colors (matching chart palette) ───────────
const LANG_COLORS = {
  ".c": "#7aa2f7",
  ".cpp": "#bb9af7",
  ".py": "#e0af68",
  ".js": "#f7768e",
  ".vdx": "#9ece6a",
  ".go": "#7dcfff",
  ".zig": "#f38ba8",
  ".rs": "#ff9e64",
  ".java": "#cba6f7",
};

// ── State ──────────────────────────────────────────────────────
let BENCHMARK_DATA = null;

// ── Test descriptions ──────────────────────────────────────────
const TEST_DESC = {
  hello: "Simple Hello World print. Measures startup + I/O overhead.",
  count: "Triple-nested loop counting to 1000. Measures raw loop iteration speed.",
  fibonacci: "Recursive fib(30). Measures function call overhead and recursion.",
  primes: "Trial division prime counting up to 10000. Tests arithmetic + branching.",
  sort: "Bubble sort of 100 elements. Tests array access and comparison logic.",
};

// ── Fetch and render ───────────────────────────────────────────

async function init() {
  try {
    const res = await fetch("results.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    BENCHMARK_DATA = await res.json();
    renderHero(BENCHMARK_DATA);
    renderRankings(BENCHMARK_DATA);
    renderCharts(BENCHMARK_DATA);
    renderToolchains(BENCHMARK_DATA);
    handleRoute();
  } catch (err) {
    document.querySelectorAll(".loading-block").forEach((el) => {
      el.textContent = `Failed to load results.json — ${err.message}`;
      el.style.color = "#f7768e";
    });
  }
}

// ── Hash routing ───────────────────────────────────────────────

window.addEventListener("hashchange", handleRoute);

function handleRoute() {
  const hash = window.location.hash;
  const rankingsSection = document.getElementById("rankings");
  const detailSection = document.getElementById("test-detail");

  const match = hash.match(/^#test=(.+)$/);
  if (match && BENCHMARK_DATA) {
    const testName = match[1];
    if (BENCHMARK_DATA.tests[testName]) {
      renderTestDetail(testName);
      rankingsSection.style.display = "none";
      detailSection.style.display = "";
      detailSection.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
  }

  rankingsSection.style.display = "";
  detailSection.style.display = "none";
}

function renderHero(data) {
  const ts = data.timestamp ? new Date(data.timestamp) : null;
  const tsStr = ts
    ? ts.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }) +
      " " +
      ts.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })
    : "—";

  document.getElementById("timestamp").textContent = `Last run: ${tsStr}`;
  document.getElementById("run-count").textContent = data.runs || "—";
  document.getElementById("runs-test").textContent = data.runs || "—";

  const testCount = Object.keys(data.tests).length;
  document.getElementById("test-count").textContent = testCount;

  const langSet = new Set();
  for (const test of Object.values(data.tests)) {
    for (const r of test.rankings) {
      langSet.add(r.ext);
    }
  }
  document.getElementById("lang-count").textContent = langSet.size;
}

function renderRankings(data) {
  const container = document.getElementById("rankings-content");
  container.innerHTML = "";

  for (const [testName, testData] of Object.entries(data.tests)) {
    const card = document.createElement("div");
    card.className = "test-card test-card--clickable";
    card.onclick = () => { window.location.hash = `test=${testName}`; };

    const fastest = testData.rankings[0];
    const maxTime = testData.rankings[testData.rankings.length - 1].median_ms;

    card.innerHTML = `
      <div class="test-card-header">
        <span class="test-card-name">${escapeHtml(testName)}</span>
        <span class="test-card-count">${testData.rankings.length} entries</span>
      </div>
      <div class="test-card-body">
        ${testData.rankings
          .map((r, i) => {
            const icon = EXT_TO_ICON[r.ext] || "";
            const color = LANG_COLORS[r.ext] || "var(--text-dim)";
            const barWidth = (r.median_ms / fastest.median_ms) * 100;
            const rankClass = i < 3 ? `rank-num--${i + 1}` : "";
            return `
            <div class="ranking-row">
              <span class="rank-num ${rankClass}">${i + 1}</span>
              ${icon ? `<img class="rank-icon" src="icons/${icon}.png" alt="${escapeHtml(r.label)}" />` : ""}
              <span class="rank-label">${escapeHtml(r.label)}</span>
              <span class="rank-time" style="color: ${color}">${fmtTime(r.median_ms)}</span>
              <div class="rank-bar" style="width: ${barWidth}%; background: ${color}"></div>
            </div>`;
          })
          .join("")}
      </div>
    `;
    container.appendChild(card);
  }
}

function renderTestDetail(testName) {
  const testData = BENCHMARK_DATA.tests[testName];
  const fastest = testData.rankings[0];
  const slowest = testData.rankings[testData.rankings.length - 1];

  document.getElementById("detail-title").textContent = testName;
  document.getElementById("detail-desc").textContent = TEST_DESC[testName] || "";

  const container = document.getElementById("detail-content");
  const icon = EXT_TO_ICON[fastest.ext] || "";
  const winnerColor = LANG_COLORS[fastest.ext] || "var(--text-dim)";

  container.innerHTML = `
    <div class="detail-winner">
      ${icon ? `<img class="detail-winner-icon" src="icons/${icon}.png" alt="${escapeHtml(fastest.label)}" />` : ""}
      <div class="detail-winner-info">
        <span class="detail-winner-label">Fastest</span>
        <span class="detail-winner-name" style="color: ${winnerColor}">${escapeHtml(fastest.label)}</span>
        <span class="detail-winner-time">${fmtTime(fastest.median_ms)} median</span>
      </div>
      <div class="detail-winner-info">
        <span class="detail-winner-label">Slowest</span>
        <span class="detail-winner-name" style="color: ${LANG_COLORS[slowest.ext] || "var(--text-dim)"}">${escapeHtml(slowest.label)}</span>
        <span class="detail-winner-time">${fmtTime(slowest.median_ms)} median</span>
      </div>
    </div>

    <div class="detail-chart">
      <img src="data/${testName}_benchmark.png" alt="${escapeHtml(testName)} benchmark chart" loading="lazy" />
    </div>

    <table class="detail-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Language</th>
          <th>Median (ms)</th>
          <th>Min (ms)</th>
          <th>vs Fastest</th>
        </tr>
      </thead>
      <tbody>
        ${testData.rankings
          .map((r, i) => {
            const langIcon = EXT_TO_ICON[r.ext] || "";
            const color = LANG_COLORS[r.ext] || "var(--text-dim)";
            const ratio = (r.median_ms / fastest.median_ms).toFixed(2);
            return `
            <tr>
              <td class="detail-rank ${i < 3 ? `rank-num--${i + 1}` : ""}">${i + 1}</td>
              <td class="detail-lang">
                ${langIcon ? `<img class="rank-icon" src="icons/${langIcon}.png" alt="" />` : ""}
                <span style="color: ${color}">${escapeHtml(r.label)}</span>
              </td>
              <td class="detail-num">${fmtTime(r.median_ms)}</td>
              <td class="detail-num">${fmtTime(r.min_ms)}</td>
              <td class="detail-ratio">${ratio}x</td>
            </tr>`;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

function renderCharts(data) {
  const container = document.getElementById("charts-content");
  container.innerHTML = "";

  const combined = document.createElement("div");
  combined.className = "chart-card";
  combined.innerHTML = `
    <img src="data/combined_benchmark.png" alt="Combined benchmark chart" loading="lazy" />
    <div class="chart-card-label">combined_benchmark.png</div>
  `;
  container.appendChild(combined);
}

function renderToolchains(data) {
  const container = document.getElementById("toolchain-list");
  if (!container) return;
  container.innerHTML = "";

  for (const [ext, chains] of Object.entries(data.toolchains)) {
    for (const tc of chains) {
      const item = document.createElement("div");
      item.className = "toolchain-item";
      item.textContent = `${tc.id} ${tc.version}  (${ext})`;
      container.appendChild(item);
    }
  }
}

function fmtTime(ms) {
  if (ms < 1) return ms.toFixed(2) + " ms";
  if (ms < 1000) return ms.toFixed(1) + " ms";
  return (ms / 1000).toFixed(1) + " s";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

init();
