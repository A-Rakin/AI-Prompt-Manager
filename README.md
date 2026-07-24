# PromptForge 🚀
> **Modern AI Prompt Management Platform** built with Flask, SQLAlchemy, Bootstrap 5, Chart.js, and Notion/Linear-inspired dark glassmorphism UI.

---

## 🌟 Features Overview

- **Notion & Linear Inspired Interface**: Dark glassmorphic aesthetic (`#0F172A` deep slate navy background, `#1E293B` cards, `#6366F1` indigo accent, floating sidebar, soft glow shadows).
- **Authentication & User Profiles**: Account registration, secure password hashing (PBKDF2/SHA256), session management ("Remember Me"), profile bio customization, and password updates.
- **Productivity Dashboard**:
  - Total Prompts & Favorites Counter
  - Category statistics & Top Used Category detector
  - Recent Prompts grid
  - Recently Copied list
  - Real-time Activity Timeline feed
  - Weekly Copy Statistics
- **Full Prompt Management (CRUD)**:
  - Create, Edit, View, Soft Delete (Archive), and Hard Delete prompts.
  - Pin prompts to top of library views.
  - Mark prompts as favorites.
  - Duplicate prompts with one click.
  - 1-Click Clipboard Copying with live copy count tracking and copy history velocity.
  - Export prompts as JSON or CSV.
  - Import prompts from JSON files.
- **Advanced Multi-Criteria Live Search & Filters**:
  - Filter by Title, Content, Tags, Categories, AI Platforms (ChatGPT, Claude, Gemini, Copilot, Grok, Midjourney, Stable Diffusion), Language, and Complexity Level.
  - Live client-side instant search without reloading the page.
- **Folder Collections & Drag-and-Drop**:
  - Group prompts into custom folder collections (e.g. Work, Personal, University, Research).
  - Drag and drop prompt cards onto collection dropzones for quick sorting.
- **Productivity Analytics & Charts**:
  - Interactive Chart.js charts: Prompts created per month, platform usage doughnut chart, category breakdown bar chart, favorites ratio, and weekly copy velocity.
- **RESTful API (v1)**:
  - Endpoints at `/api/v1/` returning JSON representations of prompts, tags, and stats for browser extension or mobile client integrations.

---

## 🏗️ Technology Stack

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Werkzeug, SQLite (Development), PostgreSQL ready (Production).
- **Frontend**: HTML5, CSS3 (Vanilla CSS variables), Bootstrap 5, Font Awesome, Chart.js, SweetAlert2, AOS (Animate On Scroll).

---

## ⚙️ Installation & Local Setup

### 1. Clone or Open Project Directory
```bash
cd "d:/ai prompt manager"
```

### 2. Create & Activate Virtual Environment
```bash
# On Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python run.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/prompts` | `GET` | Retrieve paginated active prompts in JSON format |
| `/api/v1/prompts/<id>` | `GET` | Retrieve single prompt details by ID |
| `/api/v1/prompts/<id>/copy` | `POST` | Increment copy counter and record copy event |
| `/api/v1/tags` | `GET` | List user's tags for search autocompletion |
| `/api/v1/stats` | `GET` | Summary statistics of active/favorite/archived prompts |


<img width="1365" height="646" alt="image" src="https://github.com/user-attachments/assets/3e559e42-cf46-4f88-92f6-1aaf849cfaec" />
<img width="1360" height="640" alt="image" src="https://github.com/user-attachments/assets/9f517a77-16e0-4675-8524-142877fc5355" />
<img width="1349" height="643" alt="image" src="https://github.com/user-attachments/assets/6d513895-8fc2-41e7-9bc7-118626be5696" />
<img width="1365" height="691" alt="image" src="https://github.com/user-attachments/assets/db74d93f-bc2b-4235-8cd2-8f1757defc9d" />


