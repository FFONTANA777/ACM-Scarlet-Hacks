import { useState, useRef, useEffect } from "react";
import "./Dashboard.css";
import ARCamera from "../components/ARCamera.jsx";
import Model from "../components/PetModel.jsx";
import { useNavigate } from "react-router-dom";

const PET_STATES = {
  normal: { mood: "normal", label: "Neutral" },
  happy: { mood: "happy", label: "Happy" },
  sad: { mood: "sad", label: "Sad" },
  tired: { mood: "tired", label: "Tired" },
  sleep: { mood: "sleep", label: "Sleep" },
  sick: { mood: "sick", label: "Neutral" },
};

// Placeholder data — replace with real API calls
const MOCK = {
  username: "Ratana",
  petName: "Eggy",
  petState: "normal",
  level: 1,
  expScore: 72,
  streak: 5,
  coins: 120,
  sleep: "7.5h",
  steps: "8,204",
  calories: "1,840",
  petMessage: "You slept great! Let's get some steps in today 🌿",

  // Add your owned items right here:
  inventory: [
    { id: 'Ice', icon: '🧊', amount: 6, price: 50 },
    { id: 'Boost', icon: '⚡', amount: 7, price: 100 },
  ]
};

// Raw numeric values for the stat buttons (used when sending to backend)
const STAT_RAW = {
  sleep: 7.5,
  steps: 8204,
  calories: 1840,
};

const GOALS = ["Cut", "Bulk", "Maintain"];
const GENDERS = ["Male", "Female", "Other", "Prefer not to say"];
const ACTIVITY_LEVELS = [
  { id: "sedentary", label: "Sedentary", sub: "Little or no exercise" },
  { id: "light", label: "Lightly active", sub: "1–3 days/week" },
  { id: "moderate", label: "Moderately active", sub: "3–5 days/week" },
  { id: "very", label: "Very active", sub: "6–7 days/week" },
  { id: "extra", label: "Extra active", sub: "Physical job or 2x/day" },
];

const ACCOUNT_INITIAL = {
  nickname: "Ratana", gender: "Male", email: "hack@example.com",
  birthYear: "2001", height: "175", weight: "70",
  goal: "Maintain", activity: "moderate", calorieGoal: "2200", stepsGoal: "8000", sleepGoal: "8"
};

