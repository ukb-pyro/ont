# Create a small landing site with an animated canvas "crawler" hero and staged links.
# Files:
# - index.html
# - assets/style.css
# - (no external images needed; animation is JS-based)
# Then zip as /mnt/data/ont-landing.zip

import os, zipfile, textwrap, json, pathlib, shutil

root = pathlib.Path("/mnt/data/ont-landing")
assets = root / "assets"
assets.mkdir(parents=True, exist_ok=True)

index_html = """<!DOCTYPE html>
<html lang="en-US">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ont</title>
  <meta name="description" content="Ontology as tree — roots to canopy. A tiny landing that visualizes a find-crawl vibe." />
  <link rel="stylesheet" href="assets/style.css" />
  <meta property="og:title" content="ont" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://ukb-pyro.github.io/ont/" />
  <meta property="og:site_name" content="ont" />
</head>
<body>
  <header class="site-header">
    <div class="brand">ont</div>
    <nav class="nav">
      <a href="https://ukb-pyro.github.io/truth/" target="_blank" rel="noopener">truth</a>
      <a href="https://ukubona-llc.github.io/cpho/" target="_blank" rel="noopener">time is compressed</a>
      <a href="https://ukb-pyro.github.io/i-had-a-dream/" target="_blank" rel="noopener">dream</a>
      <a href="https://github.com/ukb-pyro" target="_blank" rel="noopener">github</a>
    </nav>
  </header>

  <main>
    <!-- HERO: animated canvas crawl (devil/god idleness vibe) -->
    <section class="hero">
      <canvas id="crawl" width="1280" height="420" aria-label="crawler animation"></canvas>
      <div class="hero-controls">
        <button id="restart">restart</button>
        <button id="pause">pause</button>
        <button id="play">play</button>
        <span class="cmd">find . -maxdepth 2 ! -name <strong>ingest.py</strong> -exec rm -rf {} +</span>
      </div>
    </section>

    <!-- Cards -->
    <section class="grid">
      <a class="card" href="https://ukb-pyro.github.io/truth/" target="_blank" rel="noopener">
        <h3>Canopy</h3>
        <p>Compressed time, emergence, intelligence.</p>
      </a>
      <a class="card" href="https://ukubona-llc.github.io/cpho/" target="_blank" rel="noopener">
        <h3>Time is Compressed</h3>
        <p>Signals fold; resonance survives.</p>
      </a>
      <a class="card" href="https://ukb-pyro.github.io/i-had-a-dream/" target="_blank" rel="noopener">
        <h3>Dream</h3>
        <p>Electron’s-eye view of the circuit.</p>
      </a>
      <a class="card" href="https://github.com/ukb-pyro?tab=repositories" target="_blank" rel="noopener">
        <h3>Branches</h3>
        <p>1,000+ repos — the wandering routes.</p>
      </a>
    </section>

    <!-- Ontology legend -->
    <section class="legend">
      <h2>roots → trunk → branches → leaves → canopy</h2>
      <ol>
        <li><b>ukuvula</b> — open/seed (parameters)</li>
        <li><b>ukuzula</b> — wander (routes)</li>
        <li><b>ukukona</b> — collide (ingest)</li>
        <li><b>ukubona</b> — see (observe)</li>
        <li><b>ukukula</b> — grow (echo)</li>
      </ol>
    </section>
  </main>

  <footer class="site-footer">
    <small>© ont — a tiny recursive landing. Built lightweight, no deps.</small>
  </footer>

<script>
// Tiny canvas animation of a "crawler" traversing a directory graph.
// Visual: a tree-like grid of nodes; crawler snakes through edges
// while selectively "pruning" nodes (fade) except the protected 'ingest.py'.

(() => {
  const canvas = document.getElementById('crawl');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;

  // Graph layout (grid-ish tree)
  const cols = 12;
  const rows = 5;
  const padding = 40;
  const gx = (W - padding*2) / (cols - 1);
  const gy = (H - padding*2) / (rows - 1);

  const nodes = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = padding + c*gx + (Math.sin(r*13.37 + c*0.7)*5);
      const y = padding + r*gy + (Math.cos(c*9.73 + r*0.3)*5);
      nodes.push({ x, y, alive: true, name: null, alpha: 1 });
    }
  }

  // Tag a few filenames along the top row, protect "ingest.py"
  const top = nodes.filter((_, i) => i < cols);
  const labels = ["README.md","notes.txt","build.sh","data.csv","logs/","temp/","venv/","module.py","main.py","viz.ipynb","ingest.py","old/"];
  top.forEach((n, i) => n.name = labels[i] || null);

  // Edges (connect to next row in a tree-ish fan)
  const edges = [];
  for (let r = 0; r < rows-1; r++) {
    for (let c = 0; c < cols; c++) {
      const i = r*cols + c;
      const downLeft = (r+1)*cols + Math.max(0, c-1);
      const down = (r+1)*cols + c;
      const downRight = (r+1)*cols + Math.min(cols-1, c+1);
      edges.push([i, down]);
      if (Math.random() < 0.5) edges.push([i, downLeft]);
      if (Math.random() < 0.5) edges.push([i, downRight]);
    }
  }

  // Path: simple zig-zag through columns to mimic find's traversal
  const path = [];
  for (let r = 0; r < rows; r++) {
    if (r % 2 === 0) {
      for (let c = 0; c < cols; c++) path.push(r*cols + c);
    } else {
      for (let c = cols-1; c >= 0; c--) path.push(r*cols + c);
    }
  }

  let t = 0;
  let playing = true;

  function reset() {
    t = 0;
    nodes.forEach(n => { n.alive = true; n.alpha = 1; });
    playing = true;
  }

  function pruneCandidate(n) {
    // emulate: ! -name ingest.py
    return (n.name !== "ingest.py");
  }

  function step() {
    if (!playing) return;
    t += 0.015; // speed
  }

  function render() {
    ctx.clearRect(0,0,W,H);

    // Background slight vignette
    const g = ctx.createLinearGradient(0,0,0,H);
    g.addColorStop(0, "#0b0d10");
    g.addColorStop(1, "#0e1116");
    ctx.fillStyle = g;
    ctx.fillRect(0,0,W,H);

    // Draw edges
    ctx.lineWidth = 1.2;
    ctx.globalAlpha = 0.4;
    ctx.strokeStyle = "#8aa1b1";
    edges.forEach(([a,b]) => {
      const A = nodes[a], B = nodes[b];
      ctx.beginPath();
      ctx.moveTo(A.x, A.y);
      ctx.lineTo(B.x, B.y);
      ctx.stroke();
    });
    ctx.globalAlpha = 1;

    // Prune logic tied to traversal index
    const idx = Math.min(Math.floor(t * path.length), path.length-1);
    for (let i=0; i<idx; i++) {
      const n = nodes[path[i]];
      if (pruneCandidate(n)) {
        n.alpha = Math.max(0.08, n.alpha * 0.985);
        if (n.alpha < 0.12) n.alive = false;
      }
    }

    // Draw nodes
    nodes.forEach(n => {
      ctx.globalAlpha = n.alpha;
      ctx.beginPath();
      ctx.arc(n.x, n.y, 4, 0, Math.PI*2);
      ctx.fillStyle = n.name === "ingest.py" ? "#6ee7b7" : "#cbd5e1";
      ctx.fill();
      if (n.name) {
        ctx.font = "12px ui-monospace, SFMono-Regular, Menlo, monospace";
        ctx.fillStyle = n.name === "ingest.py" ? "#6ee7b7" : "#9aa7b4";
        ctx.fillText(n.name, n.x + 8, n.y - 8);
      }
    });
    ctx.globalAlpha = 1;

    // Crawler
    const cur = nodes[path[idx]];
    const prev = nodes[path[Math.max(0, idx-1)]];
    const dx = cur.x - prev.x;
    const dy = cur.y - prev.y;
    const angle = Math.atan2(dy, dx);

    // tail
    ctx.save();
    ctx.translate(cur.x, cur.y);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(-14, -3);
    ctx.quadraticCurveTo(-6, -1, 0, 0);
    ctx.quadraticCurveTo(-6, 1, -14, 3);
    ctx.fillStyle = "#94a3b8";
    ctx.globalAlpha = 0.6;
    ctx.fill();
    ctx.restore();

    // head
    ctx.beginPath();
    ctx.arc(cur.x, cur.y, 6, 0, Math.PI*2);
    ctx.fillStyle = "#e2e8f0";
    ctx.fill();

    // eye
    ctx.beginPath();
    ctx.arc(cur.x + Math.cos(angle)*3, cur.y + Math.sin(angle)*3, 1.5, 0, Math.PI*2);
    ctx.fillStyle = "#0b0d10";
    ctx.fill();

    // halo if protected file is near
    if (cur.name === "ingest.py") {
      ctx.beginPath();
      ctx.arc(cur.x, cur.y, 12, 0, Math.PI*2);
      ctx.strokeStyle = "#6ee7b7";
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.7;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }

  function loop() {
    step();
    render();
    requestAnimationFrame(loop);
  }

  // Controls
  document.getElementById('restart').addEventListener('click', reset);
  document.getElementById('pause').addEventListener('click', () => playing = false);
  document.getElementById('play').addEventListener('click', () => playing = true);

  // Click the canvas to restart
  canvas.addEventListener('click', reset);

  reset();
  loop();
})();
</script>

</body>
</html>
"""

