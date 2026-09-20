import re
import os
import markdown
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

MD_PATH = r"d:\Learning\Stack\Siva_Prasad_Product_Company_AI_Roadmap.md"
HTML_PATH = r"d:\Learning\Stack\Siva_Prasad_Product_Company_AI_Roadmap.html"
DOCX_PATH = r"d:\Learning\Stack\Siva_Prasad_Product_Company_AI_Roadmap.docx"

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_content = f.read()

# ==============================================================================
# 1. GENERATE STYLED HTML FOR BROWSER & PRINT/PDF
# ==============================================================================

# Parse markdown to HTML using python-markdown with extensions
md_extensions = ['extra', 'sane_lists', 'toc']
html_body = markdown.markdown(md_content, extensions=md_extensions)

# Extract Table of Contents from headings
toc_items = []
heading_regex = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
for match in heading_regex.finditer(md_content):
    level = len(match.group(1))
    title = match.group(2).strip()
    slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', title.lower()).strip('-')
    toc_items.append((level, title, slug))

# Build TOC HTML
toc_html_list = []
for level, title, slug in toc_items:
    clean_title = re.sub(r'[*_`]', '', title)
    if level == 1:
        toc_html_list.append(f'<li class="toc-h1"><a href="#{slug}">{clean_title}</a></li>')
    elif level == 2:
        toc_html_list.append(f'<li class="toc-h2"><a href="#{slug}">{clean_title}</a></li>')

toc_html = "\n".join(toc_html_list)

# Add ids to headings in html_body
def add_heading_ids(match):
    tag = match.group(1)
    content = match.group(2)
    # clean slug
    text_only = re.sub(r'<[^>]+>', '', content)
    slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', text_only.lower()).strip('-')
    return f'<{tag} id="{slug}">{content}</{tag}>'