function AccountScreen({ onBack }) {
  const [form, setForm] = useState(ACCOUNT_INITIAL);
  function set(key, val) { setForm(prev => ({ ...prev, [key]: val })); }
  function handleSave() { console.log("Save:", form); onBack(); }

  return (
    <div style={{ paddingBottom: 120 }}>
      <div className="topbar" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button onClick={onBack} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 20, color: "var(--text)", padding: 0 }}>‹</button>
          <div className="username">Account</div>
        </div>
      </div>

      <div className="section-title">Identity</div>
      <div className="account-card">
        <div className="account-row">
          <div className="account-row-label">Nickname</div>
          <input className="account-row-input" value={form.nickname}
            onChange={e => set("nickname", e.target.value)} placeholder="Your name" />
        </div>
        <div className="account-row">
          <div className="account-row-label">Email</div>
          <input className="account-row-input" value={form.email} type="email"
            onChange={e => set("email", e.target.value)} placeholder="email@example.com" />
        </div>
        <div className="account-row">
          <div className="account-row-label">Gender</div>
          <div style={{ display: "flex", gap: 8, paddingTop: 4 }}>
            {GENDERS.map(g => (
              <button key={g} onClick={() => set("gender", g)} style={{
                flex: 1,
                padding: "10px 8px",
                borderRadius: 10,
                border: form.gender === g ? "1.5px solid var(--text)" : "0.5px solid #E2DDD5",
                background: form.gender === g ? "var(--text)" : "var(--surface)",
                color: form.gender === g ? "#fff" : "var(--text)",
                cursor: "pointer",
                fontSize: 12,
                fontWeight: 600,
                textAlign: "center",
              }}>
                {g}
                {form.gender === g && <div style={{ fontSize: 10, opacity: 0.8, marginTop: 2 }}>✓</div>}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="section-title">Body</div>
      <div className="settings-card">
        <div className="account-row">
          <div className="account-row-label">Height <span style={{ textTransform: "none" }}>(cm)</span></div>
          <input className="account-row-input" value={form.height} type="number"
            onChange={e => set("height", e.target.value)} placeholder="e.g. 175" />
        </div>

        <div className="account-row">
          <div className="account-row-label">Weight <span style={{ textTransform: "none" }}>(kg)</span></div>
          <input className="account-row-input" value={form.weight} type="number"
            onChange={e => set("weight", e.target.value)} placeholder="e.g. 70" />
        </div>
      </div>

      <div className="section-title">Goals</div>
      <div className="settings-card">
        <div className="account-row">
          <div className="account-row-label">Goal</div>
          <div style={{ display: "flex", gap: 8, paddingTop: 4 }}>
            {GOALS.map(g => (
              <button key={g} onClick={() => set("goal", g)} style={{
                flex: 1,
                padding: "10px 8px",
                borderRadius: 10,
                border: form.goal === g ? "1.5px solid var(--text)" : "0.5px solid #E2DDD5",
                background: form.goal === g ? "var(--text)" : "var(--surface)",
                color: form.goal === g ? "#fff" : "var(--text)",
                cursor: "pointer",
                fontSize: 12,
                fontWeight: 600,
                textAlign: "center",
              }}>
                {g}
                {form.goal === g && <div style={{ fontSize: 10, opacity: 0.8, marginTop: 2 }}>✓</div>}
              </button>
            ))}
          </div>
        </div>
        <div className="settings-row" style={{ flexDirection: "column", alignItems: "flex-start", gap: 8 }}>
          <div className="settings-row-label">Activity level</div>
          {ACTIVITY_LEVELS.map(a => (
            <button key={a.id} onClick={() => set("activity", a.id)} style={{
              width: "100%", display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: "10px 12px", borderRadius: 10, marginBottom: 6, cursor: "pointer", textAlign: "left",
              border: form.activity === a.id ? "1.5px solid var(--text)" : "0.5px solid #E2DDD5",
              background: form.activity === a.id ? "var(--text)" : "var(--surface)",
              color: form.activity === a.id ? "#fff" : "var(--text)",
            }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{a.label}</div>
                <div style={{ fontSize: 11, opacity: 0.65, marginTop: 1 }}>{a.sub}</div>
              </div>
              {form.activity === a.id && <span>✓</span>}
            </button>
          ))}
        </div>
        <div className="account-row">
          <div className="account-row-label">Calorie goal <span style={{ textTransform: "none", fontSize: 10, color: "var(--text-muted)" }}>(override)</span></div>
          <input className="account-row-input" value={form.calorieGoal} type="number"
            onChange={e => set("calorieGoal", e.target.value)} placeholder="e.g. 2000" />
        </div>

        <div className="account-row">
          <div className="account-row-label">Daily steps goal</div>
          <input className="account-row-input" value={form.stepsGoal} type="number"
            onChange={e => set("stepsGoal", e.target.value)} placeholder="e.g. 10000" />
        </div>

        <div className="account-row">
          <div className="account-row-label">Daily sleep goal</div>
          <input className="account-row-input" value={form.sleepGoal} type="number"
            onChange={e => set("sleepGoal", e.target.value)} placeholder="e.g. 8" />
        </div>
      </div>

      <div style={{ padding: "20px 20px 0" }}>
        <button className="log-btn" onClick={handleSave}>Save changes</button>
      </div>
    </div>
  );
}

function NotificationScreen({ onBack }) {
  const [enabled, setEnabled] = useState(true);

  return (
    <div style={{ paddingBottom: 120 }}>
      <div className="topbar" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button
            onClick={onBack}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              fontSize: 20,
              color: "var(--text)",
              padding: 0
            }}
          >
            ‹
          </button>
          <div className="username">Notifications</div>
        </div>
      </div>

      <div className="settings-card">
        <div className="settings-row">
          <div className="settings-left">
            <div className="settings-icon-wrap">🔔</div>
            <div>
              <div className="settings-row-label">Notifications</div>
              <div className="settings-row-sub">
                Enable or disable notifications
              </div>
            </div>
          </div>

          <button
            onClick={() => setEnabled(!enabled)}
            style={{
              padding: "6px 12px",
              borderRadius: 8,
              border: "none",
              cursor: "pointer",
              background: enabled ? "var(--text)" : "#ccc",
              color: enabled ? "#fff" : "#000",
              fontWeight: 600,
              width: 60,
              textAlign: "center"
            }}
          >
            {enabled ? "ON" : "OFF"}
          </button>
        </div>
      </div>
    </div>
  );
}

