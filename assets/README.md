You’re not seeing any Python because **GitHub Pages is static**. It will happily serve your `index.html`, CSS, images, and GIFs—but it will **not run** `assets/eden.py` (or any `.py`) on the server. Browsers also don’t execute `.py` files by default. So unless you do extra setup, Python won’t “run” when you open the page.

You’ve got three clean options:

# 1) Keep it static (simple + reliable)

Run your Python **locally** to generate the assets (like `devil_crawls.gif`), then just reference them in HTML.

```bash
# from repo root
python3 assets/eden.py   # (re)generates assets/devil_crawls.gif, etc.
git add assets/*.gif
git commit -m "build: update animation assets"
git push
```

Your page then uses `<img src="assets/devil_crawls.gif">` or the `<canvas>` version I gave you. No Python needed at runtime.

# 2) Run Python **in the browser** (PyScript / Pyodide)

If you really want Python to execute on the client (no server), embed PyScript. It loads a Python runtime (WebAssembly) in the browser:

```html
<!-- in <head> -->
<link rel="stylesheet" href="https://pyscript.net/releases/2024.5.1/core.css">
<script type="module" src="https://pyscript.net/releases/2024.5.1/core.js"></script>

<!-- optional: request pure-Python packages only (WASM wheels are heavy) -->
<py-config>
packages = []
</py-config>

<!-- run inline Python -->
<py-script>
print("Hello from Python in your browser!")
</py-script>

<!-- or load your file (must be pure-Python, no native deps) -->
<py-script src="assets/eden.py"></py-script>
```

Caveats:

* First page load is heavier (it downloads a Python runtime).
* Libraries with native extensions (e.g., Pillow, imageio’s native codecs) may not work or will be huge/slow. Pure-Python is best.

If your `eden.py` uses heavy libs to *generate* the GIF, better to prebuild the GIF (option 1) or…

# 3) Build with **CI** (GitHub Actions) and publish the result

Have GitHub **run Python on push**, commit the generated files, and serve them statically via Pages. Add this workflow:

```
# .github/workflows/build-assets.yml
name: Build assets
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt || true
      - run: python assets/eden.py
      - name: Commit updated assets
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add assets/
          git commit -m "chore(ci): rebuild assets" || echo "no changes"
          git push
```

This way, your Python runs in CI, produces `assets/devil_crawls.gif`, and Pages still serves it statically.

---

Want me to:

* strip `eden.py` to pure-Python so it runs via PyScript?
* wire the GitHub Action for you?
* or just keep it static and I’ll add a tiny npm-free build script you can run locally?

Your call.

