import os
import re
import markdown
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = r"d:\Learning\Stack"
INTERVIEW_DIR = os.path.join(BASE_DIR, "Interview_Notes")
ROADMAP_MD = os.path.join(BASE_DIR, "Siva_Prasad_Product_Company_AI_Roadmap.md")

OUTPUT_HTML = os.path.join(BASE_DIR, "Siva_Prasad_Master_Product_AI_Guide.html")
OUTPUT_DOCX = os.path.join(BASE_DIR, "Siva_Prasad_Master_Product_AI_Guide.docx")

# 1. Discover and sequence all documents
files_in_notes = sorted([f for f in os.listdir(INTERVIEW_DIR) if f.endswith('.md')])

chapters = []

# Chapter 0: Master Career Roadmap
with open(ROADMAP_MD, "r", encoding="utf-8") as f:
    roadmap_content = f.read()

chapters.append({
    "id": "chap-roadmap",
    "num": "00-ROADMAP",
    "filename": "Siva_Prasad_Product_Company_AI_Roadmap.md",
    "title": "Master Product-Company Transition & AI Engineering Roadmap",
    "category": "Career Strategy & Roadmap",
    "content": roadmap_content
})

def categorize(filename):
    if filename.startswith("00") or filename == "INDEX.md":
        return "Audit & Index"
    num = filename[:2]
    if num in ["01", "02", "03", "04", "21", "26", "27"]:
        return "Core Java & Backend Internals"
    if num in ["05", "06", "07"]:
        return "Distributed Data & Messaging"
    if num in ["08", "09", "10", "11", "23", "28", "29"]:
        return "System Design & Production Cloud"
    if num in ["12", "13", "14", "15", "16", "17", "18", "19", "31", "38"]:
        return "Applied AI, LLMs & Spring AI"
    if num in ["20", "22", "24", "25", "30", "32", "33", "34", "35", "36", "37"]:
        return "Interview Workbooks & Domain Dossiers"
    return "General"

for f_name in files_in_notes:
    f_path = os.path.join(INTERVIEW_DIR, f_name)
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract title from first H1
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = m.group(1).strip() if m else f_name.replace('.md', '').replace('_', ' ')
    
    slug = "chap-" + re.sub(r'[^a-zA-Z0-9_\-]+', '-', f_name.lower().replace('.md', ''))
    chapters.append({
        "id": slug,
        "num": f_name[:2] if f_name[:2].isdigit() else "IDX",
        "filename": f_name,
        "title": title,
        "category": categorize(f_name),
        "content": content
    })

print(f"Total chapters indexed: {len(chapters)}")

# ==============================================================================
# BUILD MASTER HTML DOCUMENTATION PORTAL
# ==============================================================================
print("Generating Master HTML Portal...")

# Group chapters for sidebar navigation
categories = {}
for ch in chapters:
    categories.setdefault(ch["category"], []).append(ch)

sidebar_nav_html = []
for cat, ch_list in categories.items():
    sidebar_nav_html.append(f'<div class="nav-category"><h4>{cat}</h4><ul>')
    for ch in ch_list:
        clean_title = re.sub(r'[*_`]', '', ch["title"])
        sidebar_nav_html.append(f'<li><a href="#{ch["id"]}" class="nav-link"><span class="badge">{ch["num"]}</span> {clean_title}</a></li>')
    sidebar_nav_html.append('</ul></div>')

sidebar_html = "\n".join(sidebar_nav_html)

# Convert all markdown chapters to HTML
md_converter = markdown.Markdown(extensions=['extra', 'tables', 'toc', 'sane_lists'])

chapters_rendered = []
for ch in chapters:
    raw_md = ch["content"]
    rendered = md_converter.reset().convert(raw_md)
    
    # Add chapter anchor container
    chapter_block = f"""
    <section class="chapter-container" id="{ch['id']}">
      <div class="chapter-header">
        <span class="chapter-category-tag">{ch['category']}</span>
        <span class="chapter-number-tag">Section {ch['num']}</span>
        <h1 class="chapter-title">{ch['title']}</h1>
        <div class="chapter-meta">Source file: <code>{ch['filename']}</code></div>
      </div>
      <div class="chapter-body">
        {rendered}
      </div>
    </section>
    """
    chapters_rendered.append(chapter_block)