html_body_with_ids = re.sub(r'<(h[1-3])>(.*?)</\1>', add_heading_ids, html_body)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siva Prasad Vajja — Career Transition & AI Engineering Roadmap</title>
<style>
  :root {{
    --primary: #1e3a8a;
    --primary-light: #eff6ff;
    --text: #1f2937;
    --text-muted: #4b5563;
    --border: #e5e7eb;
    --bg-code: #f3f4f6;
    --accent: #2563eb;
    --callout-bg: #f8fafc;
    --callout-border: #3b82f6;
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: var(--text);
    background-color: #f1f5f9;
    line-height: 1.65;
    margin: 0;
    padding: 0;
    font-size: 15px;
  }}

  /* Top Bar Actions */
  .top-action-bar {{
    position: sticky;
    top: 0;
    z-index: 100;
    background: #ffffff;
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}

  .brand {{
    font-weight: 700;
    color: var(--primary);
    font-size: 1.05rem;
  }}

  .btn-group {{
    display: flex;
    gap: 12px;
  }}

  .btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;
    border: none;
  }}

  .btn-print {{
    background: var(--accent);
    color: white;
  }}
  .btn-print:hover {{
    background: #1d4ed8;
  }}

  .btn-toggle-toc {{
    background: #f1f5f9;
    color: var(--text);
    border: 1px solid var(--border);
  }}
  .btn-toggle-toc:hover {{
    background: #e2e8f0;
  }}

  /* Main Layout */
  .layout-container {{
    display: flex;
    max-width: 1400px;
    margin: 24px auto;
    padding: 0 20px;
    gap: 32px;
  }}

  /* Sidebar TOC */
  .sidebar {{
    width: 320px;
    flex-shrink: 0;
    position: sticky;
    top: 80px;
    max-height: calc(100vh - 100px);
    overflow-y: auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid var(--border);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}

  .sidebar h3 {{
    margin-top: 0;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    border-bottom: 2px solid var(--border);
    padding-bottom: 8px;
  }}

  .sidebar ul {{
    list-style: none;
    padding: 0;
    margin: 0;
  }}

  .sidebar li {{
    margin: 6px 0;
    font-size: 13px;
    line-height: 1.4;
  }}

  .sidebar li.toc-h1 {{
    font-weight: 600;
    margin-top: 10px;
  }}

  .sidebar li.toc-h2 {{
    padding-left: 14px;
    font-weight: 400;
    color: var(--text-muted);
  }}

  .sidebar a {{
    color: inherit;
    text-decoration: none;
  }}

  .sidebar a:hover {{
    color: var(--accent);
    text-decoration: underline;
  }}

  /* Main Document Content */
  .document-content {{
    flex: 1;
    min-width: 0;
    background: white;
    padding: 48px 56px;
    border-radius: 8px;
    border: 1px solid var(--border);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}

  h1 {{
    color: var(--primary);
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 36px;
    margin-bottom: 16px;
    font-size: 1.75rem;
    line-height: 1.3;
  }}

  h2 {{
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 28px;
    margin-bottom: 14px;
    font-size: 1.35rem;
  }}

  h3 {{
    color: #334155;
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 1.15rem;
  }}

  p, ul, ol {{
    margin-bottom: 14px;
  }}

  ul, ol {{
    padding-left: 24px;
  }}

  li {{
    margin-bottom: 4px;
  }}

  /* Blockquotes / Callout boxes */
  blockquote {{
    margin: 18px 0;
    padding: 14px 18px;
    background-color: var(--callout-bg);
    border-left: 4px solid var(--callout-border);
    border-radius: 0 6px 6px 0;
    color: #334155;
    font-size: 0.95rem;
  }}

  blockquote > :first-child {{
    margin-top: 0;
  }}
  blockquote > :last-child {{
    margin-bottom: 0;
  }}

  /* Code */
  code {{
    background: var(--bg-code);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: Consolas, Monaco, "Courier New", monospace;
    font-size: 0.88em;
    color: #b91c1c;
  }}

  pre {{
    background: #0f172a;
    color: #f8fafc;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.88em;
    line-height: 1.5;
  }}

  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
  }}

  hr {{
    border: 0;
    height: 1px;
    background: #e2e8f0;
    margin: 32px 0;
  }}

  a {{
    color: var(--accent);
    text-decoration: underline;
  }}

  /* PRINT STYLING (For Save as PDF & Printing) */
  @media print {{
    body {{
      background: white !important;
      color: black !important;
      font-size: 11pt !important;
      line-height: 1.45 !important;
    }}

    .top-action-bar, .sidebar {{
      display: none !important;
    }}

    .layout-container {{
      display: block !important;
      margin: 0 !important;
      padding: 0 !important;
      max-width: 100% !important;
    }}

    .document-content {{
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
    }}

    h1, h2, h3 {{
      page-break-after: avoid;
      color: black !important;
    }}

    h1 {{
      border-bottom: 2px solid #333 !important;
      margin-top: 24pt !important;
    }}

    blockquote, pre {{
      page-break-inside: avoid;
      background: #f8f9fa !important;
      border-left: 3px solid #666 !important;
      color: black !important;
    }}

    a {{
      color: black !important;
      text-decoration: underline !important;
    }}

    @page {{
      margin: 1.8cm 1.5cm;
      @bottom-right {{
        content: counter(page);
      }}
    }}
  }}
</style>
</head>
<body>

<div class="top-action-bar">
  <div class="brand">📄 Siva Prasad Vajja — Product Company & AI Roadmap</div>
  <div class="btn-group">
    <button class="btn btn-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
  </div>
</div>

<div class="layout-container">
  <nav class="sidebar" id="tocSidebar">
    <h3>Table of Contents</h3>
    <ul>
      {toc_html}
    </ul>
  </nav>

  <main class="document-content">
    {html_body_with_ids}
  </main>
</div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Generated HTML: {HTML_PATH}")


# ==============================================================================
# 2. GENERATE CLEAN FORMATTED WORD DOCUMENT (.DOCX)
# ==============================================================================

