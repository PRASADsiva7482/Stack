import os
import re
import json
import markdown
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = r"d:\Learning\Stack"
INTERVIEW_DIR = os.path.join(BASE_DIR, "Interview_Notes")
ROADMAP_MD = os.path.join(BASE_DIR, "Siva_Prasad_Product_Company_AI_Roadmap.md")

INDEX_HTML = os.path.join(BASE_DIR, "index.html")
DOCX_OUTPUT = os.path.join(BASE_DIR, "Siva_Prasad_Master_Product_AI_Guide.docx")

# 1. Load and Index All Chapters
files_in_notes = sorted([f for f in os.listdir(INTERVIEW_DIR) if f.endswith('.md')])

chapters = []

# Chapter 0: Master Career Roadmap
with open(ROADMAP_MD, "r", encoding="utf-8") as f:
    roadmap_content = f.read()

chapters.append({
    "id": "chap-00-roadmap",
    "num": "00",
    "slug": "career-transition-roadmap",
    "filename": "Siva_Prasad_Product_Company_AI_Roadmap.md",
    "title": "Master Product-Company Transition & AI Engineering Roadmap",
    "category": "Career Strategy & Roadmap",
    "content": roadmap_content
})

def categorize(filename):
    if filename.startswith("00") or filename == "INDEX.md":
        return "Audit & Strategy Index"
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
    
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = m.group(1).strip() if m else f_name.replace('.md', '').replace('_', ' ')
    
    clean_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', f_name.lower().replace('.md', '')).strip('-')
    chapters.append({
        "id": f"chap-{clean_slug}",
        "num": f_name[:2] if f_name[:2].isdigit() else "IDX",
        "slug": clean_slug,
        "filename": f_name,
        "title": title,
        "category": categorize(f_name),
        "content": content
    })

print(f"Loaded {len(chapters)} chapters.")

# Markdown Parser
md_parser = markdown.Markdown(extensions=['extra', 'tables', 'sane_lists'])

# Pre-parse HTML content and Sub-headings (H2, H3) for right-hand TOC
processed_chapters = []
for ch in chapters:
    raw_md = ch["content"]
    
    # Extract subheadings for "On this page" TOC
    subheadings = []
    for line in raw_md.split('\n'):
        line_s = line.strip()
        if line_s.startswith('## ') and not line_s.startswith('### '):
            h_text = line_s[3:].strip()
            h_clean = re.sub(r'[*_`#]', '', h_text)
            h_id = re.sub(r'[^a-zA-Z0-9_\-]+', '-', h_clean.lower()).strip('-')
            subheadings.append({"level": 2, "title": h_clean, "id": h_id})
        elif line_s.startswith('### '):
            h_text = line_s[4:].strip()
            h_clean = re.sub(r'[*_`#]', '', h_text)
            h_id = re.sub(r'[^a-zA-Z0-9_\-]+', '-', h_clean.lower()).strip('-')
            subheadings.append({"level": 3, "title": h_clean, "id": h_id})

    # Pre-process links: Convert relative markdown links ([file.md](file.md)) to hash links (#chap-slug)
    def rewrite_md_links(match):
        link_text = match.group(1)
        href = match.group(2)
        if href.endswith('.md') or '.md#' in href:
            parts = href.split('#')
            f_name_only = parts[0].split('/')[-1]
            hash_part = f"#{parts[1]}" if len(parts) > 1 else ""
            target = next((c for c in chapters if c["filename"].lower() == f_name_only.lower()), None)
            if target:
                return f"[{link_text}](#{target['id']}{hash_part})"
            else:
                return f"[{link_text}](Interview_Notes/{f_name_only}{hash_part})"
        return match.group(0)

    preprocessed_md = re.sub(r'\[(.*?)\]\((.*?)\)', rewrite_md_links, raw_md)

    # Render HTML
    html_content = md_parser.reset().convert(preprocessed_md)
    
    # Inject IDs into h2 and h3
    def inject_id(match):
        tag = match.group(1)
        inner = match.group(2)
        text_only = re.sub(r'<[^>]+>', '', inner)
        slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', text_only.lower()).strip('-')
        return f'<{tag} id="{slug}">{inner}</{tag}>'

    html_content = re.sub(r'<(h[2-4])>(.*?)</\1>', inject_id, html_content)
    
    # Estimate reading time (approx 200 words per min)
    word_count = len(raw_md.split())
    read_time = max(2, round(word_count / 200))
    
    processed_chapters.append({
        "id": ch["id"],
        "num": ch["num"],
        "slug": ch["slug"],
        "filename": ch["filename"],
        "title": ch["title"],
        "category": ch["category"],
        "readTime": f"{read_time} min read",
        "wordCount": word_count,
        "subheadings": subheadings,
        "html": html_content
    })

# Convert data to JSON for high-performance SPA routing
chapters_json = json.dumps([{
    "id": c["id"],
    "num": c["num"],
    "slug": c["slug"],
    "filename": c["filename"],
    "title": re.sub(r'[*_`]', '', c["title"]),
    "category": c["category"],
    "readTime": c["readTime"],
    "subheadings": c["subheadings"],
    "html": c["html"]
} for c in processed_chapters])

# Group chapters for left navigation
categories = {}
for ch in processed_chapters:
    categories.setdefault(ch["category"], []).append(ch)

