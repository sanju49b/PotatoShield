# How to Convert Technical Document to PDF

The technical document `TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md` has been created. Here are several ways to convert it to PDF:

## Option 1: Online Converter (Easiest - Recommended)

1. **Markdown to PDF** (https://www.markdowntopdf.com/):
   - Go to https://www.markdowntopdf.com/
   - Upload `TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md`
   - Click "Convert" and download the PDF

2. **Dillinger** (https://dillinger.io/):
   - Go to https://dillinger.io/
   - Copy and paste the markdown content
   - Click "Export as" → "PDF"

3. **Pandoc Try** (https://pandoc.org/try/):
   - Go to https://pandoc.org/try/
   - Paste the markdown content
   - Select output format: PDF
   - Download

## Option 2: Install Python Libraries

### Using WeasyPrint (Recommended - Better Formatting)

```bash
pip install weasyprint markdown
python convert_to_pdf.py
```

### Using pdfkit (Requires wkhtmltopdf)

1. Install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
2. Install Python libraries:
   ```bash
   pip install pdfkit markdown
   ```
3. Run:
   ```bash
   python convert_to_pdf.py
   ```

## Option 3: Using Pandoc (Command Line)

If you have Pandoc installed:

```bash
pandoc TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md -o TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.pdf --pdf-engine=xelatex
```

Or with basic PDF engine:

```bash
pandoc TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md -o TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.pdf
```

## Option 4: Using VS Code Extension

1. Install "Markdown PDF" extension in VS Code
2. Open `TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md`
3. Right-click → "Markdown PDF: Export (pdf)"

## Option 5: Manual Conversion

1. Open the markdown file in a markdown viewer (VS Code, Typora, etc.)
2. Use "Print to PDF" feature
3. Save as PDF

---

## Document Details

- **File**: `TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md`
- **Pages**: Approximately 6-8 pages when converted to PDF
- **Content**: Full technical methodology for peer review
- **Target Audience**: Agricultural professionals, plant pathologists, researchers

The document includes:
- Disease Triangle conceptual framework
- Environmental threshold derivations
- Infection periods and cumulative indices
- Expert rules + AI integration
- Mathematical equations and models
- Theoretical foundations (Smith Period, Hutton Criteria, Dew Formation)
- Validation framework
- Implementation details

