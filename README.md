# pdf2xml — step‑by‑step PDF → XML scaffold

> Parse academic PDFs into a pragmatic JATS‑like XML.  
> This repo is being built **incrementally** with tests at each step.

Right now we have a **working CLI**, a **config loader**, a **minimal XML builder/validator**, and a **reader abstraction** with:
- `DummyReader` (safe fallback) — derives a title from the filename.
- `PyMuPDFReader` — pulls **title**, the **Abstract** block, and a **list of authors** from the first page(s).

We also added a small text normalizer to fix common PDF artifacts (hyphenations like `dif- ferent`, ligatures, and mojibake like `128Ã×128` → `128×128`).

---

## Quick start (Windows / PowerShell)

```powershell
# 0) Open a terminal in the repo folder
Set-Location C:\Users\YOURNAME\Desktop\pdf2xml

# 1) Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install the package in editable mode + test tools
python -m pip install -U pip
pip install -e .
pip install pytest

# 3) (Recommended) enable real text extraction
pip install PyMuPDF

# 4) Sanity check the CLI
pdf2xml --help
```

---

## Usage

### Pick a reader in the config

`examples/minimal_config.yaml`:
```yaml
# Use 'pymupdf' for real parsing if PyMuPDF is installed;
# or 'dummy' to use a filename-only fallback.
reader: pymupdf
enable_ocr: false
table_extractor: camelot
page_ranges: "all"
detect_columns: true
strip_headers_footers: true
normalize_affiliations: true
reference_style: "auto"
emit_base64_figures: false
emit_tables_as_html: true
timeout_sec: 120
```

### Convert and validate

```powershell
# Convert a PDF → XML
pdf2xml convert .\tests\data\sample1.pdf -o .\out.xml -c .\examples\minimal_config.yaml

# Validate the generated XML
pdf2xml validate .\out.xml
```

To test with a real paper:
```powershell
# Put your paper in tests\data\
Copy-Item "C:\path\to\GAN-based_synthetic_brain_MR_image_generation.pdf" .\tests\data\

# Convert using the PyMuPDF reader
pdf2xml convert .\tests\data\GAN-based_synthetic_brain_MR_image_generation.pdf -o .\gan.xml -c .\examples\minimal_config.yaml
pdf2xml validate .\gan.xml
```

---

## What it extracts **today**

- **Title** (heuristic from the first page).
- **Abstract** block text (lines after “Abstract” until the next heading/section hint).
- **Authors** (multiple) emitted as:
  ```xml
  <contrib-group>
    <contrib><name><given-names>First</given-names><surname>Last</surname></name></contrib>
    ...
  </contrib-group>
  ```
- **Text normalization**: de‑hyphenation across line breaks; common ligatures; `Ã×` → `×`; whitespace collapse.
- **XML skeleton**: `<article><front>…</front><body>…</body><back>…</back></article>`
- **CLI**: `convert`, `validate`, `preview` (stub).
- **Validator**: checks basic structure.

> Note: The abstract currently appears as a `<body><p>…</p></body>` paragraph. We’ll promote it to a proper `<abstract>` block in the next milestone.

---

## What’s **not** implemented yet

- Section splitting (Introduction, Methods, Results, …).
- Reference parsing / `<ref-list>` population.
- Figure and table extraction.
- Affiliations, author roles, ORCIDs, correspondence.
- Robust header/footer removal, column detection, page‑range selection.
- OCR fallback for scanned PDFs.

These are on the roadmap (see below).

---

## Project layout

```
pdf2xml/
├─ pyproject.toml
├─ examples/
│  └─ minimal_config.yaml
├─ src/
│  └─ pdf2xml/
│     ├─ __init__.py
│     ├─ cli.py                # CLI entrypoints
│     ├─ config.py             # YAML/JSON/KV config loader
│     ├─ pipeline.py           # reader → XML → validate
│     ├─ utils/
│     │  ├─ log.py
│     │  └─ text.py            # normalization helpers (hyphens, ligatures, mojibake)
│     ├─ pdf_reader/
│     │  ├─ base.py            # DocMeta + protocol
│     │  ├─ dummy_reader.py    # filename‑only fallback
│     │  └─ pymupdf_reader.py  # real text extraction (PyMuPDF)
│     └─ xml/
│        ├─ build.py           # XML writer (supports multiple authors)
│        └─ validate.py        # basic structural checks
└─ tests/
   ├─ data/
   │  └─ sample1.pdf
   ├─ test_step1_smoke.py
   └─ test_step2_reader.py
```

---

## Development

### Run tests
```powershell
pytest -q
```

### Where to tweak things
- **Reader logic**: `src/pdf2xml/pdf_reader/pymupdf_reader.py`
  - Title heuristic, Abstract window, and author block splitting.
- **Text normalization**: `src/pdf2xml/utils/text.py`
  - Add more ligature/mojibake mappings if needed.
- **XML structure**: `src/pdf2xml/xml/build.py`
  - We currently emit a minimal JATS‑ish skeleton; will grow with sections, refs, etc.

### Common troubleshooting

- **CLI says “Using DummyReader” when you expected PyMuPDF**  
  - Ensure `reader: pymupdf` in the YAML you pass with `-c`.
  - Ensure `src/pdf2xml/pdf_reader/pymupdf_reader.py` exists in your checkout.
  - `pip install -e .` again (editable install must pick up new files).
  - `pip show PyMuPDF` inside the same virtualenv.

- **Weird characters like `128Ã×128` in console**  
  - The file is UTF‑8; PowerShell sometimes shows mojibake. Open the XML in VS Code, or in PowerShell:
    ```powershell
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Get-Content .\gan.xml -TotalCount 40
    ```

- **“@' … | Set‑Content …” text appears inside files**  
  - Those are PowerShell here‑string markers. They should be run in the terminal, **not** pasted into the file editor. Remove the first line `@'` and the last line with `Set‑Content` from any affected file.

---

## Roadmap (near‑term)

1. **Promote Abstract** to `<abstract>` (front‑matter), and keep a clean `<body>` for sections.  
2. **Section detection** (Introduction/Methods/Results/Discussion/Conclusion) with simple heading rules; emit `<sec>` blocks.  
3. **More robust authors/affiliations** (split roles, strip emails/superscripts reliably, capture affiliations).  
4. **References**: detect a References section and emit minimal `<ref-list>` entries.  
5. **Figures/Tables**: detect captions and stub out `<fig>`/`<table-wrap>` nodes.  
6. **CI**: add GitHub Actions to run tests on push (no external PDF engines required).

---

## License
TBD

---

## Acknowledgements
Built incrementally with a focus on **testable steps** and **clear fallbacks** so you can evolve the pipeline safely.
