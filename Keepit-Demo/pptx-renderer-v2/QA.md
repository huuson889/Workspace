# Demo v2 — QA scope

Tested in Chromium on 2026-11-26. This is standalone-demo functional QA, not extension acceptance and not a PowerPoint-fidelity certification.

## Passing run

`qa/report.json`: **22 test groups**, no false assertions, no captured JavaScript errors/unhandled rejections. The run:

- Loaded the actual user PPTX through a file-input `change` event and recognized 92 slides in presentation order.
- Traversed all 92 slide indices and checked current index, SVG content and absence of literal `NaN` markup. This does **not** mean each slide visually matches PowerPoint.
- Checked numeric page selection, previous/next controls, optional local PDF page 13 rendering, and split comparison mode.
- Opened an independently generated two-slide PPTX, checking its own text, raster picture, theme-style ellipse and second-slide text, with no old PDF reference. This catches fixture-only behavior.
- Rejected an invalid ZIP and retained the existing deck.
- Checked body overflow/control presence at widths 1512, 900 and 390, both light/dark, fit/150% zoom (12 combinations).
- Checked return to the single embedded sample with its sample-only reference.

First run found missing theme `fillRef` fallback on the independent ellipse. The renderer was fixed and the complete second run passed; the persisted report is that second run.

## Additional manual browser actions

- Used browser file upload on the revealed real file input for `independent.pptx`; snapshot confirmed `independent.pptx · 2 slide`, selectable `CUSTOM DECK 1`, correct paging and cleared old PDF.
- Visually reviewed standalone desktop sample and narrow/light layout. Full arbitrary-deck pixel-fidelity review was **not** performed.
- Opened the delivered HTML directly with `file:///home/user/keepit-pptx-demo-v2.html`; sample and controls initialized. Arbitrary-file input was tested through HTTP, not repeated under `file://`.
- Native OS picker dialog itself was not exercised. The upload tool and automated tests populated the actual browser file input; they did not just invoke a fixture renderer.
- `node --check` passed for renderer/controller; Python build scripts compiled. Rebuild output is byte-identical to the browser-tested runtime (later template edits only clarified sample hash and embedded license text).

The automated harness and independent test deck are retained separately under `/home/user/qa-pptx-demo-v2/` for this workspace. The harness originally expects the user's cached original PPTX/PDF and the local QA report receiver; it is not a portable product file.

## Source documents

User-provided GitHub `Uploads` documents, 92 slides/pages:

- PPTX: 17,134,774 bytes; SHA256 `f32b0795b7c03adcdd7731ac9bb36e717c1f2a0737d57f7bfa318231ee88d88b`.
- PDF: 5,653,384 bytes; SHA256 `3917ea734a6ae9c1a6315c72f8023d94903160d3624d4f0ae586b3f2b9829b9e`.

Neither full document is bundled with v2; only the explicitly labeled slide-1 sample inherited from v1 is embedded. The full originals remain in the user's GitHub Uploads.

## Known unverified areas

Other browsers, native OS picker, the complete arbitrary-file flow under `file://`, encrypted inputs, every PPTX feature, large/hostile ZIP resource exhaustion, all PDF font/image codecs, and selection-based extension actions. No production extension files or version changed. See README for implementation limits.