all_chapters_html = "\n<hr class='chapter-divider'>\n".join(chapters_rendered)

master_html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siva Prasad Vajja — Master Product Engineering & AI Interview Compendium</title>
<style>
  :root {{
    --primary: #1e3a8a;
    --primary-light: #eff6ff;
    --text: #1f2937;
    --text-muted: #4b5563;
    --border: #e5e7eb;
    --bg-page: #f8fafc;
    --bg-card: #ffffff;
    --bg-code: #f1f5f9;
    --accent: #2563eb;
    --callout-bg: #f0fdf4;
    --callout-border: #16a34a;
    --table-stripe: #f9fafb;
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    color: var(--text);
    background-color: var(--bg-page);
    line-height: 1.65;
    margin: 0;
    padding: 0;
    font-size: 15px;
  }}

  /* Top sticky action header */
  .top-header {{
    position: sticky;
    top: 0;
    z-index: 1000;
    background: #ffffff;
    border-bottom: 1px solid var(--border);
    padding: 12px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }}

  .top-header .brand {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .top-header .sub-brand {{
    font-size: 0.85rem;
    color: var(--text-muted);
    font-weight: normal;
  }}

  .actions {{
    display: flex;
    gap: 12px;
    align-items: center;
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
    border: none;
    transition: all 0.2s ease;
  }}

  .btn-print {{
    background: var(--accent);
    color: white;
  }}
  .btn-print:hover {{
    background: #1d4ed8;
  }}

  /* Layout Container */
  .app-layout {{
    display: flex;
    max-width: 1600px;
    margin: 0 auto;
  }}

  /* Sidebar */
  .sidebar {{
    width: 360px;
    flex-shrink: 0;
    position: sticky;
    top: 57px;
    height: calc(100vh - 57px);
    overflow-y: auto;
    background: #ffffff;
    border-right: 1px solid var(--border);
    padding: 20px;
  }}

  .search-box {{
    margin-bottom: 16px;
  }}

  .search-box input {{
    width: 100%;
    padding: 9px 12px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 13px;
    outline: none;
    background: #f8fafc;
  }}
  .search-box input:focus {{
    border-color: var(--accent);
    background: #ffffff;
  }}

  .nav-category {{
    margin-bottom: 20px;
  }}

  .nav-category h4 {{
    margin: 0 0 8px 0;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
    font-weight: 700;
    padding-left: 6px;
  }}

  .nav-category ul {{
    list-style: none;
    padding: 0;
    margin: 0;
  }}

  .nav-category li {{
    margin-bottom: 2px;
  }}

  .nav-link {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 13px;
    color: #334155;
    text-decoration: none;
    line-height: 1.35;
    transition: background 0.15s;
  }}

  .nav-link:hover {{
    background: #f1f5f9;
    color: var(--accent);
  }}

  .badge {{
    display: inline-block;
    padding: 2px 6px;
    background: #e2e8f0;
    color: #475569;
    border-radius: 4px;
    font-size: 10px;
    font-family: monospace;
    font-weight: 600;
    flex-shrink: 0;
  }}

  /* Content area */
  .main-content {{
    flex: 1;
    min-width: 0;
    padding: 40px 60px;
  }}

  .chapter-container {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 44px 50px;
    margin-bottom: 40px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  }}

  .chapter-header {{
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 20px;
    margin-bottom: 30px;
  }}

  .chapter-category-tag {{
    display: inline-block;
    padding: 3px 10px;
    background: #dbeafe;
    color: #1e40af;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    margin-right: 8px;
  }}

  .chapter-number-tag {{
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
  }}

  .chapter-title {{
    margin: 12px 0 6px 0;
    font-size: 2rem;
    color: var(--primary);
    line-height: 1.25;
  }}

  .chapter-meta {{
    font-size: 12px;
    color: #94a3b8;
  }}

  .chapter-body h1 {{
    display: none; /* Already shown in header */
  }}

  .chapter-body h2 {{
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 36px;
    margin-bottom: 16px;
    font-size: 1.45rem;
  }}

  .chapter-body h3 {{
    color: #334155;
    margin-top: 24px;
    margin-bottom: 10px;
    font-size: 1.18rem;
  }}

  .chapter-body h4 {{
    color: #475569;
    margin-top: 18px;
    font-size: 1.05rem;
  }}

  .chapter-body p, .chapter-body ul, .chapter-body ol {{
    margin-bottom: 14px;
  }}

  .chapter-body ul, .chapter-body ol {{
    padding-left: 24px;
  }}

  .chapter-body li {{
    margin-bottom: 5px;
  }}

  /* Blockquotes / Callouts */
  blockquote {{
    margin: 18px 0;
    padding: 14px 18px;
    background: #f8fafc;
    border-left: 4px solid var(--accent);
    border-radius: 0 6px 6px 0;
    color: #334155;
  }}

  /* Code */
  code {{
    background: var(--bg-code);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: Consolas, Monaco, "Courier New", monospace;
    font-size: 0.88em;
    color: #991b1b;
  }}

  pre {{
    background: #0f172a;
    color: #f8fafc;
    padding: 16px 20px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 0.88em;
    line-height: 1.5;
  }}

  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
  }}

  /* TABLES */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 13.5px;
  }}

  th, td {{
    padding: 10px 14px;
    border: 1px solid var(--border);
    text-align: left;
    vertical-align: top;
  }}

  th {{
    background-color: #f1f5f9;
    color: #1e293b;
    font-weight: 700;
  }}

  tr:nth-child(even) td {{
    background-color: var(--table-stripe);
  }}

  hr.chapter-divider {{
    border: none;
    border-top: 2px dashed #cbd5e1;
    margin: 50px 0;
  }}

  /* PRINT STYLES */
  @media print {{
    .top-header, .sidebar, .search-box {{
      display: none !important;
    }}
    .app-layout {{
      display: block !important;
      margin: 0 !important;
    }}
    .main-content {{
      padding: 0 !important;
    }}
    .chapter-container {{
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
      page-break-before: always;
    }}
    h1, h2, h3 {{
      page-break-after: avoid;
      color: black !important;
    }}
    pre, blockquote, table {{
      page-break-inside: avoid;
    }}
    table {{
      font-size: 10pt !important;
    }}
  }}