style_css = """
* { box-sizing: border-box; }
:root {
  --bg: #0b0d10;
  --bg-2: #0e1116;
  --text: #e5e7eb;
  --muted: #9aa7b4;
  --card: #12161c;
  --accent: #6ee7b7;
  --ring: #334155;
}
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
a { color: inherit; text-decoration: none; }
.site-header {
  position: sticky; top: 0; z-index: 20;
  display:flex; align-items:center; justify-content:space-between;
  padding: 14px 20px; background: linear-gradient(180deg,var(--bg),rgba(11,13,16,0.6));
  border-bottom: 1px solid #11151b;
  backdrop-filter: blur(6px);
}
.brand { font-weight: 700; letter-spacing: 0.02em; }
.nav a { margin-left: 14px; color: var(--muted); }
.nav a:hover { color: var(--text); }

.hero {
  position: relative;
  max-width: 1200px;
  margin: 26px auto 8px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35), 0 0 0 1px var(--ring) inset;
}
#crawl { display:block; width: 100%; height: auto; background: linear-gradient(180deg,var(--bg),var(--bg-2)); }
.hero-controls {
  position:absolute; inset:auto 12px 12px auto; display:flex; gap:8px; align-items:center;
  background: rgba(10,12,16,0.6); padding: 8px 10px; border-radius: 12px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.35);
}
.hero-controls button {
  appearance:none; border: 1px solid var(--ring); background: #12161c; color: var(--text);
  padding: 6px 10px; border-radius: 10px; cursor:pointer; font-size: 13px;
}
.hero-controls button:hover { border-color: #475569; }
.hero-controls .cmd {
  margin-left: 8px; padding-left: 10px; border-left: 1px dotted #2b323c; color: var(--muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px;
}
.grid {
  max-width: 1200px; margin: 20px auto; padding: 0 14px;
  display:grid; grid-template-columns: repeat(auto-fit,minmax(240px,1fr)); gap: 14px;
}
.card {
  background: var(--card); padding: 16px; border-radius: 16px; border: 1px solid var(--ring);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.card:hover { transform: translateY(-2px); border-color: #475569; box-shadow: 0 8px 26px rgba(0,0,0,0.3); }
.card h3 { margin: 0 0 6px; font-size: 18px; }
.card p { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.4; }

.legend {
  max-width: 1200px; margin: 14px auto 40px; padding: 0 14px;
}
.legend h2 { font-size: 16px; font-weight: 600; color: var(--muted); margin-bottom: 8px; }
.legend ol { margin: 0; padding-left: 18px; color: var(--muted); }
.legend li { padding: 2px 0; }
.site-footer { border-top: 1px solid #11151b; padding: 18px 14px; text-align: center; color: var(--muted); }
"""

# Write files
(root / "index.html").write_text(index_html, encoding="utf-8")
(assets / "style.css").write_text(style_css, encoding="utf-8")

# Zip it
zip_path = "/mnt/data/ont-landing.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for p in [root / "index.html", assets / "style.css"]:
        z.write(p, arcname=str(p.relative_to(root)))

zip_path