nav_list_html = []
for cat_name, ch_items in categories.items():
    nav_list_html.append(f'''
    <div class="nav-group">
      <div class="nav-group-header">
        <span>{cat_name}</span>
        <span class="nav-group-count">{len(ch_items)}</span>
      </div>
      <ul class="nav-group-items">
    ''')
    for item in ch_items:
        clean_t = re.sub(r'[*_`]', '', item["title"])
        nav_list_html.append(f'''
        <li>
          <a href="#{item["id"]}" class="nav-item" data-id="{item["id"]}">
            <span class="nav-num">{item["num"]}</span>
            <span class="nav-title">{clean_t}</span>
          </a>
        </li>
        ''')
    nav_list_html.append('</ul></div>')

left_sidebar_html = "\n".join(nav_list_html)

# ==============================================================================
# 2. GENERATE INDUSTRY-STANDARD HTML DOCUMENTATION PORTAL
# ==============================================================================
print("Generating Industry-Standard Documentation Portal...")

html_template = f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siva Prasad Vajja &mdash; Senior Product Engineer &amp; AI Compendium</title>
<meta name="description" content="Production-grade Technical Interview &amp; Architecture Reference for Senior Software Engineers targeting Tier-1 Product Companies.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<!-- Prism Syntax Highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
<style>
  :root {{
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', Consolas, Monaco, monospace;
    
    /* Strict Neutral Scale */
    --bg-canvas: #fafafa;
    --bg-surface: #ffffff;
    --bg-subtle: #f4f4f5;
    --bg-muted: #e4e4e7;
    
    --border-subtle: #e4e4e7;
    --border-strong: #d4d4d8;
    
    --text-primary: #09090b;
    --text-secondary: #52525b;
    --text-muted: #71717a;
    
    --accent: #0284c7;
    --accent-hover: #0369a1;
    --accent-subtle: #f0f9ff;
    --accent-text: #0369a1;

    --callout-bg: #f8fafc;
    --callout-border: #0ea5e9;

    --table-header: #f4f4f5;
    --table-stripe: #fafafa;
    --table-border: #e4e4e7;

    --sidebar-width: 320px;
    --toc-width: 260px;
    --header-height: 56px;
    --content-max-width: 860px;
  }}

  [data-theme="dark"] {{
    --bg-canvas: #09090b;
    --bg-surface: #121215;
    --bg-subtle: #18181b;
    --bg-muted: #27272a;
    
    --border-subtle: #27272a;
    --border-strong: #3f3f46;
    
    --text-primary: #fafafa;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    
    --accent: #38bdf8;
    --accent-hover: #7dd3fc;
    --accent-subtle: #082f49;
    --accent-text: #7dd3fc;

    --callout-bg: #0c1524;
    --callout-border: #0284c7;

    --table-header: #18181b;
    --table-stripe: #0f1117;
    --table-border: #27272a;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  html {{
    scroll-behavior: smooth;
    font-size: 15px;
  }}

  body {{
    font-family: var(--font-sans);
    background-color: var(--bg-canvas);
    color: var(--text-primary);
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }}

  /* Top Navigation Bar */
  .app-header {{
    position: sticky;
    top: 0;
    z-index: 50;
    height: var(--header-height);
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    backdrop-filter: blur(12px);
  }}

  .header-left {{
    display: flex;
    align-items: center;
    gap: 16px;
  }}

  .btn-mobile-nav {{
    display: none;
    background: transparent;
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    padding: 6px 10px;
    color: var(--text-primary);
    cursor: pointer;
  }}

  .header-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: var(--text-primary);
  }}

  .brand-logo {{
    width: 24px;
    height: 24px;
    background: var(--text-primary);
    color: var(--bg-surface);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
    font-family: var(--font-mono);
  }}

  .brand-title {{
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
  }}

  .brand-badge {{
    font-size: 11px;
    padding: 2px 8px;
    background: var(--bg-subtle);
    color: var(--text-secondary);
    border-radius: 999px;
    border: 1px solid var(--border-subtle);
    font-weight: 500;
  }}

  .header-actions {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .action-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    font-size: 12.5px;
    font-weight: 500;
    border-radius: 6px;
    text-decoration: none;
    color: var(--text-secondary);
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    cursor: pointer;
    transition: all 0.15s ease;
  }}

  .action-btn:hover {{
    color: var(--text-primary);
    background: var(--bg-subtle);
    border-color: var(--border-strong);
  }}

  .action-btn-primary {{
    background: var(--accent);
    color: #ffffff;
    border: 1px solid var(--accent);
  }}
  .action-btn-primary:hover {{
    background: var(--accent-hover);
    color: #ffffff;
    border-color: var(--accent-hover);
  }}

  /* App Layout */
  .app-container {{
    display: flex;
    max-width: 1720px;
    margin: 0 auto;
  }}

  /* Left Sidebar Navigation */
  .sidebar-nav {{
    width: var(--sidebar-width);
    flex-shrink: 0;
    position: sticky;
    top: var(--header-height);
    height: calc(100vh - var(--header-height));
    overflow-y: auto;
    background: var(--bg-surface);
    border-right: 1px solid var(--border-subtle);
    padding: 16px 12px;
  }}

  .search-wrapper {{
    position: relative;
    margin-bottom: 16px;
    padding: 0 4px;
  }}

  .search-input {{
    width: 100%;
    padding: 7px 10px 7px 32px;
    font-size: 12.5px;
    font-family: var(--font-sans);
    background: var(--bg-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    color: var(--text-primary);
    outline: none;
    transition: all 0.15s ease;
  }}

  .search-input:focus {{
    background: var(--bg-surface);
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-subtle);
  }}

  .search-icon {{
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    pointer-events: none;
    width: 14px;
    height: 14px;
  }}

  .nav-group {{
    margin-bottom: 18px;
  }}

  .nav-group-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }}

  .nav-group-count {{
    font-size: 10px;
    font-family: var(--font-mono);
  }}

  .nav-group-items {{
    list-style: none;
  }}

  .nav-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 13px;
    color: var(--text-secondary);
    text-decoration: none;
    line-height: 1.35;
    transition: all 0.1s ease;
  }}

  .nav-item:hover {{
    background: var(--bg-subtle);
    color: var(--text-primary);
  }}

  .nav-item.active {{
    background: var(--accent-subtle);
    color: var(--accent-text);
    font-weight: 500;
  }}

  .nav-num {{
    font-size: 10px;
    font-family: var(--font-mono);
    color: var(--text-muted);
    min-width: 18px;
  }}

  .nav-title {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  /* Main Reader Content */
  .main-reader {{
    flex: 1;
    min-width: 0;
    padding: 40px 48px 80px 48px;
    display: flex;
    justify-content: center;
  }}

  .article-container {{
    width: 100%;
    max-width: var(--content-max-width);
  }}

  /* Breadcrumb */
  .breadcrumb {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    color: var(--text-muted);
    margin-bottom: 16px;
  }}

  .breadcrumb a {{
    color: var(--text-muted);
    text-decoration: none;
  }}
  .breadcrumb a:hover {{
    color: var(--text-primary);
  }}

  /* Chapter Header */
  .article-header {{
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border-subtle);
  }}

  .article-meta-tags {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }}

  .badge-category {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    padding: 3px 8px;
    background: var(--accent-subtle);
    color: var(--accent-text);
    border-radius: 4px;
  }}

  .badge-time {{
    font-size: 12px;
    color: var(--text-muted);
  }}

  .article-title {{
    font-size: 2.1rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.25;
    color: var(--text-primary);
    margin-bottom: 10px;
  }}

  .article-source {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 6px;
  }}

  .source-link-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--accent);
    text-decoration: none;
    font-family: var(--font-mono);
    font-size: 12px;
    padding: 3px 10px;
    background: var(--bg-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: 6px;
    font-weight: 500;
    transition: all 0.15s ease;
  }}
  .source-link-btn:hover {{
    background: var(--accent-subtle);
    border-color: var(--accent);
    color: var(--accent-text);
  }}

  .source-badge {{
    font-size: 10px;
    background: var(--accent);
    color: #ffffff;
    padding: 1px 6px;
    border-radius: 4px;
    font-weight: 600;
  }}

  .doc-link-tag {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 1px 7px;
    background: var(--accent-subtle);
    color: var(--accent-text) !important;
    border-radius: 4px;
    text-decoration: none !important;
    border: 1px solid rgba(2, 132, 199, 0.25);
    font-weight: 500;
    transition: all 0.12s ease;
  }}
  .doc-link-tag:hover {{
    background: var(--accent);
    color: #ffffff !important;
    border-color: var(--accent);
  }}


  /* Article Body Typography (GitBook / Stripe style) */
  .article-body {{
    font-size: 15px;
    line-height: 1.75;
    color: var(--text-secondary);
  }}

  .article-body h1 {{
    display: none; /* Already rendered in header */
  }}

  .article-body h2 {{
    font-size: 1.45rem;
    font-weight: 600;
    letter-spacing: -0.015em;
    color: var(--text-primary);
    margin-top: 40px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-subtle);
  }}

  .article-body h3 {{
    font-size: 1.18rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 28px;
    margin-bottom: 12px;
  }}

  .article-body h4 {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-top: 20px;
    margin-bottom: 8px;
  }}

  .article-body p {{
    margin-bottom: 16px;
  }}

  .article-body ul, .article-body ol {{
    margin-bottom: 16px;
    padding-left: 22px;
  }}

  .article-body li {{
    margin-bottom: 6px;
  }}

  .article-body strong {{
    color: var(--text-primary);
    font-weight: 600;
  }}

  /* Blockquote / Notes */
  .article-body blockquote {{
    margin: 20px 0;
    padding: 14px 18px;
    background: var(--callout-bg);
    border-left: 3px solid var(--callout-border);
    border-radius: 0 6px 6px 0;
    color: var(--text-primary);
    font-size: 14.5px;
  }}

  /* Code & Syntax Highlighting */
  .article-body code {{
    font-family: var(--font-mono);
    font-size: 0.88em;
    padding: 2px 6px;
    background: var(--bg-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    color: var(--text-primary);
  }}

  .code-block-wrapper {{
    position: relative;
    margin: 20px 0;
  }}

  .code-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #1e1e24;
    padding: 6px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: #a1a1aa;
    border: 1px solid #27272a;
    border-bottom: none;
  }}

  .copy-btn {{
    background: transparent;
    border: none;
    color: #a1a1aa;
    cursor: pointer;
    font-size: 11px;
    font-family: var(--font-sans);
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .copy-btn:hover {{
    color: #ffffff;
  }}

  .article-body pre {{
    background: #0f1117 !important;
    border: 1px solid #27272a;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 16px !important;
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 13px !important;
    line-height: 1.6;
    margin: 0 !important;
  }}

  .article-body pre code {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    color: #f4f4f5 !important;
  }}

  /* Tables */
  .table-wrapper {{
    overflow-x: auto;
    margin: 24px 0;
    border: 1px solid var(--table-border);
    border-radius: 8px;
  }}

  .article-body table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
    line-height: 1.5;
  }}

  .article-body th {{
    background: var(--table-header);
    color: var(--text-primary);
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    border-bottom: 1px solid var(--table-border);
  }}

  .article-body td {{
    padding: 10px 14px;
    border-bottom: 1px solid var(--table-border);
    color: var(--text-secondary);
    vertical-align: top;
  }}

  .article-body tr:nth-child(even) td {{
    background: var(--table-stripe);
  }}

  .article-body tr:last-child td {{
    border-bottom: none;
  }}

  .article-body hr {{
    border: none;
    border-top: 1px solid var(--border-subtle);
    margin: 36px 0;
  }}

  .article-body a {{
    color: var(--accent);
    text-decoration: underline;
    text-underline-offset: 2px;
  }}

  /* Article Footer (Pagination Prev/Next) */
  .article-footer {{
    margin-top: 60px;
    padding-top: 24px;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    justify-content: space-between;
    gap: 16px;
  }}

  .nav-card {{
    display: flex;
    flex-direction: column;
    padding: 14px 18px;
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    text-decoration: none;
    color: var(--text-primary);
    width: 48%;
    transition: all 0.15s ease;
  }}

  .nav-card:hover {{
    border-color: var(--accent);
    background: var(--bg-surface);
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  }}

  .nav-card-sub {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
    margin-bottom: 4px;
  }}

  .nav-card-title {{
    font-size: 14px;
    font-weight: 600;
    color: var(--accent-text);
  }}

  /* Right Sidebar ("On this page") */
  .toc-sidebar {{
    width: var(--toc-width);
    flex-shrink: 0;
    position: sticky;
    top: var(--header-height);
    height: calc(100vh - var(--header-height));
    overflow-y: auto;
    padding: 32px 16px 32px 20px;
  }}

  .toc-header {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 12px;
  }}

  .toc-list {{
    list-style: none;
  }}

  .toc-link {{
    display: block;
    font-size: 12.5px;
    color: var(--text-muted);
    text-decoration: none;
    padding: 4px 0;
    line-height: 1.4;
    transition: color 0.1s ease;
  }}

  .toc-link:hover {{
    color: var(--text-primary);
  }}

  .toc-h3 {{
    padding-left: 12px;
    font-size: 12px;
  }}

  /* Responsive Breakpoints */
  @media (max-width: 1200px) {{
    .toc-sidebar {{
      display: none;
    }}
  }}

  @media (max-width: 900px) {{
    .btn-mobile-nav {{
      display: inline-block;
    }}
    .sidebar-nav {{
      position: fixed;
      top: var(--header-height);
      left: calc(-1 * var(--sidebar-width));
      z-index: 100;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
      transition: left 0.25s ease;
    }}
    .sidebar-nav.open {{
      left: 0;
    }}
    .main-reader {{
      padding: 24px 20px 60px 20px;
    }}
    .brand-badge {{
      display: none;
    }}
  }}

  /* Print Styles */
  @media print {{
    .app-header, .sidebar-nav, .toc-sidebar, .article-footer {{
      display: none !important;
    }}
    .app-container, .main-reader {{
      display: block !important;
      padding: 0 !important;
      margin: 0 !important;
    }}
    .article-container {{
      max-width: 100% !important;
    }}
    .article-body h2, .article-body h3 {{
      page-break-after: avoid;
    }}
    pre, blockquote, table {{
      page-break-inside: avoid;
    }}
  }}
