# 🐾 Tamagotchi Pet Health App

A web app that gamifies personal health tracking through a Tamagotchi-style virtual pet — your pet thrives when you do.

## Tech Stack
- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)

## General Structure
```
ACM-SCARLET-HACKS/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt
│   ├── .python-version
│   └── .gitignore
├── .vscode/
│   └── settings.json        # Shared VSCode interpreter path (Windows)
├── .gitignore
└── README.md
```

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
| Backend  | `uvicorn main:app --reload` (in `/backend`) | http://localhost:8000 |