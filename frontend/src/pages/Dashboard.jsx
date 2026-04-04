import { useState, useRef } from "react";
import "./Dashboard.css";

const PET_STATES = {
  thriving: { emoji: "🐣", label: "Thriving" },
  happy:    { emoji: "🐥", label: "Happy"    },
  neutral:  { emoji: "🐤", label: "Neutral"  },
  tired:    { emoji: "😴", label: "Tired"    },
  sad:      { emoji: "🥺", label: "Sad"      },
};

// Placeholder data — replace with real API calls
const MOCK = {
  username: "Ratana",
  petName: "Eggy",
  petState: "thriving",
  expScore: 72,
  streak: 5,
  coins: 120,
  sleep: "7.5h",
  steps: "8,204",
  calories: "1,840",
  petMessage: "You slept great! Let's get some steps in today 🌿",
};

export default function Dashboard() {
  const [tab, setTab] = useState("home");
  const [photo, setPhoto] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [calorieResult, setCalorieResult] = useState(null);
  const fileRef = useRef();

  const pet = PET_STATES[MOCK.petState];

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPhoto(URL.createObjectURL(file));
    setCalorieResult(null);
  };

  const handleAnalyze = async () => {
    if (!photo) return;
    setAnalyzing(true);
    // TODO: POST photo to /analyze-meal on FastAPI
    await new Promise((r) => setTimeout(r, 1500)); // mock delay
    setCalorieResult({ meal: "Grilled chicken & rice", calories: 540, protein: "38g" });
    setAnalyzing(false);
  };

  return (
    <div className="dash-screen">

      {/* ── HOME TAB ── */}
      {tab === "home" && (
        <>
          <div className="topbar">
            <div>
              <div className="greeting">Good morning 🌤</div>
              <div className="username">{MOCK.username}</div>
            </div>
            <div className="streak-pill">🔥 {MOCK.streak} day streak</div>
            <div className="gold-pill">👛 {MOCK.coins}</div>
          </div>

          {/* Pet card */}
          <div className="pet-card">
            <div className="pet-emoji">{pet.emoji}</div>
            <div className="pet-name">{MOCK.petName}</div>
            <div className="pet-state">{pet.label}</div>
            <div className="exp-bar-wrap">
              <div className="exp-bar-label">
                <span>Level</span>
                <span>{MOCK.expScore}%</span>
              </div>
              <div className="exp-bar-bg">
                <div className="exp-bar-fill" style={{ width: `${MOCK.expScore}%` }} />
              </div>
            </div>
          </div>

          {/* Pet message bubble */}
          <div className="message-bubble">
            <span className="bubble-pet">{pet.emoji}</span>
            <div className="bubble-text">{MOCK.petMessage}</div>
          </div>

          {/* Today's stats */}
          <div className="section-title">Today</div>
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-icon">😴</div>
              <div className="stat-val">{MOCK.sleep}</div>
              <div className="stat-label">Sleep</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">👟</div>
              <div className="stat-val">{MOCK.steps}</div>
              <div className="stat-label">Steps</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🍽️</div>
              <div className="stat-val">{MOCK.calories}</div>
              <div className="stat-label">Cal</div>
            </div>
          </div>

          {/* Connect devices */}
          <div className="section-title">Connect devices</div>
          <div className="settings-card">
            <div className="settings-row">
              <div className="settings-left">
                <div className="settings-icon-wrap">🏃</div>
                <div>
                  <div className="settings-row-label">Google Fit</div>
                  <div className="settings-row-sub">Steps & exercise</div>
                </div>
              </div>
              <button className="connect-btn">Connect</button>
            </div>
            <div className="settings-row">
              <div className="settings-left">
                <div className="settings-icon-wrap">😴</div>
                <div>
                  <div className="settings-row-label">Sleep tracker</div>
                  <div className="settings-row-sub">Sleep duration & quality</div>
                </div>
              </div>
              <button className="connect-btn">Connect</button>
            </div>
          </div>
        </>
      )}

      {/* ── SCAN TAB ── */}
      {tab === "scan" && (
        <>
          <div className="topbar">
            <div className="username">Log a meal</div>
          </div>

          <div className="camera-card">
            <div
              className="camera-preview"
              onClick={() => fileRef.current.click()}
              style={photo ? { backgroundImage: `url(${photo})`, backgroundSize: "cover", backgroundPosition: "center" } : {}}
            >
              {!photo && (
                <>
                  <div className="camera-icon">📷</div>
                  <div className="camera-hint">Tap to take a photo</div>
                </>
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: "none" }}
              onChange={handlePhoto}
            />
            <div className="camera-footer">
              <div>
                <div className="camera-label">Calorie scan</div>
                <div className="camera-sub">AI estimates from your photo</div>
              </div>
              <button className="analyze-btn" onClick={handleAnalyze} disabled={!photo || analyzing}>
                {analyzing ? "Analyzing..." : "Analyze"}
              </button>
            </div>
          </div>

          {calorieResult && (
            <div className="result-card">
              <div className="result-meal">{calorieResult.meal}</div>
              <div className="result-row">
                <span className="result-label">Calories</span>
                <span className="result-val">{calorieResult.calories} kcal</span>
              </div>
              <div className="result-row">
                <span className="result-label">Protein</span>
                <span className="result-val">{calorieResult.protein}</span>
              </div>
              <button className="log-btn">Log this meal</button>
            </div>
          )}
        </>
      )}

      {/* ── PLAY TAB ── */}
      {tab === "play" && (
        <>
          <div className="topbar">
            <div className="username">Play</div>
          </div>
          <div className="ar-placeholder">
            <div className="ar-icon">🌍</div>
            <div className="ar-title">AR mode coming soon</div>
            <div className="ar-sub">Take {MOCK.petName} out into the real world — Pokémon Go style. Stay tuned.</div>
          </div>
        </>
      )}

      {/* ── SETTINGS TAB ── */}
      {tab === "settings" && (
        <>
          <div className="topbar">
            <div className="username">Settings</div>
          </div>
          <div className="settings-card">
            <div className="settings-row">
              <div className="settings-left">
                <div className="settings-icon-wrap">👤</div>
                <div>
                  <div className="settings-row-label">Account</div>
                  <div className="settings-row-sub">{MOCK.username}</div>
                </div>
              </div>
              <span className="chevron">›</span>
            </div>
            <div className="settings-row">
              <div className="settings-left">
                <div className="settings-icon-wrap">🐣</div>
                <div>
                  <div className="settings-row-label">Pet name</div>
                  <div className="settings-row-sub">{MOCK.petName}</div>
                </div>
              </div>
              <span className="chevron">›</span>
            </div>
            <div className="settings-row">
              <div className="settings-left">
                <div className="settings-icon-wrap">🔔</div>
                <div>
                  <div className="settings-row-label">Notifications</div>
                  <div className="settings-row-sub">Morning check-in reminder</div>
                </div>
              </div>
              <span className="chevron">›</span>
            </div>
            <div className="settings-row">
              <div className="settings-left">
                <div className="settings-icon-wrap">🚪</div>
                <div>
                  <div className="settings-row-label">Sign out</div>
                </div>
              </div>
              <span className="chevron">›</span>
            </div>
          </div>
        </>
      )}

      {/* ── BOTTOM NAV ── */}
      <nav className="navbar">
        {[
          { id: "home",     icon: "🏠", label: "Home"     },
          { id: "scan",     icon: "📷", label: "Scan"     },
          { id: "play",     icon: "🎮", label: "Play"     },
          { id: "settings", icon: "⚙️", label: "Settings" },
        ].map(({ id, icon, label }) => (
          <button
            key={id}
            className={`nav-item ${tab === id ? "active" : ""}`}
            onClick={() => setTab(id)}
          >
            <span className="nav-icon">{icon}</span>
            <span className="nav-label">{label}</span>
          </button>
        ))}
      </nav>

    </div>
  );
}
