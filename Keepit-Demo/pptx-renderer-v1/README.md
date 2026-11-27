# Keepit PPTX renderer demo v1

**Standalone experiment only. Keepit-OCR remains unchanged at 3.5.629.**

Open `keepit-pptx-demo-v1.html` in a current browser. It is a single self-contained file: no server, installation or network access is required. The bundled XML, font subset and reference PNG are inline. A downloaded HTML file is sufficient; the other files are build sources.

## What to try

- **PPTX dựng mới**: live rendering of supplied slide 1 XML, not a PDF screenshot.
- **PDF đối chiếu**: raster reference from page 1 of the user-provided PDF.
- **Chồng lớp**: blend PDF over the PPTX rendering; adjust the slider.
- **Đặt cạnh nhau**: PPTX left / PDF right.
- Drag to select `ENGLISH VOCABULARY` or `Workshop` in the PPTX view. PDF reference is intentionally an image, not a text layer.
- Test zoom, object bounds and light/dark UI. Theme never recolors the slide.

## Real input and construction

Source files provided by the user in `huuson889/Workspace/Uploads`, both 92 slides/pages:

- `English Vocabulary Workshop XL by Slidesgo.pptx`: SHA256 `f32b0795b7c03adcdd7731ac9bb36e717c1f2a0737d57f7bfa318231ee88d88b`.
- `English Vocabulary Workshop XL by Slidesgo.pdf`: SHA256 `3917ea734a6ae9c1a6315c72f8023d94903160d3624d4f0ae586b3f2b9829b9e`.

The builder follows slide1 → slideLayout1 → slideMaster1 → **theme4**, rather than choosing theme1. The HTML embeds these four XML parts and the renderer uses DOMParser at runtime. Custom M/L/C/Q/Z paths, source group transforms and rotation/flip, explicit fill/stroke, color-map/theme/alpha/tint, layout decoration and placeholder text inheritance are processed. Coordinates and curve control points are read from PPTX; none come from PDF. Statistics:76 custom shapes (70 slide +6 layout),76 paths,1838 cubic segments,8 groups,2 selectable XHTML text boxes. Text lives in SVG foreignObject, not raster artwork.

The original deck contains compressed EOT fonts; this proof of concept does **not** implement EOT decompression. Pangolin is a subset of the OFL Google Fonts release, embedded locally as WOFF. Synthetic bold is used where the source requests bold. See `assets/OFL.txt` for the full license and original copyright. Source: https://raw.githubusercontent.com/google/fonts/main/ofl/pangolin/Pangolin-Regular.ttf . Font version/metrics can differ from Office's embedded font.

The PDF reference PNG is rasterized at2× with PyMuPDF during build. It is separate from the XML-derived render and provides no geometry/text measurements to it.

## Scope and honest limits

Only this first slide is demonstrated. No general upload picker, full92-slide navigation, animation, SmartArt, charts, arbitrary preset geometry/formula evaluation, complete typography or full file-security pipeline is claimed. This is not integrated into the extension and is not a pixel-perfect Office compatibility promise. Do not replace the app's existing renderer with this standalone script without adapting its sanitizer, limits, annotation, OCR and text-selection contracts.

The browser smoke/geometry matrix exercised1512/900/390 CSS-pixel iframe widths,2 themes,4 viewing modes (24 cases),3 zoom settings,blend,object bounds and source/render checks (31 groups total). A trusted mouse drag selected `ENGLISH`. Graphics-only browser-canvas comparison to PDF at960×540, excluding the two text boxes, had mean maximum per-channel error1.247/255 and99.077% pixels within20/255. This is a diagnostic on this page, not an overall accuracy score or typography acceptance. Side-by-side output visually checked in browser. Physical phone, other slides, unpacked extension, other browser engines and accessibility assistive technologies are not tested.

## Build

Python dependencies: lxml, pymupdf. `renderer.js` is embedded by `build.py`.

```sh
python build.py --assets /path/containing/the/two/original/files --output keepit-pptx-demo-v1.html
```

Font/license inputs are included under assets as fallbacks. The original PPTX and PDF are not duplicated in this demo package. The subset WOFF was generated with fontTools from the source above; it includes the English alphabet/digits/punctuation needed here.

Content/design of the original slide belongs to its respective owners; this demonstration is for comparison of the user-provided document, not a new rights grant over that artwork.