</style>
</head>
<body>

<header class="top-header">
  <div class="brand">
    <span>📘</span>
    <div>
      <div>Siva Prasad Vajja — Complete Product Engineering & AI Interview Compendium</div>
      <div class="sub-brand">Complete Master Study Guide &bull; 41 Chapters &bull; All Interview Topics</div>
    </div>
  </div>
  <div class="actions">
    <button class="btn btn-print" onclick="window.print()">🖨️ Print / Save to PDF</button>
  </div>
</header>

<div class="app-layout">
  <aside class="sidebar">
    <div class="search-box">
      <input type="text" id="topicSearch" placeholder="🔍 Search topics or chapters..." onkeyup="filterTopics()">
    </div>
    <nav id="sidebarNav">
      {sidebar_html}
    </nav>
  </aside>

  <main class="main-content">
    {all_chapters_html}
  </main>
</div>

<script>
function filterTopics() {{
  let input = document.getElementById('topicSearch').value.toLowerCase();
  let links = document.querySelectorAll('.nav-link');
  links.forEach(link => {{
    let text = link.textContent.toLowerCase();
    let parentLi = link.parentElement;
    if (text.includes(input)) {{
      parentLi.style.display = "";
    }} else {{
      parentLi.style.display = "none";
    }}
  }});
}}
</script>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(master_html_template)

print(f"Master HTML successfully generated at: {OUTPUT_HTML}")


# ==============================================================================
# BUILD MASTER WORD DOCUMENT (.DOCX)
# ==============================================================================
print("Generating Master Word (.docx) Document... (This compiles all 41 chapters)")

doc = Document()

# Page Setup: Standard Margins
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

# Configure base styles
style_normal = doc.styles['Normal']
font = style_normal.font
font.name = 'Segoe UI'
font.size = Pt(10)
font.color.rgb = RGBColor(33, 37, 41)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_formatted_runs(paragraph, text, base_italic=False):
    # Split text for **bold**, `code`, and [link](url)
    pattern = re.compile(r'(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))')
    parts = pattern.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            if base_italic: run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(160, 20, 20)
            if base_italic: run.italic = True
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
            if base_italic: run.italic = True

