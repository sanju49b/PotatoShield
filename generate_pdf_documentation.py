#!/usr/bin/env python3
"""
Script to convert RISK_CALCULATION_METHODOLOGY.md to PDF
Requires: pip install markdown weasyprint
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import sys

def markdown_to_pdf(markdown_file: str, output_pdf: str):
    """Convert markdown file to PDF with nice styling."""
    
    # Read markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'tables', 'codehilite', 'toc']
    )
    
    # Create styled HTML document
    html_document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Potato Blight Risk Calculation Methodology</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @top-center {{
                content: "Potato Blight Risk Calculation Methodology";
                font-size: 10pt;
                color: #666;
            }}
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #555;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        
        h4 {{
            color: #666;
            margin-top: 15px;
            page-break-after: avoid;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #c7254e;
        }}
        
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            page-break-inside: avoid;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding-left: 15px;
            color: #555;
            font-style: italic;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 8px 0;
        }}
        
        .toc a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}
        
        em {{
            color: #555;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        @media print {{
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="border: none; padding: 0; margin: 0;">Potato Blight Risk Calculation Methodology</h1>
        <p style="color: #666; font-size: 14px; margin-top: 10px;">
            Comprehensive Documentation of the Predictive Algorithm<br>
            Version 2.0 (Sliding Window Implementation)<br>
            Last Updated: January 2025
        </p>
    </div>
    
    {html_content}
    
    <div style="margin-top: 50px; padding-top: 20px; border-top: 2px solid #ecf0f1; text-align: center; color: #666; font-size: 12px;">
        <p>Potato Shield - Advanced Agricultural Intelligence Platform</p>
        <p>This document describes the deterministic risk calculation methodology used in the Potato Shield predictive system.</p>
    </div>
</body>
</html>"""
    
    # Convert HTML to PDF
    try:
        HTML(string=html_document).write_pdf(
            output_pdf,
            stylesheets=[CSS(string="""
                @page {
                    size: A4;
                    margin: 2cm;
                }
            """)]
        )
        print(f"✅ Successfully created PDF: {output_pdf}")
        return True
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("\nTrying alternative method with pdfkit...")
        return False

def markdown_to_pdf_alternative(markdown_file: str, output_pdf: str):
    """Alternative method using pdfkit (requires wkhtmltopdf)."""
    try:
        import pdfkit
        
        # Read markdown and convert to HTML
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'tables', 'codehilite', 'toc']
        )
        
        # Create HTML document
        html_document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Potato Blight Risk Calculation Methodology</title>
    <style>
        body {{ font-family: Georgia, serif; line-height: 1.6; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #95a5a6; padding-bottom: 8px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background-color: #3498db; color: white; padding: 12px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 10px; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        code {{ background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background-color: #f8f8f8; border: 1px solid #ddd; padding: 15px; }}
    </style>
</head>
<body>
    <h1>Potato Blight Risk Calculation Methodology</h1>
    {html_content}
</body>
</html>"""
        
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        pdfkit.from_string(html_content, output_pdf, options=options)
        print(f"✅ Successfully created PDF: {output_pdf}")
        return True
    except ImportError:
        print("❌ pdfkit not installed. Install with: pip install pdfkit")
        print("   Also requires wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    markdown_file = "RISK_CALCULATION_METHODOLOGY.md"
    output_pdf = "RISK_CALCULATION_METHODOLOGY.pdf"
    
    if not Path(markdown_file).exists():
        print(f"❌ Error: {markdown_file} not found!")
        sys.exit(1)
    
    print(f"📄 Converting {markdown_file} to PDF...")
    
    # Try weasyprint first
    try:
        import weasyprint
        if markdown_to_pdf(markdown_file, output_pdf):
            sys.exit(0)
    except ImportError:
        print("⚠️  weasyprint not installed. Trying alternative method...")
    
    # Try alternative method
    if not markdown_to_pdf_alternative(markdown_file, output_pdf):
        print("\n" + "="*60)
        print("INSTALLATION INSTRUCTIONS:")
        print("="*60)
        print("\nOption 1 (Recommended): Install weasyprint")
        print("  pip install weasyprint markdown")
        print("\nOption 2: Install pdfkit (requires wkhtmltopdf)")
        print("  pip install pdfkit markdown")
        print("  Download wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html")
        print("\nOption 3: Use online converter")
        print("  Upload RISK_CALCULATION_METHODOLOGY.md to:")
        print("  - https://www.markdowntopdf.com/")
        print("  - https://dillinger.io/ (export as PDF)")
        sys.exit(1)