</style>
</head>
<body>

<!-- Header -->
<header class="app-header">
  <div class="header-left">
    <button class="btn-mobile-nav" onclick="toggleMobileSidebar()" aria-label="Toggle Navigation">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
    </button>
    <a href="#" class="header-brand">
      <div class="brand-logo">SP</div>
      <span class="brand-title">Siva Prasad Vajja</span>
      <span class="brand-badge">Product Engineering &amp; AI Compendium</span>
    </a>
  </div>

  <div class="header-actions">
    <a href="Siva_Prasad_Master_Product_AI_Guide.docx" class="action-btn" download title="Download Formatted Word Document">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
      <span>Download .docx</span>
    </a>

    <button class="action-btn action-btn-primary" onclick="window.print()" title="Print Current Chapter to PDF">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
      <span>Print / PDF</span>
    </button>

    <button class="action-btn" onclick="toggleTheme()" id="themeToggleBtn" aria-label="Toggle Theme">
      <svg id="themeIcon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
    </button>
  </div>
</header>

<div class="app-container">
  <!-- Left Sidebar Nav -->
  <aside class="sidebar-nav" id="sidebarNav">
    <div class="search-wrapper">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <input type="text" id="chapterSearch" class="search-input" placeholder="Search 41 chapters..." onkeyup="filterNav()">
    </div>

    <nav id="navTree">
      {left_sidebar_html}
    </nav>
  </aside>

  <!-- Main Reader -->
  <main class="main-reader">
    <article class="article-container">
      <div class="breadcrumb" id="readerBreadcrumb">
        <span>Compendium</span>
        <span>&rsaquo;</span>
        <span id="bcCategory">Core Java</span>
        <span>&rsaquo;</span>
        <span id="bcChapter">01 Core Java Advanced</span>
      </div>

      <header class="article-header">
        <div class="article-meta-tags">
          <span class="badge-category" id="metaCategory">Core Java</span>
          <span class="badge-time" id="metaReadTime">15 min read</span>
        </div>
        <h1 class="article-title" id="chapterTitle">Title</h1>
        <div class="article-source">
          <span>Source:</span>
          <code id="metaSource">Interview_Notes/01_Core_Java_Advanced.md</code>
          <a id="metaGhLink" href="#" target="_blank" class="source-link-btn" title="View formatted Markdown on GitHub">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
            <span>GitHub .md ↗</span>
          </a>
          <a id="metaSourceLink" href="#" target="_blank" class="source-link-btn" title="View raw static Markdown file">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            <span>Raw File ↗</span>
          </a>
        </div>
      </header>

      <div class="article-body" id="articleBody">
        <!-- Chapter Content Rendered dynamically -->
      </div>

      <nav class="article-footer">
        <a href="#" class="nav-card" id="prevCard" style="visibility: hidden;">
          <span class="nav-card-sub">&larr; Previous</span>
          <span class="nav-card-title" id="prevCardTitle">Previous Chapter</span>
        </a>
        <a href="#" class="nav-card" id="nextCard" style="visibility: hidden; text-align: right;">
          <span class="nav-card-sub">Next &rarr;</span>
          <span class="nav-card-title" id="nextCardTitle">Next Chapter</span>
        </a>
      </nav>
    </article>
  </main>

  <!-- Right TOC Sidebar -->
  <aside class="toc-sidebar">
    <div class="toc-header">On this page</div>
    <ul class="toc-list" id="tocList">
      <!-- Subheadings populated dynamically -->
    </ul>
  </aside>
