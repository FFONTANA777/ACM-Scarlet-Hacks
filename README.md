# 🐾 Tamagotchi Pet Health App

A web app that gamifies personal health tracking through a Tamagotchi-style virtual pet — your pet thrives when you do. Designed as a morning check-in app, not a 24/7 logging tool.

## Tech Stack
- **Frontend:** React + Vite → deployed on Vercel
- **Backend:** FastAPI (Python) → deployed on Railway or Render
- **Database:** Supabase (Postgres + Auth)
- **AI:** GPT-4o Vision → Nutritionix API (calories), Claude/GPT (pet mood + message)
- **ML:** PyTorch (health score model)
- **Health Data:** Google Fit API

## General Structure
```
ACM-SCARLET-HACKS/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CheckIn.jsx       # morning check-in form
│   │   │   ├── Pet.jsx           # pet display + state
│   │   │   └── Dashboard.jsx     # wraps pet + check-in
│   │   ├── pages/
│   │   │   ├── Login.jsx         # signup/login page
│   │   │   └── Dashboard.jsx     # main app page (protected)
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py                   # FastAPI entry point
│   ├── requirements.txt
│   ├── .python-version
│   └── .gitignore
├── .vscode/
│   └── settings.json             # Shared VSCode interpreter path (Windows)
├── .gitignore
└── README.md
```

## Pages
| Route | Description |
|-------|-------------|
| `/login` | Signup / login — judges can create an account to try the app |
| `/dashboard` | Pet display + morning check-in form (protected) |

## Data Shape
```js
// POST to /checkin
{
  sleep_hours: 7.5,   // slider 0-12
  calories: 2000,     // manual input or vision pipeline
  steps: 8000,        // manual input or Google Fit
  mood: 4             // slider 1-5
}
```

## Pet States
| State | Health Score |
|-------|-------------|
| Thriving | 0.8 - 1.0 |
| Happy | 0.6 - 0.8 |
| Neutral | 0.4 - 0.6 |
| Tired | 0.2 - 0.4 |
| Sad | 0.0 - 0.2 |

## Set Up Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev` → runs at `http://localhost:5173`

## Set Up Backend
1. Make sure you're using the correct Python version:
```bash
python --version  # should match .python-version
```
2. `cd backend`
3. Create and activate the virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Run the server:
```bash
uvicorn main:app --reload    # runs at http://localhost:8000
```

## Running the App
Open two terminals:
| Terminal | Command | URL |
|----------|---------|-----|
| Frontend | `npm run dev` (in `/frontend`) | http://localhost:5173 |
| Backend | `uvicorn main:app --reload` (in `/backend`) | http://localhost:8000 |

## Deployment
| Part | Platform |
|------|----------|
| Frontend | Vercel |
| Backend | Railway or Render |
| Database | Supabase |