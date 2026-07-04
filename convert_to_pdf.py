#!/usr/bin/env python3
"""
Convert TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md to PDF

Requirements:
- pip install markdown pdfkit
- Install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
  OR use alternative: pip install weasyprint (better for complex formatting)
"""

import sys
import os

def convert_with_weasyprint(md_file, pdf_file):
    """Convert markdown to PDF using WeasyPrint (better formatting)"""
    try:
        import markdown
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Read markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables']
        )
        
        # Add CSS styling
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: 'Georgia', 'Times New Roman', serif;
                    font-size: 11pt;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    font-size: 24pt;
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-top: 30px;
                }}
                h2 {{
                    font-size: 18pt;
                    color: #34495e;
                    border-bottom: 2px solid #95a5a6;
                    padding-bottom: 5px;
                    margin-top: 25px;
                }}
                h3 {{
                    font-size: 14pt;
                    color: #555;
                    margin-top: 20px;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }}
                pre {{
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    overflow-x: auto;
                    font-size: 9pt;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    padding-left: 15px;
                    margin: 15px 0;
                    color: #555;
                }}
                .page-break {{
                    page-break-after: always;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert to PDF
        HTML(string=html_doc).write_pdf(pdf_file)
        print(f"[OK] PDF created successfully: {pdf_file}")
        return True
        
    except ImportError:
        print("[ERROR] WeasyPrint not installed. Install with: pip install weasyprint markdown")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def convert_with_pdfkit(md_file, pdf_file):
    """Convert markdown to PDF using pdfkit (requires wkhtmltopdf)"""
    try:
        import markdown
        import pdfkit
        
        # Read markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables']
        )
        
        # Add CSS
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Georgia, serif; font-size: 11pt; line-height: 1.6; }}
                h1 {{ font-size: 24pt; color: #2c3e50; border-bottom: 3px solid #3498db; }}
                h2 {{ font-size: 18pt; color: #34495e; border-bottom: 2px solid #95a5a6; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; }}
                pre {{ background-color: #f8f8f8; padding: 10px; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert to PDF
        pdfkit.from_string(html_doc, pdf_file)
        print(f"[OK] PDF created successfully: {pdf_file}")
        return True
        
    except ImportError:
        print("[ERROR] pdfkit not installed. Install with: pip install pdfkit markdown")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def main():
    md_file = "TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.md"
    pdf_file = "TECHNICAL_DISEASE_PREDICTION_METHODOLOGY.pdf"
    
    if not os.path.exists(md_file):
        print(f"[ERROR] File not found: {md_file}")
        sys.exit(1)
    
    print(f"Converting {md_file} to PDF...")
    
    # Try WeasyPrint first (better formatting)
    if convert_with_weasyprint(md_file, pdf_file):
        return
    
    # Fallback to pdfkit
    if convert_with_pdfkit(md_file, pdf_file):
        return
    
    print("\n[ERROR] Could not convert to PDF. Please install one of:")
    print("   1. pip install weasyprint markdown (recommended)")
    print("   2. pip install pdfkit markdown (requires wkhtmltopdf)")
    print("\nOr use an online converter like:")
    print("   - https://www.markdowntopdf.com/")
    print("   - https://dillinger.io/ (export as PDF)")

if __name__ == "__main__":
    main()

