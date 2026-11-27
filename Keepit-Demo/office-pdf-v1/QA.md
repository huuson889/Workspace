# Office → PDF v1 · QA

Test date: 2026-11-26 (conversation local date). Linux, LibreOffice 25.2.3.2, Chromium. Standalone-demo QA only; Keepit-OCR production version remains 3.5.629.

## Results

### API / preflight / real conversion: 21 checks passed

See `tests/results/api-report.json`; reproduced with:

```sh
python -m pip install pymupdf  # test dependency only
python tests/check_api.py --base http://localhost:8120 --output /path/to/api-report.json
# Optional authorized original deck:
python tests/check_api.py --base http://localhost:8120 --deck /path/to/file.pptx --output /path/to/api-report.json
```

Checks include consent requirement, cross-origin mutation rejection, incorrect extensions, invalid ZIP, no static access to server.py, unknown job, path traversal/macro/OLE/DTD/external-image rejection, TTL sweep deletion, Internet socket denial in the launcher, real DOCX and PPTX conversion with text extraction, queued/running cancellation, deletion and idempotent delete.

Final measured run:

| Input | PDF pages | Output bytes | Engine time | Extracted text chars |
|---|---:|---:|---:|---:|
| Generated DOCX sample | 2 | See API report | About 1 second | 1,204 |
| Generated PPTX sample | 2 | See API report | About 1 second | 314 |
| User's original PPTX | **92** | **6,049,041** | **29.96 seconds** | **18,259** |

The original deck had extractable text on **87 of 92 PDF pages**. Other pages can be graphics-only/empty; this is not OCR and does not imply every page has selectable content. All 92 output pages were parsed successfully by PyMuPDF. This is a conversion/count/text check, **not** a visual-fidelity score.

Original PPTX source SHA256: `f32b0795b7c03adcdd7731ac9bb36e717c1f2a0737d57f7bfa318231ee88d88b`. The separately supplied original PDF was **not** returned as conversion output. Neither original nor its converted PDF is included in this source/ZIP. Derived output is retained only in the workspace QA folder for inspection, outside the product source.

### Browser: 18 groups passed, no captured JS errors

Run `/qa.html` and press **Run generated sample tests**. It uses only generated sample documents. Summary recorded from the final browser DOM report: `tests/results/browser-summary.json`.

- Choosing a sample alone does not upload; dialog appears before upload; cancel dialog sends nothing.
- DOCX → real two-page PDF; PDF text layer covers the canvas and actual text spans have non-zero bounds.
- Next/numeric page navigation, 150% zoom/internal scroll and rotation work.
- Widths **1512 / 900 / 390**, light/dark: no document-body horizontal overflow. This matrix is a geometry check, not pixel-by-pixel mobile visual acceptance.
- PPTX → real two-page PDF with its own text on both pages.
- New conversion deletes previous server PDF; download endpoint returns `%PDF-`; delete returns 404 for the old job; UI resets.
- No captured error/unhandledrejection events.

Additional real browser actions:

- Uploaded the generated DOCX through the browser's real file input and confirmed the upload dialog.
- Visually reviewed desktop blank state, consent dialog and rendered DOCX page.
- Dragged across the rendered Vietnamese line with real mouse input. The selection status contained **“Bạn có thể kéo chọn dòng này: Tiếng Việt có dấu”**; this is not just a programmatically created Range.
- Visually inspected raster of converted original slide 1, with vector artwork and text present. No full-deck pixel comparison was performed.

Last UI edit after the full browser suite only corrected transfer-status wording (the selected file label now changes from “not sent” to “sent and converted”). No conversion/navigation logic changed in that edit.

## Issues found and fixed during development

1. Forcing LibreOffice's `gen` VCL plugin tried to access an X display despite headless mode. Switched to `svp`; sample conversions succeeded.
2. Initial tagged-PDF text layer used old markedContent layout CSS, so the text did not align for mouse selection. Changed marked-content wrappers to `display: contents`, matching the existing Keepit PDF.js text-layer approach; real selection verified afterward.
3. Converting the entire 92-slide deck at once exceeded this approximately 2 GB environment's usable RAM/time budget. Added disclosed low-memory batches of eight slides for PPTX over 12 slides, merging PDFs in presentation order. The full-deck test then passed twice in about 29–30 seconds.
4. Tested that repeated ZIP writing uses copies of ZipInfo entries; sharing mutable header offsets corrupted subsequent batch reads during an early split-helper test. Fixed before successful full-deck runs.

## Not certified / still limited

- Exact fidelity for all Office documents, every font, formula, chart and SmartArt.
- Cross-batch links, automatic page/slide fields, custom shows, sections and tagged PDF structure. See README.
- End-to-end native Keepit translation/read-aloud/notes. They are not wired into this separate viewer.
- Hardened multi-tenant security, malicious engine exploits, production authentication/rate limiting, cgroup isolation, cold installation on every Linux distro, Windows/macOS, complete PDF CMap/WASM coverage.
- Actual 30-minute wall-clock waiting was not performed; the same expiry-sweep function was tested with an expired job and its file was removed.
- SIGINT/SIGTERM cleanup is implemented; crash/SIGKILL cleanup is not guaranteed. This demo should not receive sensitive documents.

## Static / package checks

Python compilation and JavaScript syntax checks pass. ZIP is CRC-tested and member bytes are checked against the source tree. Existing extension sources, archives and Uploads are unchanged. Bundled library/font/sample hashes are in `assets.lock.json`.
