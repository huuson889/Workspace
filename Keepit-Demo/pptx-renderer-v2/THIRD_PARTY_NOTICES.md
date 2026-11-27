# Third-party notices

The standalone HTML embeds all runtime modules and their license texts. It does not fetch document data or these dependencies from a CDN.

## Office bundle

`office.mjs` is the existing Keepit-OCR vendor bundle pinned in `dependencies.json`. This demo imports **JSZip** only; the unchanged bundle also contains docx-preview, DOMPurify, and pptx-to-html. Their inclusion does not mean this experiment uses the old pptx-to-html rendering engine.

Preserved upstream licenses:
- JSZip: `licenses/LICENSE-jszip.txt` (dual MIT/GPLv3 text as supplied upstream).
- docx-preview: `licenses/LICENSE-docx-preview.txt`.
- DOMPurify: `licenses/LICENSE-dompurify.txt`.
- pptx-to-html: `licenses/LICENSE-pptx-to-html.txt`.

## PDF.js

`pdf.mjs` and `pdf.worker.mjs`: existing Keepit-OCR vendor modules, exact hashes and immutable source paths in `dependencies.json`. Apache License 2.0 text: `licenses/LICENSE-pdfjs.txt`.

No additional CMap, standard-font or WASM distribution is included. Certain PDFs may render incompletely.

## Pangolin font

Pangolin Regular by the Pangolin project authors, SIL Open Font License 1.1. License: `assets/OFL.txt`. The embedded WOFF is a subset converted from Google Fonts Pangolin-Regular.ttf, originally retrieved from https://raw.githubusercontent.com/google/fonts/main/ofl/pangolin/Pangolin-Regular.ttf . It is a disclosed replacement for the sample's embedded compressed EOT font, not an extraction of that EOT. Other fonts in user documents may fall back to installed system fonts.

## Embedded sample

The sample is slide 1 XML/theme/layout/master and a separate PDF page raster from the user's supplied English Vocabulary Workshop XL documents, carried forward from demo v1. New user-selected files are read independently; the sample does not substitute for their contents. Source document hashes and QA scope are in `QA.md`.