</div>

<!-- Prism Code Highlighter Script -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>

<script>
// Data Store
const CHAPTERS = {chapters_json};

let currentChapterIndex = 0;

function renderChapter(index) {{
  if (index < 0 || index >= CHAPTERS.length) return;
  currentChapterIndex = index;
  const ch = CHAPTERS[index];

  // Update Breadcrumb
  document.getElementById('bcCategory').textContent = ch.category;
  document.getElementById('bcChapter').textContent = ch.title;

  // Update Meta
  document.getElementById('metaCategory').textContent = ch.category;
  document.getElementById('metaReadTime').textContent = ch.readTime;
  document.getElementById('chapterTitle').textContent = ch.title;
  
  const isRoadmap = (ch.num === "00" && ch.filename.includes("Roadmap"));
  const sourcePath = isRoadmap ? ch.filename : 'Interview_Notes/' + ch.filename;
  document.getElementById('metaSource').textContent = sourcePath;
  document.getElementById('metaSourceLink').href = sourcePath;
  document.getElementById('metaGhLink').href = 'https://github.com/PRASADsiva7482/Stack/blob/main/' + sourcePath;


  // Render Body
  const bodyEl = document.getElementById('articleBody');
  bodyEl.innerHTML = ch.html;

  // Make all links pointing to .md files fully clickable and interactive!
  bodyEl.querySelectorAll('a').forEach(a => {{
    const href = a.getAttribute('href');
    if (!href) return;

    if (href.endsWith('.md') || href.includes('.md#')) {{
      const [cleanHref, hash] = href.split('#');
      const parts = cleanHref.split('/');
      const targetFilename = parts[parts.length - 1];

      const targetIdx = CHAPTERS.findIndex(c => c.filename.toLowerCase() === targetFilename.toLowerCase());
      if (targetIdx !== -1) {{
        a.classList.add('doc-link-tag');
        a.setAttribute('title', 'Click to view Chapter ' + CHAPTERS[targetIdx].num + ' (' + CHAPTERS[targetIdx].title + ')');
        a.addEventListener('click', (e) => {{
          e.preventDefault();
          renderChapter(targetIdx);
          if (hash) {{
            setTimeout(() => {{
              const targetHeading = document.getElementById(hash);
              if (targetHeading) targetHeading.scrollIntoView({{ behavior: 'smooth' }});
            }}, 80);
          }}
        }});
      }} else {{
        if (!href.startsWith('Interview_Notes/') && !href.startsWith('http')) {{
          a.setAttribute('href', 'Interview_Notes/' + href);
        }}
        a.setAttribute('target', '_blank');
      }}
    }}
  }});


  // Wrap tables for responsive scrolling
  bodyEl.querySelectorAll('table').forEach(tbl => {{
    if (!tbl.parentElement.classList.contains('table-wrapper')) {{
      const wrapper = document.createElement('div');
      wrapper.className = 'table-wrapper';
      tbl.parentNode.insertBefore(wrapper, tbl);
      wrapper.appendChild(tbl);
    }}
  }});

  // Wrap Pre/Code with code-header and copy button
  bodyEl.querySelectorAll('pre').forEach(pre => {{
    if (!pre.parentElement.classList.contains('code-block-wrapper')) {{
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block-wrapper';
      
      const codeEl = pre.querySelector('code');
      let lang = 'code';
      if (codeEl) {{
        const classNames = codeEl.className.split(' ');
        classNames.forEach(cn => {{
          if (cn.startsWith('language-')) {{
            lang = cn.replace('language-', '').toUpperCase();
          }}
        }});
      }}

      const header = document.createElement('div');
      header.className = 'code-header';
      header.innerHTML = `<span>${{lang}}</span><button class="copy-btn" onclick="copySnippet(this)"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy</button>`;
      
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(header);
      wrapper.appendChild(pre);
    }}
  }});

  // Trigger Prism Highlighter
  Prism.highlightAllUnder(bodyEl);

  // Update Right TOC
  const tocList = document.getElementById('tocList');
  tocList.innerHTML = '';
  if (ch.subheadings && ch.subheadings.length > 0) {{
    ch.subheadings.forEach(sub => {{
      const li = document.createElement('li');
      li.className = sub.level === 3 ? 'toc-h3' : 'toc-h2';
      li.innerHTML = `<a href="#${{sub.id}}" class="toc-link">${{sub.title}}</a>`;
      tocList.appendChild(li);
    }});
  }} else {{
    tocList.innerHTML = '<li class="toc-link" style="color: var(--text-muted); font-size: 12px;">No sub-sections</li>';
  }}

  // Update Prev / Next Cards
  const prevCard = document.getElementById('prevCard');
  if (index > 0) {{
    prevCard.style.visibility = 'visible';
    const prevCh = CHAPTERS[index - 1];
    prevCard.href = '#' + prevCh.id;
    document.getElementById('prevCardTitle').textContent = prevCh.title;
  }} else {{
    prevCard.style.visibility = 'hidden';
  }}

  const nextCard = document.getElementById('nextCard');
  if (index < CHAPTERS.length - 1) {{
    nextCard.style.visibility = 'visible';
    const nextCh = CHAPTERS[index + 1];
    nextCard.href = '#' + nextCh.id;
    document.getElementById('nextCardTitle').textContent = nextCh.title;
  }} else {{
    nextCard.style.visibility = 'hidden';
  }}

  // Update Active Link in Sidebar
  document.querySelectorAll('.nav-item').forEach(link => {{
    if (link.getAttribute('data-id') === ch.id) {{
      link.classList.add('active');
      link.scrollIntoView({{ block: 'nearest' }});
    }} else {{
      link.classList.remove('active');
    }}
  }});

  // Scroll to top
  window.scrollTo({{ top: 0, behavior: 'instant' }});

  // Update URL Hash without reload
  if (window.location.hash !== '#' + ch.id) {{
    history.replaceState(null, null, '#' + ch.id);
  }}
}}

