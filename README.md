# Siva Prasad Vajja — Product Company & AI Engineering Master Compendium

> Complete 41-chapter technical study guide, system design blueprints, JVM & framework internals, and applied AI engineering reference for Senior Product Engineer interview preparation.

---

## 🌐 Live Web Documentation & GitHub Pages

Once pushed to your GitHub repository, this documentation is immediately viewable online via **GitHub Pages**:

`https://<your-github-username>.github.io/<repository-name>/`

### Site Features
- **41 In-Depth Chapters**: From Java 17, Spring Boot, Kafka, Redis, and Distributed Systems to Spring AI, RAG, and MCP.
- **Fast Live Search**: Filter through all 41 chapters in milliseconds.
- **Active Scroll Tracking**: Sidebar automatically highlights your position as you read.
- **One-Click Word Download**: Direct link to download the complete formatted Word document (`.docx`).
- **One-Click PDF/Print**: High-contrast, clean printable view (`Ctrl + P` or top bar button) with auto-hidden sidebars and proper page margins.
- **Dark / Light Theme Toggle**: Persistent theme switcher for comfortable reading.
- **Mobile Responsive**: Off-canvas slideout navigation drawer for smartphones and tablets.

---

## 🚀 How to Publish to GitHub Pages

### Step 1: Initialize Git and Commit
Open PowerShell or your terminal in this directory (`d:\Learning\Stack`) and run:

```bash
# Initialize git repository
git init

# Add all files (ignoring .venv)
git add .

# Initial commit
git commit -m "feat: complete master interview compendium with GitHub Pages support"
```

### Step 2: Link to Your GitHub Repository
1. Go to [GitHub.com](https://github.com) and create a **New Repository** (e.g., `product-ai-compendium`).
2. Run the following commands in your terminal:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### Step 3: Enable GitHub Pages in Repository Settings
1. On GitHub, navigate to your repository.
2. Click on **Settings** $\rightarrow$ **Pages** (in the left sidebar).
3. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Select `main` branch and `/ (root)` folder.
4. Click **Save**.

Your documentation portal will be live in ~60 seconds at `https://<your-username>.github.io/<your-repo-name>/`!

---

## 🛠️ How to Update and Recompile Locally

Whenever you edit or add notes in `Interview_Notes/` or update `Siva_Prasad_Product_Company_AI_Roadmap.md`, simply run:

```powershell
# Rebuilds index.html and both master HTML & DOCX files
.venv\Scripts\python build_github_pages.py
```

Then commit and push:
```bash
git add .
git commit -m "docs: update study notes"
git push
```
GitHub Pages will automatically deploy the latest changes.