doc = Document()

# Set page margins to 1 inch
sections = doc.sections
for section in sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Set base Normal style font
style_normal = doc.styles['Normal']
font = style_normal.font
font.name = 'Segoe UI'
font.size = Pt(10.5)
font.color.rgb = RGBColor(33, 37, 41)

# Helper function to parse inline markdown (bold, italic, code) into runs
def add_formatted_text(paragraph, text, base_italic=False):
    # Regex to tokenize bold, inline code, and links
    # Matches: **bold**, `code`, [link text](url)
    pattern = re.compile(r'(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))')
    parts = pattern.split(text)
    
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            if base_italic:
                run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(160, 20, 20)
            if base_italic:
                run.italic = True
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            m = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if m:
                run = paragraph.add_run(m.group(1))
                run.font.color.rgb = RGBColor(29, 78, 216)
                run.underline = True
            else:
                run = paragraph.add_run(part)
        else:
            run = paragraph.add_run(part)
            if base_italic:
                run.italic = True

lines = md_content.split('\n')
i = 0
n = len(lines)

while i < n:
    line = lines[i]
    stripped = line.strip()

    # Empty line
    if not stripped:
        i += 1
        continue

    # Horizontal rule
    if stripped in ('---', '***', '___'):
        # Add a subtle separator or space
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run('—' * 40)
        run.font.color.rgb = RGBColor(200, 205, 210)
        i += 1
        continue

    # Heading 1
    if line.startswith('# ') and not line.startswith('## '):
        heading_text = line[2:].strip()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(heading_text)
        run.bold = True
        run.font.size = Pt(18)
        run.font.name = 'Segoe UI Semibold'
        run.font.color.rgb = RGBColor(30, 58, 138) # Deep navy
        i += 1
        continue

    # Heading 2
    if line.startswith('## ') and not line.startswith('### '):
        heading_text = line[3:].strip()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(heading_text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.name = 'Segoe UI Semibold'
        run.font.color.rgb = RGBColor(31, 41, 55) # Dark slate
        i += 1
        continue

    # Heading 3
    if line.startswith('### '):
        heading_text = line[4:].strip()
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(heading_text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(55, 65, 81)
        i += 1
        continue

    # Blockquotes (> ...)
    if line.startswith('>'):
        # Collect continuous blockquote lines
        quote_lines = []
        while i < n and (lines[i].startswith('>') or (lines[i].strip() and quote_lines and not lines[i].startswith('#'))):
            q_line = lines[i]
            if q_line.startswith('>'):
                q_line = q_line[1:].strip()
            else:
                q_line = q_line.strip()
            if q_line:
                quote_lines.append(q_line)
            i += 1
        
        quote_text = " ".join(quote_lines)
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.right_indent = Inches(0.3)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        
        add_formatted_text(p, quote_text, base_italic=True)
        continue

    # Bullet lists (- or * or nested)
    match_bullet = re.match(r'^(\s*)([-*])\s+(.*)$', line)
    if match_bullet:
        indent_spaces = len(match_bullet.group(1))
        content = match_bullet.group(3).strip()
        
        p = doc.add_paragraph(style='List Bullet')
        if indent_spaces >= 2:
            p.paragraph_format.left_indent = Inches(0.25 + (indent_spaces // 2) * 0.2)
        else:
            p.paragraph_format.left_indent = Inches(0.25)
            
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        
        add_formatted_text(p, content)
        i += 1
        continue

    # Code block (```)
    if line.startswith('```'):
        i += 1
        code_lines = []
        while i < n and not lines[i].startswith('```'):
            code_lines.append(lines[i])
            i += 1
        if i < n and lines[i].startswith('```'):
            i += 1
            
        code_text = "\n".join(code_lines)
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(40, 40, 40)
        continue

    # Standard Paragraph
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    add_formatted_text(p, stripped)
    i += 1

doc.save(DOCX_PATH)
print(f"Generated DOCX: {DOCX_PATH}")
