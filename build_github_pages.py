import os
import re
import markdown
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"d:\Learning\Stack"
INTERVIEW_DIR = os.path.join(BASE_DIR, "Interview_Notes")
ROADMAP_MD = os.path.join(BASE_DIR, "Siva_Prasad_Product_Company_AI_Roadmap.md")

INDEX_HTML = os.path.join(BASE_DIR, "index.html")
MASTER_HTML = os.path.join(BASE_DIR, "Siva_Prasad_Master_Product_AI_Guide.html")
MASTER_DOCX = os.path.join(BASE_DIR, "Siva_Prasad_Master_Product_AI_Guide.docx")

# 1. Discover all files
files_in_notes = sorted([f for f in os.listdir(INTERVIEW_DIR) if f.endswith('.md')])

chapters = []

# Chapter 0: Master Career Roadmap
with open(ROADMAP_MD, "r", encoding="utf-8") as f:
    roadmap_content = f.read()

chapters.append({
    "id": "chap-00-roadmap",
    "num": "00",
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
    
    slug = "chap-" + re.sub(r'[^a-zA-Z0-9_\-]+', '-', f_name.lower().replace('.md', ''))
    chapters.append({
        "id": slug,
        "num": f_name[:2] if f_name[:2].isdigit() else "IDX",
        "filename": f_name,
        "title": title,
        "category": categorize(f_name),
        "content": content
    })

print(f"Total chapters: {len(chapters)}")

# ==============================================================================
# BUILD GITHUB PAGES `index.html`
# ==============================================================================
print("Generating GitHub Pages index.html...")

categories = {}
for ch in chapters:
    categories.setdefault(ch["category"], []).append(ch)

sidebar_nav_html = []
for cat, ch_list in categories.items():
    sidebar_nav_html.append(f'<div class="nav-category"><h4>{cat}</h4><ul>')
    for ch in ch_list:
        clean_title = re.sub(r'[*_`]', '', ch["title"])
        sidebar_nav_html.append(f'''<li>
          <a href="#{ch["id"]}" class="nav-link" data-id="{ch["id"]}">
            <span class="badge">{ch["num"]}</span>
            <span class="nav-text">{clean_title}</span>
          </a>
        </li>''')
    sidebar_nav_html.append('</ul></div>')

sidebar_html = "\n".join(sidebar_nav_html)

# Markdown parser
md_converter = markdown.Markdown(extensions=['extra', 'tables', 'toc', 'sane_lists'])

chapters_rendered = []
for ch in chapters:
    raw_md = ch["content"]
    rendered = md_converter.reset().convert(raw_md)
    
    chapter_block = f"""
    <section class="chapter-container" id="{ch['id']}" data-title="{re.sub(r'[*_`]', '', ch['title'])}">
      <div class="chapter-header">
        <div class="chapter-tags">
          <span class="chapter-category-tag">{ch['category']}</span>
          <span class="chapter-number-tag">Section {ch['num']}</span>
        </div>
        <h2 class="chapter-title">{ch['title']}</h2>
        <div class="chapter-meta">
          <span>📄 Source: <code>Interview_Notes/{ch['filename']}</code></span>
        </div>
      </div>
      <div class="chapter-body">
        {rendered}
      </div>
    </section>
    """
    chapters_rendered.append(chapter_block)

all_chapters_html = "\n".join(chapters_rendered)

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Siva Prasad Vajja — Product Engineering & AI Interview Compendium</title>
<meta name="description" content="Complete 41-Chapter Study Guide & Roadmap for Senior Product Engineering, Distributed Systems, Cloud Architecture, and Applied AI.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --font-main: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', Consolas, Monaco, monospace;
    
    --bg-page: #f8fafc;
    --bg-surface: #ffffff;
    --bg-surface-elevated: #ffffff;
    --bg-hover: #f1f5f9;
    --border-color: #e2e8f0;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    
    --primary: #1e40af;
    --primary-light: #eff6ff;
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    
    --code-bg: #0f172a;
    --code-text: #f8fafc;
    --inline-code-bg: #f1f5f9;
    --inline-code-color: #b91c1c;
    
    --callout-bg: #f0fdf4;
    --callout-border: #16a34a;
    --table-stripe: #f8fafc;
    --badge-bg: #e2e8f0;
    --badge-color: #475569;
    --active-link-bg: #e0e7ff;
    --active-link-color: #1e40af;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  }}

  [data-theme="dark"] {{
    --bg-page: #0b0f19;
    --bg-surface: #111827;
    --bg-surface-elevated: #1f2937;
    --bg-hover: #1f2937;
    --border-color: #374151;
    --text-primary: #f9fafb;
    --text-secondary: #cbd5e1;
    --text-muted: #64748b;
    
    --primary: #60a5fa;
    --primary-light: #1e293b;
    --accent: #3b82f6;
    --accent-hover: #60a5fa;
    
    --code-bg: #030712;
    --code-text: #f9fafb;
    --inline-code-bg: #1f2937;
    --inline-code-color: #f87171;
    
    --callout-bg: #062817;
    --callout-border: #22c55e;
    --table-stripe: #172033;
    --badge-bg: #1e293b;
    --badge-color: #94a3b8;
    --active-link-bg: #1e3a8a;
    --active-link-color: #93c5fd;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.5);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
  }}

  * {{
    box-sizing: border-box;
  }}

  html {{
    scroll-behavior: smooth;
  }}

  body {{
    font-family: var(--font-main);
    color: var(--text-primary);
    background-color: var(--bg-page);
    line-height: 1.65;
    margin: 0;
    padding: 0;
    font-size: 15px;
    transition: background-color 0.2s, color 0.2s;
  }}

  /* Top Navigation Bar */
  .top-navbar {{
    position: sticky;
    top: 0;
    z-index: 1000;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-color);
    padding: 10px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(8px);
  }}

  .nav-left {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .menu-toggle-btn {{
    display: none;
    background: transparent;
    border: 1px solid var(--border-color);
    padding: 6px 10px;
    border-radius: 6px;
    color: var(--text-primary);
    cursor: pointer;
    font-size: 16px;
  }}

  .brand-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--primary);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .brand-sub {{
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: normal;
  }}

  .nav-actions {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.15s ease;
    border: none;
  }}

  .btn-primary {{
    background: var(--accent);
    color: #ffffff;
  }}
  .btn-primary:hover {{
    background: var(--accent-hover);
    color: #ffffff;
  }}

  .btn-outline {{
    background: var(--bg-surface);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }}
  .btn-outline:hover {{
    background: var(--bg-hover);
  }}

  .theme-toggle-btn {{
    background: var(--bg-hover);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 7px 11px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
  }}

  /* Layout Structure */
  .app-layout {{
    display: flex;
    max-width: 1650px;
    margin: 0 auto;
  }}

  /* Sidebar Navigation */
  .sidebar {{
    width: 360px;
    flex-shrink: 0;
    position: sticky;
    top: 56px;
    height: calc(100vh - 56px);
    overflow-y: auto;
    background: var(--bg-surface);
    border-right: 1px solid var(--border-color);
    padding: 20px 16px;
  }}

  .sidebar-search {{
    margin-bottom: 18px;
  }}

  .sidebar-search input {{
    width: 100%;
    padding: 9px 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: 13px;
    outline: none;
    background: var(--bg-page);
    color: var(--text-primary);
    transition: border-color 0.2s;
  }}
  .sidebar-search input:focus {{
    border-color: var(--accent);
    background: var(--bg-surface);
  }}

  .nav-category {{
    margin-bottom: 22px;
  }}

  .nav-category h4 {{
    margin: 0 0 8px 6px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
    font-weight: 700;
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
    color: var(--text-secondary);
    text-decoration: none;
    line-height: 1.35;
    transition: all 0.12s;
  }}

  .nav-link:hover {{
    background: var(--bg-hover);
    color: var(--accent);
  }}

  .nav-link.active {{
    background: var(--active-link-bg);
    color: var(--active-link-color);
    font-weight: 600;
  }}

  .badge {{
    display: inline-block;
    padding: 2px 6px;
    background: var(--badge-bg);
    color: var(--badge-color);
    border-radius: 4px;
    font-size: 10px;
    font-family: var(--font-mono);
    font-weight: 600;
    flex-shrink: 0;
  }}

  .nav-text {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  /* Main Content Area */
  .main-content {{
    flex: 1;
    min-width: 0;
    padding: 36px 56px;
  }}

  /* Chapter Card Container */
  .chapter-container {{
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 44px 50px;
    margin-bottom: 40px;
    box-shadow: var(--shadow-sm);
  }}

  .chapter-header {{
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 20px;
    margin-bottom: 28px;
  }}

  .chapter-tags {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }}

  .chapter-category-tag {{
    display: inline-block;
    padding: 3px 10px;
    background: var(--primary-light);
    color: var(--primary);
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
  }}

  .chapter-number-tag {{
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
  }}

  .chapter-title {{
    margin: 6px 0 8px 0;
    font-size: 2rem;
    color: var(--primary);
    line-height: 1.25;
    font-weight: 700;
  }}

  .chapter-meta {{
    font-size: 12px;
    color: var(--text-muted);
  }}

  /* Typography inside chapters */
  .chapter-body h1 {{
    display: none; /* Already rendered in chapter header */
  }}

  .chapter-body h2 {{
    color: var(--text-primary);
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 6px;
    margin-top: 36px;
    margin-bottom: 16px;
    font-size: 1.4rem;
    font-weight: 600;
  }}

  .chapter-body h3 {{
    color: var(--text-primary);
    margin-top: 24px;
    margin-bottom: 10px;
    font-size: 1.15rem;
    font-weight: 600;
  }}

  .chapter-body h4 {{
    color: var(--text-secondary);
    margin-top: 18px;
    margin-bottom: 8px;
    font-size: 1.02rem;
  }}

  .chapter-body p, .chapter-body ul, .chapter-body ol {{
    margin-bottom: 14px;
    color: var(--text-secondary);
  }}

  .chapter-body ul, .chapter-body ol {{
    padding-left: 24px;
  }}

  .chapter-body li {{
    margin-bottom: 5px;
  }}

  .chapter-body strong {{
    color: var(--text-primary);
  }}

  /* Callouts / Blockquotes */
  blockquote {{
    margin: 18px 0;
    padding: 14px 18px;
    background: var(--callout-bg);
    border-left: 4px solid var(--callout-border);
    border-radius: 0 8px 8px 0;
    color: var(--text-primary);
  }}

  /* Code */
  code {{
    background: var(--inline-code-bg);
    color: var(--inline-code-color);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.88em;
  }}

  pre {{
    background: var(--code-bg);
    color: var(--code-text);
    padding: 16px 20px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 0.88em;
    line-height: 1.5;
    font-family: var(--font-mono);
  }}

  pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 24px 0;
    font-size: 13.5px;
  }}

  th, td {{
    padding: 10px 14px;
    border: 1px solid var(--border-color);
    text-align: left;
    vertical-align: top;
  }}

  th {{
    background-color: var(--bg-hover);
    color: var(--text-primary);
    font-weight: 600;
  }}

  tr:nth-child(even) td {{
    background-color: var(--table-stripe);
  }}

  a {{
    color: var(--accent);
    text-decoration: underline;
  }}

  /* Floating Back to Top Button */
  .back-to-top {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: var(--accent);
    color: white;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    box-shadow: var(--shadow-md);
    cursor: pointer;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    z-index: 900;
    border: none;
    font-size: 18px;
  }}

  .back-to-top.visible {{
    opacity: 1;
    visibility: visible;
  }}

  /* Responsive / Mobile */
  @media (max-width: 1024px) {{
    .menu-toggle-btn {{
      display: inline-block;
    }}
    .sidebar {{
      position: fixed;
      top: 56px;
      left: -360px;
      z-index: 999;
      box-shadow: var(--shadow-md);
      transition: left 0.25s ease;
    }}
    .sidebar.open {{
      left: 0;
    }}
    .main-content {{
      padding: 24px 20px;
    }}
    .chapter-container {{
      padding: 24px 20px;
    }}
    .brand-sub {{
      display: none;
    }}
  }}

  /* PRINT STYLES */
  @media print {{
    .top-navbar, .sidebar, .back-to-top, .menu-toggle-btn {{
      display: none !important;
    }}
    .app-layout {{
      display: block !important;
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

<header class="top-navbar">
  <div class="nav-left">
    <button class="menu-toggle-btn" onclick="toggleSidebar()">☰</button>
    <a href="#" class="brand-title">
      <span>📘</span>
      <span>Siva Prasad Vajja</span>
    </a>
    <span class="brand-sub">Product Engineering & AI Interview Compendium</span>
  </div>

  <div class="nav-actions">
    <a href="Siva_Prasad_Master_Product_AI_Guide.docx" class="btn btn-outline" download title="Download Full Word Document">
      📥 Download .docx
    </a>
    <button class="btn btn-primary" onclick="window.print()" title="Print or Save as PDF">
      🖨️ Print / PDF
    </button>
    <button class="theme-toggle-btn" onclick="toggleTheme()" id="themeBtn" title="Toggle Dark/Light Mode">
      🌙
    </button>
  </div>
</header>

<div class="app-layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-search">
      <input type="text" id="topicSearch" placeholder="🔍 Search 41 chapters..." onkeyup="filterTopics()">
    </div>
    <nav id="sidebarNav">
      {sidebar_html}
    </nav>
  </aside>

  <main class="main-content">
    {all_chapters_html}
  </main>
</div>

<button class="back-to-top" id="backToTop" onclick="scrollToTop()">↑</button>

<script>
// Sidebar Toggle for Mobile
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('open');
}}

// Filter Topics in Sidebar
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

// Active Chapter Highlight on Scroll
const chaptersList = document.querySelectorAll('.chapter-container');
const navLinks = document.querySelectorAll('.nav-link');

window.addEventListener('scroll', () => {{
  let fromTop = window.scrollY + 100;
  let currentChapterId = "";

  chaptersList.forEach(chapter => {{
    if (chapter.offsetTop <= fromTop) {{
      currentChapterId = chapter.getAttribute('id');
    }}
  }});

  navLinks.forEach(link => {{
    link.classList.remove('active');
    if (link.getAttribute('data-id') === currentChapterId) {{
      link.classList.add('active');
    }}
  }});

  // Back to top button visibility
  const backToTop = document.getElementById('backToTop');
  if (window.scrollY > 400) {{
    backToTop.classList.add('visible');
  }} else {{
    backToTop.classList.remove('visible');
  }}
}});

function scrollToTop() {{
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

// Dark / Light Theme
function toggleTheme() {{
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const target = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', target);
  document.getElementById('themeBtn').textContent = target === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('theme', target);
}}

// Init theme from storage
(function() {{
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  document.getElementById('themeBtn').textContent = saved === 'dark' ? '☀️' : '🌙';
}})();
</script>

</body>
</html>
"""

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Generated GitHub Pages root index: {INDEX_HTML}")

# Also copy to MASTER_HTML
with open(MASTER_HTML, "w", encoding="utf-8") as f:
    f.write(html_template)
print(f"Updated: {MASTER_HTML}")

# ==============================================================================
# CREATE .nojekyll FILE FOR GITHUB PAGES
# ==============================================================================
NOJEKYLL_PATH = os.path.join(BASE_DIR, ".nojekyll")
with open(NOJEKYLL_PATH, "w", encoding="utf-8") as f:
    f.write("")
print(f"Created: {NOJEKYLL_PATH}")

print("GitHub Pages build complete!")