# --- COVER / TITLE PAGE ---
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(80)
title_p.paragraph_format.space_after = Pt(8)
r_title = title_p.add_run("Product-Company Career Transition\n& AI Engineering Master Compendium")
r_title.bold = True
r_title.font.size = Pt(26)
r_title.font.name = 'Segoe UI'
r_title.font.color.rgb = RGBColor(30, 58, 138)

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(20)
r_sub = sub_p.add_run("Candidate: Siva Prasad Vajja — Java 17 | Spring Boot | Microservices | Distributed Systems | Spring AI")
r_sub.font.size = Pt(13)
r_sub.font.color.rgb = RGBColor(71, 85, 105)

info_p = doc.add_paragraph()
info_p.paragraph_format.space_after = Pt(40)
r_info = info_p.add_run("Comprehensive Interview Preparation, System Architecture & Applied AI Master Reference\nIncludes all 40 Technical Deep-Dive Notes and Master Career Strategy.")
r_info.font.italic = True
r_info.font.size = Pt(10.5)
r_info.font.color.rgb = RGBColor(100, 116, 139)

doc.add_page_break()

# --- TABLE OF CONTENTS SUMMARY ---
toc_title = doc.add_paragraph()
toc_title.paragraph_format.space_before = Pt(10)
toc_title.paragraph_format.space_after = Pt(12)
r_toc = toc_title.add_run("Master Table of Contents")
r_toc.bold = True
r_toc.font.size = Pt(18)
r_toc.font.color.rgb = RGBColor(30, 58, 138)

toc_table = doc.add_table(rows=1, cols=3)
toc_table.style = 'Table Grid'
hdr_cells = toc_table.rows[0].cells
hdr_cells[0].text = "#"
hdr_cells[1].text = "Category & Topic"
hdr_cells[2].text = "Source File"
for c in hdr_cells:
    set_cell_background(c, "E2E8F0")
    for p in c.paragraphs:
        for r in p.runs:
            r.bold = True

for ch in chapters:
    row_cells = toc_table.add_row().cells
    row_cells[0].text = ch["num"]
    row_cells[1].text = f"[{ch['category']}] {ch['title']}"
    row_cells[2].text = ch["filename"]
    for c in row_cells:
        set_cell_margins(c, top=40, bottom=40, left=80, right=80)

