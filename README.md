# Tamagotchi Pet Health App

A web app that gamifies personal health tracking through a Tamagotchi-style virtual pet — your pet thrives when you do. Log daily checkpoints throughout the day and watch your pet react in real time.

## Tech Stack
- **Frontend:** React + Vite → deployed on Railway
- **Backend:** FastAPI (Python) → deployed on Railway
- **Database:** Supabase (Postgres + Auth)
- **AI:** Gemini 2.5 Flash (food vision analysis + AI pet messages)
- **3D Pet:** Spline (`@splinetool/react-spline`) with emotion-driven body states
- **AR Mode:** Browser camera overlay with 3D pet rendered on top

## Project Structure
```
ACM-SCARLET-HACKS/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ARCamera.jsx      # camera overlay with 3D pet AR view
│   │   │   └── PetModel.jsx      # Spline 3D pet with emotion switching
│   │   ├── pages/
│   │   │   ├── Login.jsx         # signup / login page
│   │   │   ├── Login.css
│   │   │   ├── Dashboard.jsx     # main app — pet, stats, check-ins, account
│   │   │   └── Dashboard.css
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── main.py                   # FastAPI entry point + all endpoints
│   ├── pet.py                    # health scoring, streak logic, AI messages
│   ├── vision.py                 # Gemini Vision food photo analysis
│   ├── model.py                  # Pydantic request/response models
│   ├── requirements.txt
│   └── Procfile                  # Railway deployment config
├── database/
│   └── schema.sql                # Supabase table definitions
├── railway.json
└── README.md
```

## Pages
| Route | Description |
|-------|-------------|
| `/login` | Signup / login — judges can create an account to try the app |
| `/dashboard` | Pet display, daily checkpoint logging, stat tracking, food photo scanner, account settings |

## How It Works

### Checkpoint System
The day is broken into 6 checkpoints: **wake, gym, breakfast, lunch, dinner, sleep**. Each time you hit a checkpoint, you tap the button to log it. The backend uses **Welford's online algorithm** to learn your personal timing patterns over time — when you're overdue on a checkpoint, your pet gets sad.

Pet state is derived from overdue checkpoints:
| Overdue Checkpoints | Pet State |
|---------------------|-----------|
| 0 | Happy |
| 1 | Neutral |
| 2 | Tired |
| 3+ | Sad |

### Health Score (for stat messages)
When you log a stat (sleep hours, calories), the backend computes a weighted score and generates an AI pet message via Gemini:

| Metric | Weight |
|--------|--------|
| Sleep | 30% |
| Calories | 25% |
| Steps | 25% |
| Mood | 20% |

### Food Photo Analysis
Upload a photo of your meal — Gemini Vision estimates calories and macros. The result feeds into your calorie stat.

### AI Pet Messages
Gemini 2.5 Flash generates personalized 2-sentence messages from the pet's perspective, reacting to your stats (sleep quality, calorie goal vs. actual, fitness goal: Cut / Bulk / Maintain).

### AR Mode
Tap the AR button on the dashboard to open your camera. The 3D Spline pet renders as an overlay on top of the live camera feed.

### Streaks
The backend tracks consecutive daily check-in streaks. Milestone days (7, 14, 30, 60, 100) trigger special pet messages.

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create account (email, password, username, pet name) |
| POST | `/login` | Authenticate and get access token |
| POST | `/checkin` | Log a checkpoint (wake/gym/breakfast/lunch/dinner/sleep) |
| GET | `/pet/state` | Get current pet state + overdue/upcoming checkpoints |
| POST | `/pet/stat-message` | AI-generated message for a logged stat |
| POST | `/analyze-food` | Upload food image → Gemini Vision calorie/macro estimate |
| GET | `/health` | Health check |

## Database Schema
Three tables in Supabase (Postgres):

- **`profiles`** — user info (username, pet name), linked to Supabase Auth
- **`checkins`** — raw checkpoint log with timestamp and hour_float
- **`user_checkpoint_stats`** — Welford running stats (mean, variance, std, needy_at) per checkpoint per user, split by weekday/weekend

## 3D Pet Emotion States
| Emotion | Trigger |
|---------|---------|
| `normal` | Default / neutral pet state |
| `happy` | 0 overdue checkpoints |
| `tired` | 2 overdue checkpoints |
| `sad` | 3+ overdue checkpoints |
| `sleep` | Sleep checkpoint logged |
| `sick` | Reserved |

## Set Up Frontend
```bash
cd frontend
npm install
npm run dev   # → http://localhost:5173
```

Set `VITE_API_URL` in a `.env` file in `/frontend` if pointing to a non-local backend:
```
VITE_API_URL=https://your-backend.up.railway.app
```

## Set Up Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file in `/backend`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
MOCK=false
```

Run the server:
```bash
uvicorn main:app --reload   # → http://localhost:8000
```

## Running Locally
Open two terminals:
| Terminal | Command | URL |
|----------|---------|-----|
| Frontend | `npm run dev` (in `/frontend`) | http://localhost:5173 |
| Backend | `uvicorn main:app --reload` (in `/backend`) | http://localhost:8000 |

## Deployment
| Part | Platform |
|------|----------|
| Frontend | Railway |
| Backend | Railway |
| Database | Supabase |
