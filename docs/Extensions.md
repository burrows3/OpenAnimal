# Using Cursor Extensions with OpenAnimal

Your installed extensions and how they make this project better.

---

## Design & frontend

### **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)

- **Use:** This project uses plain CSS in `web/styles.css`. If you add Tailwind later (e.g. via CDN or a build step), you’ll get class-name autocomplete and preview.
- **Quick win:** Add Tailwind via CDN in `web/index.html` for prototyping and the extension will help with utility classes in HTML.

### **CSS Peek** (`pranaygp.vscode-css-peek`)

- **Use:** **Ctrl+Click** (or Cmd+Click) any class name in `web/index.html` or `web/app.js` (e.g. `gallery-card`, `feed-post-avatar`) to jump to its definition in `web/styles.css`.
- **Go to definition:** Right-click a class → “Go to Definition”.

### **SVG** (`jock.svg`)

- **Use:** Open any `.svg` file in the project for preview and editing. Add SVG assets under `web/` (e.g. `web/logo.svg`, animal icons) and edit them with live preview.
- **Idea:** Replace or complement emoji animals with custom SVGs in `web/assets/`.

### **Prettier** (`esbenp.prettier-vscode`)

- **Use:** With the workspace settings in `.vscode/settings.json`, HTML, CSS, and JS in `web/` format on save. Keeps style consistent and diffs clean.
- **Config:** `.prettierrc` in the project root.

### **Live Server** (`ms-vscode.live-server`)

- **Use:** For **CSS/HTML-only** tweaks: right-click `web/index.html` → “Open with Live Server” for instant refresh. The OpenAnimal **API will not run** (no birth, no feed); use `python -m openanimal.webapp` when you need the full app.
- **Workflow:** Run the Python webapp for real use; use Live Server for quick layout/visual experiments.

---

## Icons & UI

### **Material Icon Theme** (`pkief.material-icon-theme`)

- **Use:** File and folder icons in the sidebar (e.g. `web/`, `openanimal/`, `.py` files). No config needed; enable from the theme picker if not already active.

### **File Icon Theme** (`vivekkumarmaddeshiya25.file-icon-theme`)

- **Use:** Alternative file icons. Pick either this or Material Icon Theme in the theme selector.

---

## Python backend

### **Python** (`ms-python.python`)

- **Use:** Run and debug the backend. Select the Python interpreter (e.g. the one with `openanimal` installed). Run `webapp` from the Run panel or terminal.

### **Debugpy** (`ms-python.debugpy`)

- **Use:** Set breakpoints in `openanimal/*.py` (e.g. `webapp.py`, `agent.py`, `expression.py`) and debug the server or simulator. Use “Python: Current File” or a launch config.

### **Cursor Pyright** (`anysphere.cursorpyright`)

- **Use:** Type checking for `openanimal/`. Fix type hints and get better Cursor AI suggestions. Add `pyrightconfig.json` in the project root if you want stricter options.

---

## Optional: CodeSwing (`codespaces-contrib.codeswing`)

- **Use:** In-editor HTML/CSS/JS preview and tutorials. You can open a Swing on the `web/` folder to prototype UI snippets; the preview won’t call the OpenAnimal API, so use for layout and styling only.

---

## Summary

| Extension      | Best for OpenAnimal                          |
| -------------- | -------------------------------------------- |
| CSS Peek       | Jump from HTML/JS class names to CSS         |
| Prettier       | Consistent formatting in `web/`              |
| Live Server    | Fast visual feedback for static HTML/CSS/JS  |
| SVG            | Add and edit SVG assets (e.g. logo, icons)   |
| Python/Debugpy | Run and debug `openanimal.webapp` and agents |
| Tailwind       | Useful when/if you introduce Tailwind        |
