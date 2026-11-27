# Workspace development rules

- This root is a GitHub-backed sparse working copy of `huuson889/Workspace`.
- Read `GITHUB-WORKSPACE.md` before modifying checkout layout or packaging.
- Application rules remain in `Keepit-OCR/AGENTS.md`; read `Keepit-OCR/manifest.json` for the current application version.
- Missing `Keepit-OCR/vendor/` and `Keep-it/` are intentional local omissions, NOT remote deletions.
- Run `python tools/workspace.py hydrate ocr-assets` before extension tests/packaging. Thin source alone is not runnable.
- To consult the original source, run `python tools/workspace.py hydrate original`; evict only after verifying no changes.
- Never replace local OCR model/runtime paths with GitHub URLs: delivered extensions must remain offline-capable.
- Never stage sparse omissions as deletions or force-push. If cache metadata disappeared, run `python tools/workspace.py bootstrap`, inspect status and hydrate as needed.
- Save changes to GitHub before relying on cache eviction. `~/.cache` is transient, not a backup.
- Private SSH keys remain outside Workspace, never in commits, ZIPs, logs or chat. SSH deploy keys do not grant GitHub Releases API access.
- Keep app-specific historical source restrictions and user instructions unchanged. Repository storage work does not authorize app redesign or engine changes.
- OCR responsive demos must follow the current Documents viewer responsive shell and retain Keepit's actual control designs/renderers on every screen; adapt dimensions and scrolling only. The page-list sheet is explicitly approved. Language selection must use the app's stacked `kpick` list, native/translated names, checkboxes and search behavior, never custom chips.
- OCR demo portrait sheets must sit flush left/right/bottom and share Keepit's glass tokens, sheet motion and `LHN_SHEET` gestures through one presentation adapter, not per-sheet lookalikes. Page-number pickers must reuse the actual Keepit list component (`LHN_ICONS.createFlowSelect`), with only responsive sizing/scroll-boundary adaptations. Standalone demos embed these authentic sources inline for offline use; later app integration must reference the shared modules.

- User packaging rule: always commit and push ZIP deliverables to the matching GitHub folder `<source-folder>-Zip` on `main` (e.g. `Keepit-OCR/` → `Keepit-OCR-Zip/`). Cache-only links and GitHub Releases are not substitutes. Preserve versioned names; never overwrite an existing ZIP.
- ZIP folders are omitted by the default thin checkout. Stage newly produced packages explicitly with `git add --sparse Keepit-OCR-Zip/<filename>`, commit and push; verify the remote blob before any local eviction. Do not regenerate deleted older ZIPs.
