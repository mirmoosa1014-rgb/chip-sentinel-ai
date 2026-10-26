# Editorial Swiss diagnostic bench

Reference: [Motion Graphic Style Library](https://github.com/TheRollerBlader/motion-graphic-style-library), revision `ab7faf2be3e17350f5c6c7e78dfb53d1792ae9cc`, `catalog/swiss.md` and `src/motionstyle_swiss/__init__.py`. The upstream pure exporter (`src/motionstyle_core/export.py`) produced the exact CSS copied to `frontend/src/motion-theme.css`; the application imports it before its own styles and consumes its tokens. [MIT notice](../THIRD_PARTY_NOTICES.md).

## Concrete mapping

| Upstream primitive | Diagnostic application |
|---|---|
| `#F3F0E8` paper / `#F7F4EC` surface | Full workbench and circuit blocks |
| `#111111` ink / `#5E594F` secondary text | Type, rules, connections, table values |
| `#E10600` signal red | The single primary **Run next test** control |
| Helvetica Neue / Helvetica / Arial | Compact uppercase identity and working labels |
| SF Mono / system mono | Evidence bits, candidate scores, seeds and vector readouts |
| Zero radius, 1px ink rules, no shadows | Flat, contiguous bench divisions; square diagram nodes |
| `IndexMark` | `CS / 01` masthead and numbered section titles |
| `Hairline` / `wipe_x` | Finite rule entrance, 0.55s, `cubic-bezier(0.77,0,0.18,1)` |
| `tracking_settle` | Name settles from .22em to .04em, 0.7s, `cubic-bezier(0.22,1,0.36,1)` |

## Layout and behavior

The interface opens directly into a working diagnostic record. The narrow left rail holds inputs, the one red action and stable numerical readouts. A broad schematic occupies the center; the candidate register sits to its right. Below, an evidence ledger shares a ruled band with the contraction plot. This replaces the former large marketing headline, glowing mint blocks, rounded card grid and badge treatment. Metadata, vector values and candidate scores never animate or count up.

The circuit canvas still projects actual 3D coordinates generated from the API netlist. Pointer dragging rotates that geometry. Solid square outlines mark consistent fault sites; thin dashed outlines mark excluded sites, with no color-only distinction. Connections and both node labels use light-background contrast. The chart's solid/dashed black/gray lines preserve active/fixed meanings. The data and simulation are unchanged.

The responsive bench becomes a single sequence at 390px. The diagram has a local horizontal viewport to preserve label legibility; it does not widen the page. Evidence values have a local table viewport. All existing seed, family, budget, next-test, fault reveal and JSON export controls are retained. Focus outlines remain explicit.

## Adaptations for a software interface

The source catalog describes a 1920px motion explainer. Here its grid is fluid, with desktop alignment and a one-column mobile reflow. A working interface needs more than two type sizes; size hierarchy is reserved for identity, section labels and tabular values. Continuous `idle_rule` motion is intentionally omitted: all arrival motion ends, and numerical evidence remains stationary. `prefers-reduced-motion: reduce` removes every CSS animation and transition. Pointer-driven rotation remains a direct user action, never autoplay.

Saved scientific figures retain the same numeric values, units, legends and seeds while adopting paper/ink/red. Red may identify the same series across multiple scientific subplots; the one-signal-control limit applies to the app chrome. The 3D figure and real orbit GIF use the same geometry; only styling changed. The plot generator never writes model or CSV/JSON output.

## Verification

TypeScript and Vite production build pass. Generated evaluation and 3D figures were inspected after recoloring. Backend, model and numeric result hashes remain unchanged. The local HTTP server can bind loopback. Current Mac Chrome launches through Playwright then aborts with `SIGABRT` under the execution sandbox, so desktop/mobile/reduced-motion screenshots and browser interaction checks for this redesign are not yet verified. Existing `app.png` / `mobile.png` files depict the earlier UI and are not current visual evidence. The previous functional browser checks belong to that earlier implementation.


## Linux browser evidence job

`.github/workflows/browser.yml` runs on pushes to `main` and `design/**`, pull requests, or manual dispatch. It builds the production UI on Ubuntu 24.04 with Node 22 and Python 3.12, installs the lockfile-pinned Playwright 1.56.1 Chromium, starts the real dependency-free backend on an ephemeral loopback port, and verifies actual API evidence and controls. No experiment or model training command runs.

Local equivalent on a Linux host with browser installation/network access:

```bash
npm ci --prefix frontend
frontend/node_modules/.bin/playwright install --with-deps chromium
npm run build --prefix frontend
npm run verify:browser --prefix frontend
```

The browser test produces authentic `desktop.png`, `mobile.png`, `desktop-reduced-motion.png`, `mobile-reduced-motion.png`, a JSON evidence download and a verification `report.json` under `artifacts/browser/`. Normal desktop is 1440 × 1100; mobile is 390 × 844. Locale is en-US, timezone UTC, light color scheme, default family 6 / seed 31 / budget 3. Screenshots are captured only after finite entrance motion settles. Reduced-motion screenshots run after browser media emulation, and the script asserts no animations are running. Numerical readouts and evidence cells are checked against a fresh call to the actual engine API. Family, seed, keyboard budget, next-test, truth reveal, 3D orbit and JSON download are exercised; page overflow and uncaught JS errors fail the job.

GitHub uploads the report/screenshots as `chip-sentinel-browser-evidence` for seven days, including failure evidence if available. The job has read-only repository permission and never commits or pushes. Its first hosted run is pending; defining the workflow is not evidence of a successful browser run. Optional `PYTHON_BIN`, `CHIP_BROWSER_EXECUTABLE` and `CHIP_BROWSER_OUTPUT` environment variables select an existing Python/browser or a different artifact output folder without changing UI data.
