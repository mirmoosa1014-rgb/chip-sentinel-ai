# Progress and recovery

## Recovered implementation

The original Mac workspace became unavailable during the task. This directory recovers the exact transcript-authored Python modules (`engine`, `policy`, `model`, `api`, `server`, `experiment`, `visuals`), React/TypeScript/CSS workbench, original nine-test suite, package manifest, TypeScript/Vite config, Python metadata, optional pinned requirements, CI and ignore rules. Architecture, model, evaluation, explanation, demo and summary documents were recovered from retained source text. README prose was recovered and its validation paragraphs updated for Linux. No original source file bytes can be compared because the Mac filesystem is unavailable; this is transcript-based source recovery, not a claim of byte-verified restore.

## Regenerated evidence

The original package-lock bytes were not retained; the lockfile was regenerated from the same pinned package manifest. Trained model JSON, full CSV/JSON experiments, plotted figures and orbit GIF were regenerated with the recovered scripts and original seeds. The metrics reproduce the original values: fixed/random/active final candidates 4.1/3.875/2.98125; exact learned top-1 0.36875/0.45625/0.55625. Runtime naturally changes across hosts. The raw project brief was not restored because the complete attachment bytes are owned by the parent task and were not retained here; the code and README preserve implemented scope and limitations.

## Current validation

All 11 tests pass on Linux: nine recovered unit checks and two new integration checks, including exhaustive independent arithmetic comparisons. TypeScript/Vite production build and npm install pass. The default server binds loopback and serves static HTML plus simulation JSON in a real HTTP smoke test. FastAPI TestClient health, simulation and rejected-invalid-budget checks pass. Full Chromium launch was blocked by UNIX socket restrictions, but the bundled Chromium headless shell works. Real browser checks pass for initial rendering, next vector, fault reveal, 3D dragging, JSON download and mobile layout. Desktop/mobile screenshots were captured to temporary verification files and visually inspected; no clipping or horizontal overflow was found. CI has not run remotely. No commits, repositories, or pushes were made; publication awaits user confirmation.

## Scope limits

The app diagnoses combinational ALU bus faults. The separate register primitive is tested but not part of sequential diagnosis. ML ranks candidates and does not drive active test selection. The 48-vector equivalence classes are pool-relative. Physical chip validation, noisy observations, timing faults, per-bit and multi-fault episodes, calibrated probabilities, and real-world deployment are not implemented.

New verification after recovery: `tests/test_integration.py` adds real loopback HTTP and optional FastAPI integration tests; scientific implementation and fixed seeds remain unchanged.

Final browser verification used the bundled Chromium headless shell in the same network namespace as the live Python server. No source changes were needed after browser verification.

## Editorial Swiss redesign

Replaced the generic dark card dashboard with a warm-paper ruled diagnostic bench, setup/readout rail, actual 3D circuit schematic, candidate register and evidence ledger. Exact upstream exported CSS tokens and finite entrance motion are imported; MIT attribution is in THIRD_PARTY_NOTICES.md and docs/design.md. Backend, model, and numeric datasets were frozen and are unchanged. Only the figure generator palette and image/GIF render assets changed. Production build passes. Current Mac Chrome aborts SIGABRT at launch under the execution sandbox, so redesigned desktop/mobile/reduced-motion screenshots remain pending; old screenshot files are historical only.

Added a pinned Playwright Linux browser verification script/workflow for main, design/**, pull requests and manual dispatch. It captures four authentic viewport/motion screenshots, checks controls and live evidence, and uploads read-only CI artifacts; first hosted execution remains pending. No experiments or model training are invoked by the browser workflow.