# --- PROCESS EACH CHAPTER ---
for ch_idx, ch in enumerate(chapters):
    doc.add_page_break()
    
    # Chapter Title Header Box
    head_p = doc.add_paragraph()
    head_p.paragraph_format.space_before = Pt(12)
    head_p.paragraph_format.space_after = Pt(2)
    head_p.paragraph_format.keep_with_next = True
    r_tag = head_p.add_run(f"CHAPTER {ch['num']}  |  {ch['category'].upper()}")
    r_tag.bold = True
    r_tag.font.size = Pt(9.5)
    r_tag.font.color.rgb = RGBColor(37, 99, 235)
    
    h1_p = doc.add_paragraph()
    h1_p.paragraph_format.space_before = Pt(2)
    h1_p.paragraph_format.space_after = Pt(8)
    h1_p.paragraph_format.keep_with_next = True
    r_h1 = h1_p.add_run(ch['title'])
    r_h1.bold = True
    r_h1.font.size = Pt(18)
    r_h1.font.color.rgb = RGBColor(30, 58, 138)
    
    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_after = Pt(14)
    r_m = meta_p.add_run(f"Source Reference: Interview_Notes/{ch['filename']}")
    r_m.font.italic = True
    r_m.font.size = Pt(8.5)
    r_m.font.color.rgb = RGBColor(148, 163, 184)
    
    # Parse Markdown lines
    lines = ch['content'].split('\n')
    i = 0
    n = len(lines)
    
    # Skip the very first H1 if it matches chapter title to avoid duplication
    if n > 0 and lines[0].startswith('# '):
        i = 1
        
    while i < n:
        line = lines[i]
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue
            
        # Horizontal Rule
        if stripped in ('---', '***', '___'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run('—' * 35)
            r.font.color.rgb = RGBColor(220, 224, 230)
            i += 1
            continue
            
        # Headings
        if line.startswith('# ') and not line.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line[2:].strip())
            r.bold = True
            r.font.size = Pt(15)
            r.font.color.rgb = RGBColor(30, 58, 138)
            i += 1
            continue
            
        if line.startswith('## ') and not line.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line[3:].strip())
            r.bold = True
            r.font.size = Pt(13)
            r.font.color.rgb = RGBColor(31, 41, 55)
            i += 1
            continue
            
        if line.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(9)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line[4:].strip())
            r.bold = True
            r.font.size = Pt(11)
            r.font.color.rgb = RGBColor(55, 65, 81)
            i += 1
            continue
            
        # Markdown Table Detection
        if '|' in stripped and i + 1 < n and '|---' in lines[i + 1]:
            table_lines = []
            while i < n and '|' in lines[i].strip():
                table_lines.append(lines[i].strip())
                i += 1
                
            if len(table_lines) >= 3:
                # Parse header
                headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                data_rows = []
                for t_row in table_lines[2:]:
                    cells = [c.strip() for c in t_row.split('|')[1:-1]]
                    data_rows.append(cells)
                
                # Create docx table
                cols_count = len(headers)
                t = doc.add_table(rows=1, cols=cols_count)
                t.style = 'Table Grid'
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                
                # Fill header
                hdr_cells = t.rows[0].cells
                for c_idx, h_text in enumerate(headers):
                    if c_idx < len(hdr_cells):
                        hdr_cells[c_idx].text = h_text
                        set_cell_background(hdr_cells[c_idx], "F1F5F9")
                        set_cell_margins(hdr_cells[c_idx], top=60, bottom=60, left=100, right=100)
                        for p in hdr_cells[c_idx].paragraphs:
                            for r in p.runs:
                                r.bold = True
                                r.font.size = Pt(9)
                                
                # Fill rows
                for r_idx, r_data in enumerate(data_rows):
                    row_cells = t.add_row().cells
                    for c_idx, cell_value in enumerate(r_data):
                        if c_idx < len(row_cells):
                            p = row_cells[c_idx].paragraphs[0]
                            add_formatted_runs(p, cell_value)
                            p.paragraph_format.space_before = Pt(1)
                            p.paragraph_format.space_after = Pt(1)
                            set_cell_margins(row_cells[c_idx], top=50, bottom=50, left=100, right=100)
                            if r_idx % 2 == 1:
                                set_cell_background(row_cells[c_idx], "F8FAFC")
                
                # Space after table
                p_after = doc.add_paragraph()
                p_after.paragraph_format.space_before = Pt(4)
                p_after.paragraph_format.space_after = Pt(4)
            continue
            
        # Blockquotes (> ...)
        if line.startswith('>'):
            quote_lines = []
            while i < n and (lines[i].startswith('>') or (lines[i].strip() and quote_lines and not lines[i].startswith('#'))):
                q_l = lines[i]
                if q_l.startswith('>'):
                    q_l = q_l[1:].strip()
                else:
                    q_l = q_l.strip()
                if q_l:
                    quote_lines.append(q_l)
                i += 1
            quote_text = " ".join(quote_lines)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.right_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(5)
            add_formatted_runs(p, quote_text, base_italic=True)
            continue
            
        # Bullet list
        match_bullet = re.match(r'^(\s*)([-*])\s+(.*)$', line)
        if match_bullet:
            indent_spaces = len(match_bullet.group(1))
            content = match_bullet.group(3).strip()
            p = doc.add_paragraph(style='List Bullet')
            if indent_spaces >= 2:
                p.paragraph_format.left_indent = Inches(0.25 + (indent_spaces // 2) * 0.15)
            else:
                p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            add_formatted_runs(p, content)
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
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(5)
            r = p.add_run(code_text)
            r.font.name = 'Consolas'
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(40, 40, 40)
            continue
            
        # Normal Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        add_formatted_runs(p, stripped)
        i += 1

print(f"Saving Master Word Document: {OUTPUT_DOCX}...")
doc.save(OUTPUT_DOCX)
print(f"Master DOCX successfully generated at: {OUTPUT_DOCX}")