const Confirm = ({ isOpen, item, mode, onCancel, onConfirm }) => {
  if (!isOpen) return null;

  const isBuy = mode === "buy";

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ fontSize: '40px', marginBottom: '10px' }}>{item?.icon}</div>
        <h3>{isBuy ? `Buy ${item?.id}?` : `Use ${item?.id}?`}</h3>
        <p>
          {isBuy
            ? `Spend 🪙 ${item?.price} to get this item?`
            : `Are you sure you want to use 1 ${item?.id}?`}
        </p>
        <div className="modal-actions">
          <button className="btn-cancel" onClick={onCancel}>Cancel</button>
          <button
            className="btn-confirm"
            style={{ background: isBuy ? '#FFD700' : '#000', color: isBuy ? '#000' : '#fff' }}
            onClick={onConfirm}
          >
            {isBuy ? 'Purchase' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [tab, setTab] = useState("home");
  const navigate = useNavigate();
  const [subScreen, setSubScreen] = useState(null);
  const [activeStatTab, setActiveStatTab] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [mealDescription, setMealDescription] = useState("");
  const [calorieResult, setCalorieResult] = useState(null);
  const fileRef = useRef();
  const cameraRef = useRef();

  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [confirmMode, setConfirmMode] = useState("use");

  const [pet, setPet] = useState(PET_STATES[MOCK.petState]);
  const [mood, setMood] = useState(PET_STATES[MOCK.petState].mood);
  const [petMessage, setPetMessage] = useState(MOCK.petMessage);
  const [petMessageLoading, setPetMessageLoading] = useState(false);

  const [photoFile, setPhotoFile] = useState(null);

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setPhoto(URL.createObjectURL(file)); // preview
    setPhotoFile(file);
    setCalorieResult(null);
  };

  // TEMPORARY HARD CODE DELETE
  useEffect(() => {
    fetch(`http://localhost:8000/pet/state?user_id=4630c2cd-8bff-4df0-b22c-da920991cceb`)
      .then(res => res.json())
      .then(data => {
        setMood(PET_STATES[data.pet_state].mood)
        setPet(PET_STATES[data.pet_state])
      });
  }, []);

  const [breakdownOpen, setBreakdownOpen] = useState(false);

  const [showAR, setShowAR] = useState(false);

  const handleAnalyze = async () => {
    if (!photoFile) return;
 
    setAnalyzing(true);
    setBreakdownOpen(false);
 
    const formData = new FormData();
    formData.append("file", photoFile);
 
    try {
      const res = await fetch("http://localhost:8000/analyze-food", {
        method: "POST",
        body: formData,
      });
 
      const raw = await res.json();
 
      // Remap backend field names → UI field names
      setCalorieResult({
        meal:    raw.description,
        calories: raw.calories,
        protein: raw.protein_g + "g",
        carbs:   raw.carbs_g + "g",
        fats:    raw.fat_g + "g",
        items: (raw.items ?? []).map(item => ({
          name:     item.name,
          calories: item.calories,
          protein:  item.protein_g + "g",
          carbs:    item.carbs_g + "g",
          fats:     item.fat_g + "g",
        })),
      });
    } catch (err) {
      console.error("Analyze failed:", err);
    }
 
    setAnalyzing(false);
  };

  const handleStatClick = async (key) => {
    const next = activeStatTab === key ? null : key;
    setActiveStatTab(next);
    if (next === null) return;

    setPetMessageLoading(true);
    try {
      const res = await fetch("http://localhost:8000/pet/stat-message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "4630c2cd-8bff-4df0-b22c-da920991cceb",
          stat_type: key,
          value: STAT_RAW[key],
          goal_value: parseFloat(ACCOUNT_INITIAL[{ sleep: "sleepGoal", steps: "stepsGoal", calories: "calorieGoal" }[key]]),
          fitness_goal: ACCOUNT_INITIAL.goal,
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        console.error("Stat message error:", err);
      } else {
        const data = await res.json();
        setPetMessage(data.message);
      }
    } catch (err) {
      console.error("Stat message failed (network):", err);
    }
    setPetMessageLoading(false);
  };

  const handleUseItem = () => {
    console.log(`Used ${selectedItem.id}!`);
    // Here you would eventually update the item count
    setIsConfirmOpen(false);
  };

  return (
    <div className={`dash-screen ${tab === "shop" ? "shop-open" : ""}`}>

      {/* ── HOME TAB ── */}
      {tab === "home" && (
        <>
          <div className="topbar">
            <div>
              <div className="greeting">Good morning 🌤</div>
              <div className="username">{MOCK.username}</div>
            </div>
            <div className="streak-pill">🔥 {MOCK.streak} day streak</div>
            <div className="coins-pill">👛 {MOCK.coins}</div>
          </div>

          {/* Pet card */}
          <div className="pet-card">
            <div className="pet-info-container">
              <div className="pet-name">{MOCK.petName}</div>
              <div className="pet-state">{pet.label}</div>
              <div className="exp-bar-wrap">
                <div className="exp-bar-label">
                  <span>Level {MOCK.level}</span>
                  <span>{MOCK.expScore}/100 XP</span>
                </div>
                <div className="exp-bar-bg">
                  <div className="exp-bar-fill" style={{ width: `${MOCK.expScore}%` }} />
                </div>
              </div>
            </div>
            <button className="ar-btn" onClick={() => setShowAR(true)}>
            📷 View in AR
          </button>
            <div className="pet-model-wrap">
              <Model emotion={mood} />
            </div>
          </div>

          {/* Pet message bubble */}
          <div className="message-bubble">
            <div className="bubble-text">
              {petMessageLoading ? "..." : petMessage}
            </div>
          </div>


          {/* Today's stats */}
          <div className="stats-container">
            <div className="section-title">Today</div>
            <div className="stats-row">
              {[
                { key: "sleep", icon: "😴", val: MOCK.sleep, label: "Sleep" },
                { key: "steps", icon: "👟", val: MOCK.steps, label: "Steps" },
                { key: "calories", icon: "🍽️", val: MOCK.calories, label: "Calories" },
              ].map(({ key, icon, val, label }) => (
                <div
                  key={key}
                  className={`stat-card ${activeStatTab === key ? "stat-card--active" : ""}`}
                  onClick={() => handleStatClick(key)}
                >
                  <div className="stat-icon">{icon}</div>
                  <div className="stat-val">{val}</div>
                  <div className="stat-label">{label}</div>
                  <img src="/images/arrow-right.png" alt="arrow" className="stat-more" />
                </div>
              ))}
            </div>
            {/* Expanded stat panel */}
            {activeStatTab === "sleep" && (
              <div className="stat-panel">
                <div className="stat-panel-title">Sleep breakdown</div>
                <div className="stat-panel-row"><span>Bedtime</span><span>11:14 PM</span></div>
                <div className="stat-panel-row"><span>Wake time</span><span>6:26 AM</span></div>
                <div className="stat-panel-row"><span>Deep sleep</span><span>1h 48m</span></div>
                <div className="stat-panel-row"><span>REM</span><span>2h 12m</span></div>
                <div className="stat-panel-bar">
                  <div className="stat-panel-bar-label"><span>Goal: 8h</span><span>{MOCK.sleep} / 8h</span></div>
                  <div className="stat-panel-bar-bg"><div className="stat-panel-bar-fill" style={{ width: "90%" }} /></div>
                </div>
              </div>
            )}
            {activeStatTab === "steps" && (
              <div className="stat-panel">
                <div className="stat-panel-title">Steps breakdown</div>
                <div className="stat-panel-row"><span>Distance</span><span>3.8 mi</span></div>
                <div className="stat-panel-row"><span>Active minutes</span><span>42 min</span></div>
                <div className="stat-panel-row"><span>Floors climbed</span><span>9</span></div>
                <div className="stat-panel-row"><span>Calories burned</span><span>312 kcal</span></div>
                <div className="stat-panel-bar">
                  <div className="stat-panel-bar-label"><span>Goal: {ACCOUNT_INITIAL.stepsGoal}</span><span>{MOCK.steps} / {ACCOUNT_INITIAL.stepsGoal}</span></div>
                  <div className="stat-panel-bar-bg"><div className="stat-panel-bar-fill" style={{ width: "82%" }} /></div>
                </div>
              </div>
            )}
            {activeStatTab === "calories" && (
              <div className="stat-panel">
                <div className="stat-panel-title">Calories breakdown</div>
                <div className="macros-row">
                  <div className="macro-card">
                    <div className="macro-val">38g</div>
                    <div className="macro-label">Protein</div>
                  </div>
                  <div className="macro-card">
                    <div className="macro-val">210g</div>
                    <div className="macro-label">Carbs</div>
                  </div>
                  <div className="macro-card">
                    <div className="macro-val">52g</div>
                    <div className="macro-label">Fats</div>
                  </div>
                </div>
                <div className="stat-panel-row"><span>Breakfast</span><span>480 kcal</span></div>
                <div className="stat-panel-row"><span>Lunch</span><span>720 kcal</span></div>
                <div className="stat-panel-row"><span>Dinner</span><span>510 kcal</span></div>
                <div className="stat-panel-row"><span>Snacks</span><span>130 kcal</span></div>
                <div className="stat-panel-bar">
                  <div className="stat-panel-bar-label"><span>Goal: {ACCOUNT_INITIAL.calorieGoal}</span><span>{MOCK.calories} / {ACCOUNT_INITIAL.calorieGoal}</span></div>
                  <div className="stat-panel-bar-bg"><div className="stat-panel-bar-fill" style={{ width: "92%" }} /></div>
                </div>
              </div>
            )}
          </div>
          {/* Connect devices */}
          <div className="devices-container">
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
            {showAR && <ARCamera emotion={MOCK.petState} onClose={() => setShowAR(false)} />}
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
              onClick={() => cameraRef.current.click()}
              style={photo ? { backgroundImage: `url(${photo})`, backgroundSize: "cover", backgroundPosition: "center" } : {}}
            >
              {!photo && (
                <>
                  <div className="camera-icon">📷</div>
                  <div className="camera-hint">Tap to take a photo</div>
                </>
              )}
            </div>
            <div className="scan-controls">
              <button className="scan-mode-btn scan-mode-btn--camera" onClick={() => cameraRef.current.click()}>
                Take photo
              </button>
              <button className="scan-mode-btn scan-mode-btn--upload" onClick={() => fileRef.current.click()}>
                Choose file
              </button>
            </div>
            <input
              ref={cameraRef}
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: "none" }}
              onChange={handlePhoto}
            />
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handlePhoto}
            />
            <div className="desc-title">Meal description</div>
                <textarea
                  className="desc-box"
                  placeholder="Describe your meal..."
                  value={mealDescription}
                  onChange={(e) => setMealDescription(e.target.value)}
                />
            <div className="camera-footer">
              <div>
                <div className="camera-label">Food scanner</div>
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
              {/* <div className="result-row">
                <span className="result-label">Calories</span>
                <span className="result-val">{calorieResult.calories} kcal</span>
              </div>
              <div className="result-row">
                <span className="result-label">Protein</span>
                <span className="result-val">{calorieResult.protein}</span>
              </div> */}
              <div className="cals-row">
                <div className="cals-card">
                  <div className="cal-val">{calorieResult.calories} kcal</div>
                  <div className="cal-label">Calories</div>
                </div>
              </div>
              <div className="macros-row">
                <div className="macro-card">
                  <div className="macro-val">{calorieResult.protein}</div>
                  <div className="macro-label">Protein</div>
                </div>
                <div className="macro-card">
                  <div className="macro-val">{calorieResult.carbs}</div>
                  <div className="macro-label">Carbs</div>
                </div>
                <div className="macro-card">
                  <div className="macro-val">{calorieResult.fats}</div>
                  <div className="macro-label">Fats</div>
                </div>
              </div>
              {calorieResult.items?.length > 0 && (
                <>
                  <button
                    className="breakdown-toggle"
                    onClick={() => setBreakdownOpen(prev => !prev)}
                  >
                    <div className="breakdown-line" />
                    <span className="breakdown-label">
                      {breakdownOpen ? "Hide breakdown ▲" : "View item breakdown ▼"}
                    </span>
                    <div className="breakdown-line" />
                  </button>

                  {breakdownOpen && (
                    <>
                      <div className="breakdown-list">
                        {calorieResult.items.map((item, i) => (
                          <div key={i} className="breakdown-item">
                            <div className="breakdown-item-name">{item.name}</div>
                            <div className="breakdown-item-macros">
                              <span>{item.calories} kcal</span>
                              <span>P {item.protein}</span>
                              <span>C {item.carbs}</span>
                              <span>F {item.fats}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="breakdown-footer">
                        <button className="add-item-btn"><svg width="12px" height="12px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 8V16M8 12H16M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>Add Item</button>
                      </div>
                    </>
                  )}
                </>
              )}
              <button className="log-btn">Log this meal</button>
            </div>
          )}
        </>
      )}

      {/* ── SHOP TAB ── */}
      {tab === "shop" && (
        <>
          <div className="topbar">
            <div className="username">Shop</div>
            <div className="coins-pill">👛 {MOCK.coins}</div>
          </div>
          <div className="shop-title">Featured</div>
          <div className="shop-featured">
            <div className="shop-icon">🛍️</div>
            <div className="shop-name">Shop coming soon</div>
            <div className="shop-sub">Spend your coins on cosmetics, boosts, and accessories for {MOCK.petName}.</div>
          </div>

          <div className="shop-title">Items</div>
          <div className="shop-grid">
            {MOCK.inventory.map((item) => (
              <div key={item.id} className="shop-items">
                <div className="shop-icon">{item.icon}</div>
                <div className="shop-name">{item.id.charAt(0).toUpperCase() + item.id.slice(1)}</div>
                <div className="shop-sub">
                  {item.id === 'Ice' ? "Freeze Eggy to skip a day." : "Double XP for 24 hours."}
                </div>

                {/* The Purchase Button */}
                <button
                  className="buy-btn"
                  onClick={() => {
                    setSelectedItem(item);
                    setConfirmMode("buy"); // Set mode to buy
                    setIsConfirmOpen(true);
                  }}
                >
                  🪙 {item.price}
                </button>
              </div>
            ))}
          </div>


          {/* Inventory bar */}
          <div className="inventory-bar">
            {MOCK.inventory && MOCK.inventory.length > 0 ? (
              MOCK.inventory.map((item) => (
                <button
                  className={`inventory-slot ${item.amount === 0 ? 'empty' : ''}`}
                  onClick={() => {
                    setSelectedItem(item);
                    setConfirmMode("use"); // Set mode to use
                    setIsConfirmOpen(true);
                  }}
                >
                  <span>{item.icon}</span>
                  {item.amount > 0 && <div className="inventory-badge">{item.amount}</div>}
                </button>
              ))
            ) : (
              /* Fallback if inventory is missing or empty */
              <p style={{ fontSize: '10px', color: '#999' }}>No items found</p>
            )}

          </div>
        </>
      )}

      {/* ── SETTINGS TAB ── */}
      {tab === "settings" && (
        <>
          {subScreen === "account" ? (
            <AccountScreen onBack={() => setSubScreen(null)} />
          ) : subScreen === "notifications" ? (
            <NotificationScreen onBack={() => setSubScreen(null)} />
          ) : (
            <>
              <div className="topbar">
                <div className="username">Settings</div>
              </div>
              <div className="settings-card">
                <div className="settings-row" onClick={() => setSubScreen("account")} style={{ cursor: "pointer" }}>
                  <div className="settings-left">
                    <div className="settings-icon-wrap">👤</div>
                    <div>
                      <div className="settings-row-label">Account</div>
                    </div>
                  </div>
                  <span className="chevron">›</span>
                </div>
                <div className="settings-row" style={{ cursor: "pointer" }}>
                  <div className="settings-left">
                    <div className="settings-icon-wrap">🐣</div>
                    <div>
                      <div className="settings-row-label">Pet name</div>
                    </div>
                  </div>
                  <span className="chevron">›</span>
                </div>
                <div
                  className="settings-row"
                  style={{ cursor: "pointer" }}
                  onClick={() => setSubScreen("notifications")}
                >
                  <div className="settings-left">
                    <div className="settings-icon-wrap">🔔</div>
                    <div>
                      <div className="settings-row-label">Notifications</div>
                    </div>
                  </div>
                  <span className="chevron">›</span>
                </div>
                <div
                  className="settings-row"
                  style={{ cursor: "pointer" }}
                  onClick={() => navigate("/")} // send back to Login.jsx
                >
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
        </>
      )}

      {/* ── BOTTOM NAV ── */}
      <nav className="navbar">
        {[
          { id: "home", icon: "🏠", label: "Home" },
          { id: "scan", icon: "📷", label: "Scan" },
          { id: "shop", icon: "🛍️", label: "Shop" },
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

      <Confirm
        isOpen={isConfirmOpen}
        item={selectedItem}
        mode={confirmMode}
        onCancel={() => setIsConfirmOpen(false)}
        onConfirm={handleUseItem}
      />
    </div>
  );
}
