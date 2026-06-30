// ── Language icon mapping ──────────────────────────────────────
const EXT_TO_ICON = {
  ".c": "c",
  ".cpp": "cpp",
  ".py": "python",
  ".js": "javascript",
  ".vdx": "vdx",
};

// ── Language display colors (matching chart palette) ───────────
const LANG_COLORS = {
  ".c": "#7aa2f7",
  ".cpp": "#bb9af7",
  ".py": "#e0af68",
  ".js": "#f7768e",
  ".vdx": "#9ece6a",
};

// ── Fetch and render ───────────────────────────────────────────

async function init() {
  try {
    const res = await fetch("results.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderHero(data);
    renderRankings(data);
    renderCharts(data);
    renderToolchains(data);
  } catch (err) {
    document.querySelectorAll(".loading-block").forEach((el) => {
      el.textContent = `Failed to load results.json — ${err.message}`;
      el.style.color = "#f7768e";
    });
  }
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
    card.className = "test-card";

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
              <span class="rank-time" style="color: ${color}">${r.median_ms.toFixed(2)} ms</span>
              <div class="rank-bar" style="width: ${barWidth}%; background: ${color}"></div>
            </div>`;
          })
          .join("")}
      </div>
    `;
    container.appendChild(card);
  }
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

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

init();