// Copy snippet helper
function copySnippet(btn) {{
  const code = btn.closest('.code-block-wrapper').querySelector('code').innerText;
  navigator.clipboard.writeText(code).then(() => {{
    btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;
    setTimeout(() => {{
      btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg> Copy`;
    }}, 2000);
  }});
}}

// Search / Filter Sidebar
function filterNav() {{
  const q = document.getElementById('chapterSearch').value.toLowerCase();
  document.querySelectorAll('.nav-group').forEach(grp => {{
    let groupHasMatch = false;
    grp.querySelectorAll('li').forEach(li => {{
      const text = li.textContent.toLowerCase();
      if (text.includes(q)) {{
        li.style.display = '';
        groupHasMatch = true;
      }} else {{
        li.style.display = 'none';
      }}
    }});
    grp.style.display = groupHasMatch ? '' : 'none';
  }});
}}

// Mobile Drawer
function toggleMobileSidebar() {{
  document.getElementById('sidebarNav').classList.toggle('open');
}}

// Theme Switcher
function toggleTheme() {{
  const html = document.documentElement;
  const target = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', target);
  localStorage.setItem('doc-theme', target);
}}

// Initial load
window.addEventListener('DOMContentLoaded', () => {{
  // Theme init
  const savedTheme = localStorage.getItem('doc-theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);

  // Sidebar link clicks
  document.querySelectorAll('.nav-item').forEach((item, idx) => {{
    item.addEventListener('click', (e) => {{
      e.preventDefault();
      const id = item.getAttribute('data-id');
      const foundIdx = CHAPTERS.findIndex(c => c.id === id);
      if (foundIdx !== -1) {{
        renderChapter(foundIdx);
        if (window.innerWidth <= 900) {{
          document.getElementById('sidebarNav').classList.remove('open');
        }}
      }}
    }});
  }});

  // Prev / Next click handlers
  document.getElementById('prevCard').addEventListener('click', (e) => {{
    e.preventDefault();
    if (currentChapterIndex > 0) renderChapter(currentChapterIndex - 1);
  }});

  document.getElementById('nextCard').addEventListener('click', (e) => {{
    e.preventDefault();
    if (currentChapterIndex < CHAPTERS.length - 1) renderChapter(currentChapterIndex + 1);
  }});

  // Route by hash or default to first
  const hash = window.location.hash.replace('#', '');
  const hashIdx = CHAPTERS.findIndex(c => c.id === hash);
  if (hashIdx !== -1) {{
    renderChapter(hashIdx);
  }} else {{
    renderChapter(0);
  }}
}});

window.addEventListener('hashchange', () => {{
  const hash = window.location.hash.replace('#', '');
  const hashIdx = CHAPTERS.findIndex(c => c.id === hash);
  if (hashIdx !== -1 && hashIdx !== currentChapterIndex) {{
    renderChapter(hashIdx);
  }}
}});
</script>
</body>
</html>
"""

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Generated clean SPA Portal: {INDEX_HTML}")


# ==============================================================================
# 3. GENERATE INDUSTRY-STANDARD WORD DOCUMENT (.DOCX)
# ==============================================================================
print("Generating Industry-Standard Executive Word (.docx) Document...")

doc = Document()

# Configure Margins (0.75 in for professional publications)
for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    
    # Configure running header and footer
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run("SIVA PRASAD VAJJA  |  PRODUCT ENGINEERING & AI COMPENDIUM")
    hr.font.name = 'Segoe UI'
    hr.font.size = Pt(8)
    hr.font.color.rgb = RGBColor(148, 163, 184)
    
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    fr = fp.add_run("Confidential Reference  •  Prepared for Tier-1 Product Engineering Interviews")
    fr.font.name = 'Segoe UI'
    fr.font.size = Pt(8)
    fr.font.color.rgb = RGBColor(148, 163, 184)

# Set base Normal style font
style_normal = doc.styles['Normal']
font = style_normal.font
font.name = 'Segoe UI'
font.size = Pt(10)
font.color.rgb = RGBColor(15, 23, 42) # Slate-900

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_formatted_runs(paragraph, text, base_italic=False):
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
            run.font.color.rgb = RGBColor(185, 28, 28)
            if base_italic: run.italic = True
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            m = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if m:
                run = paragraph.add_run(m.group(1))
                run.font.color.rgb = RGBColor(2, 132, 199)
                run.underline = True
            else:
                run = paragraph.add_run(part)
        else:
            run = paragraph.add_run(part)
            if base_italic: run.italic = True

# --- EXECUTIVE COVER PAGE ---
cover_top = doc.add_paragraph()
cover_top.paragraph_format.space_before = Pt(80)
cover_top.paragraph_format.space_after = Pt(4)
r_badge = cover_top.add_run("ENTERPRISE REFERENCE SPECIFICATION  |  TIER-1 PRODUCT ROLES")
r_badge.bold = True
r_badge.font.size = Pt(9.5)
r_badge.font.color.rgb = RGBColor(2, 132, 199)

title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(6)
title_p.paragraph_format.space_after = Pt(12)
r_title = title_p.add_run("Product-Company Career Transition\n& AI Engineering Master Compendium")
r_title.bold = True
r_title.font.size = Pt(24)
r_title.font.name = 'Segoe UI Semibold'
r_title.font.color.rgb = RGBColor(15, 23, 42)

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(36)
r_sub = sub_p.add_run("Siva Prasad Vajja  •  Senior Software Engineer\nJava 17  |  Spring Boot  |  Microservices  |  Distributed Systems  |  Spring AI")
r_sub.font.size = Pt(11)
r_sub.font.color.rgb = RGBColor(71, 85, 105)

# Document Control Table
ctrl_table = doc.add_table(rows=5, cols=2)
ctrl_table.style = 'Table Grid'
ctrl_data = [
    ("Target Profile", "Senior Product Software Engineer (B2B SaaS / Distributed Platforms)"),
    ("Current Focus", "Java 17, Spring Boot, Microservices, Camunda, SQL, Kafka, Redis, Spring AI"),
    ("Scope", "41 Technical Chapters (JVM, Concurrency, Systems Architecture, Applied AI)"),
    ("Source Authority", "Curated from verified production experience and evidence tracking"),
    ("Distribution", "Internal Study Compendium & Portfolio Reference (Confidential)")
]

for row_idx, (k, v) in enumerate(ctrl_data):
    r_cells = ctrl_table.rows[row_idx].cells
    r_cells[0].text = k
    r_cells[1].text = v
    set_cell_background(r_cells[0], "F8FAFC")
    set_cell_margins(r_cells[0], top=60, bottom=60, left=100, right=100)
    set_cell_margins(r_cells[1], top=60, bottom=60, left=100, right=100)
    r_cells[0].paragraphs[0].runs[0].bold = True
    r_cells[0].paragraphs[0].runs[0].font.size = Pt(9)
    r_cells[1].paragraphs[0].runs[0].font.size = Pt(9)

doc.add_page_break()

# --- TABLE OF CONTENTS ---
toc_head = doc.add_paragraph()
toc_head.paragraph_format.space_before = Pt(12)
toc_head.paragraph_format.space_after = Pt(12)
r_th = toc_head.add_run("Document Index & Study Progression")
r_th.bold = True
r_th.font.size = Pt(16)
r_th.font.color.rgb = RGBColor(15, 23, 42)

toc_tbl = doc.add_table(rows=1, cols=3)
toc_tbl.style = 'Table Grid'
h_cells = toc_tbl.rows[0].cells
h_cells[0].text = "No."
h_cells[1].text = "Curriculum Section & Chapter Title"
h_cells[2].text = "Domain Group"
for c in h_cells:
    set_cell_background(c, "F1F5F9")
    set_cell_margins(c, top=60, bottom=60, left=100, right=100)
    p = c.paragraphs[0]
    p.runs[0].bold = True
    p.runs[0].font.size = Pt(9)

for ch in chapters:
    row_cells = toc_tbl.add_row().cells
    row_cells[0].text = ch["num"]
    row_cells[1].text = re.sub(r'[*_`]', '', ch["title"])
    row_cells[2].text = ch["category"]
    for c in row_cells:
        set_cell_margins(c, top=40, bottom=40, left=80, right=80)
        p = c.paragraphs[0]
        if p.runs:
            p.runs[0].font.size = Pt(8.5)

# --- PROCESS CHAPTERS ---
for ch in chapters:
    doc.add_page_break()
    
    # Chapter Header Box
    h_box = doc.add_paragraph()
    h_box.paragraph_format.space_before = Pt(8)
    h_box.paragraph_format.space_after = Pt(2)
    h_box.paragraph_format.keep_with_next = True
    r_num = h_box.add_run(f"CHAPTER {ch['num']}  |  {ch['category'].upper()}")
    r_num.bold = True
    r_num.font.size = Pt(9)
    r_num.font.color.rgb = RGBColor(2, 132, 199)
    
    t_p = doc.add_paragraph()
    t_p.paragraph_format.space_before = Pt(2)
    t_p.paragraph_format.space_after = Pt(4)
    t_p.paragraph_format.keep_with_next = True
    r_t = t_p.add_run(re.sub(r'[*_`]', '', ch['title']))
    r_t.bold = True
    r_t.font.size = Pt(16)
    r_t.font.name = 'Segoe UI Semibold'
    r_t.font.color.rgb = RGBColor(15, 23, 42)
    
    s_p = doc.add_paragraph()
    s_p.paragraph_format.space_after = Pt(12)
    r_s = s_p.add_run(f"Source Specification: Interview_Notes/{ch['filename']}")
    r_s.font.italic = True
    r_s.font.size = Pt(8)
    r_s.font.color.rgb = RGBColor(148, 163, 184)
    
    lines = ch['content'].split('\n')
    i = 0
    n = len(lines)
    
    if n > 0 and lines[0].startswith('# '):
        i = 1
        
    while i < n:
        line = lines[i]
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue
            
        if stripped in ('---', '***', '___'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run('—' * 35)
            r.font.color.rgb = RGBColor(228, 228, 231)
            i += 1
            continue
            
        if line.startswith('# ') and not line.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line[2:].strip())
            r.bold = True
            r.font.size = Pt(14)
            r.font.name = 'Segoe UI Semibold'
            r.font.color.rgb = RGBColor(15, 23, 42)
            i += 1
            continue
            
        if line.startswith('## ') and not line.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(11)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line[3:].strip())
            r.bold = True
            r.font.size = Pt(12)
            r.font.name = 'Segoe UI Semibold'
            r.font.color.rgb = RGBColor(39, 39, 42)
            i += 1
            continue
            
        if line.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(line[4:].strip())
            r.bold = True
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(82, 82, 91)
            i += 1
            continue
            
        # Table
        if '|' in stripped and i + 1 < n and '|---' in lines[i + 1]:
            table_lines = []
            while i < n and '|' in lines[i].strip():
                table_lines.append(lines[i].strip())
                i += 1
                
            if len(table_lines) >= 3:
                headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
                data_rows = []
                for t_row in table_lines[2:]:
                    cells = [c.strip() for c in t_row.split('|')[1:-1]]
                    data_rows.append(cells)
                
                cols_count = len(headers)
                t = doc.add_table(rows=1, cols=cols_count)
                t.style = 'Table Grid'
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                
                hdr_cells = t.rows[0].cells
                for c_idx, h_text in enumerate(headers):
                    if c_idx < len(hdr_cells):
                        hdr_cells[c_idx].text = h_text
                        set_cell_background(hdr_cells[c_idx], "F4F4F5")
                        set_cell_margins(hdr_cells[c_idx], top=50, bottom=50, left=80, right=80)
                        p = hdr_cells[c_idx].paragraphs[0]
                        for r in p.runs:
                            r.bold = True
                            r.font.size = Pt(8.5)
                            r.font.color.rgb = RGBColor(15, 23, 42)
                                
                for r_idx, r_data in enumerate(data_rows):
                    row_cells = t.add_row().cells
                    for c_idx, cell_value in enumerate(r_data):
                        if c_idx < len(row_cells):
                            p = row_cells[c_idx].paragraphs[0]
                            add_formatted_runs(p, cell_value)
                            p.paragraph_format.space_before = Pt(1)
                            p.paragraph_format.space_after = Pt(1)
                            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=80, right=80)
                            if p.runs:
                                for r in p.runs: r.font.size = Pt(8.5)
                            if r_idx % 2 == 1:
                                set_cell_background(row_cells[c_idx], "FAFAFA")
                
                p_after = doc.add_paragraph()
                p_after.paragraph_format.space_before = Pt(3)
                p_after.paragraph_format.space_after = Pt(3)
            continue
            
        # Blockquote
        if line.startswith('>'):
            quote_lines = []
            while i < n and (lines[i].startswith('>') or (lines[i].strip() and quote_lines and not lines[i].startswith('#'))):
                q_l = lines[i]
                if q_l.startswith('>'): q_l = q_l[1:].strip()
                else: q_l = q_l.strip()
                if q_l: quote_lines.append(q_l)
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.right_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(5)
            add_formatted_runs(p, " ".join(quote_lines), base_italic=True)
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
            
        # Code block
        if line.startswith('```'):
            i += 1
            code_lines = []
            while i < n and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < n and lines[i].startswith('```'):
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(5)
            r = p.add_run("\n".join(code_lines))
            r.font.name = 'Consolas'
            r.font.size = Pt(8)
            r.font.color.rgb = RGBColor(39, 39, 42)
            continue
            
        # Standard paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        add_formatted_runs(p, stripped)
        i += 1

print(f"Saving Executive Document: {DOCX_OUTPUT}...")
doc.save(DOCX_OUTPUT)
print(f"Saved: {DOCX_OUTPUT}")
print("Industry-standard build complete!")
