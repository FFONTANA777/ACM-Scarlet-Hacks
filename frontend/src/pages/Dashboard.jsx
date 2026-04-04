import { useState, useRef } from "react";
import "./Dashboard.css";
import Model from "../components/PetModel.jsx";

const PET_STATES = {
<<<<<<< HEAD
  normal: {label: "Neutral"},
  sad: {label: "Sad"},
  tired: {label: "Tired"},
  sleep: {label: "Sleep"},
  sick: {label: "Neutral"},
=======
  thriving: { emoji: "🐣", label: "Thriving" },
  happy: { emoji: "🐥", label: "Happy" },
  neutral: { emoji: "🐤", label: "Neutral" },
  tired: { emoji: "😴", label: "Tired" },
  sad: { emoji: "🥺", label: "Sad" },
>>>>>>> 9a4ef2e309017ec0300c5a7db29475c5190a2de4
};

// Placeholder data — replace with real API calls
const MOCK = {
  username: "Ratana",
  petName: "Eggy",
  petState: "sleep",
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
  const [activeStatTab, setActiveStatTab] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [calorieResult, setCalorieResult] = useState(null);
  const fileRef = useRef();

  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [confirmMode, setConfirmMode] = useState("use");

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
            <div className="pet-model-wrap">
              <Model emotion={MOCK.petState} />
            </div>

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
          </div>

          {/* Pet message bubble */}
          <div className="message-bubble">
            <div className="bubble-text">{MOCK.petMessage}</div>
          </div>


          {/* Today's stats */}
          <div className="stats-container">
            <div className="section-title">Today</div>
            <div className="stats-row">
              {[
                { key: "sleep", icon: "😴", val: MOCK.sleep, label: "Sleep" },
                { key: "steps", icon: "👟", val: MOCK.steps, label: "Steps" },
                { key: "calories", icon: "🍽️", val: MOCK.calories, label: "Cal" },
              ].map(({ key, icon, val, label }) => (
                <div
                  key={key}
                  className={`stat-card ${activeStatTab === key ? "stat-card--active" : ""}`}
                  onClick={() => setActiveStatTab(prev => prev === key ? null : key)}
                >
                  <div className="stat-icon">{icon}</div>
                  <div className="stat-val">{val}</div>
                  <div className="stat-label">{label}</div>
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
                  <div className="stat-panel-bar-label"><span>Goal: 10,000</span><span>{MOCK.steps} / 10,000</span></div>
                  <div className="stat-panel-bar-bg"><div className="stat-panel-bar-fill" style={{ width: "82%" }} /></div>
                </div>
              </div>
            )}
            {activeStatTab === "calories" && (
              <div className="stat-panel">
                <div className="stat-panel-title">Calories breakdown</div>
                <div className="stat-panel-row"><span>Breakfast</span><span>480 kcal</span></div>
                <div className="stat-panel-row"><span>Lunch</span><span>720 kcal</span></div>
                <div className="stat-panel-row"><span>Dinner</span><span>510 kcal</span></div>
                <div className="stat-panel-row"><span>Snacks</span><span>130 kcal</span></div>
                <div className="stat-panel-bar">
                  <div className="stat-panel-bar-label"><span>Goal: 2,000</span><span>{MOCK.calories} / 2,000</span></div>
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
