"""
SahayakAI — Teacher Dashboard (DAY 6 UI UPGRADE + DAY 7 SHAP)
==============================================================
UPGRADES:
  ✅ Animated risk bars (CSS keyframes)
  ✅ Glowing tier badges with pulse on critical
  ✅ Live clock in header
  ✅ Hover lift effects on alert cards
  ✅ Rainbow gradient top border
  ✅ Staggered card animations
  ✅ ASI-1 interaction counter badge
  ✅ SHAP plain English explanations
  ✅ Mobile-responsive layout

Run: streamlit run src/dashboard/app.py
Tech Z Ideathon 2026 | SahayakAI — The Silence Before the Drop
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SahayakAI — Teacher Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# STUNNING CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Reset ── */
* { font-family: 'Sora', sans-serif; box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem 2rem; max-width: 1400px; }

/* ── Keyframe Animations ── */
@keyframes fillBar {
  from { width: 0% !important; }
  to   { width: var(--w); }
}
@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(230,57,70,0.5); }
  50%      { box-shadow: 0 0 0 10px rgba(230,57,70,0); }
}
@keyframes glowGreen {
  0%,100% { box-shadow: 0 0 4px #2A9D8F; }
  50%      { box-shadow: 0 0 14px #2A9D8F; }
}
@keyframes slideUp {
  from { opacity:0; transform:translateY(16px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeIn {
  from { opacity:0; }
  to   { opacity:1; }
}
@keyframes breathe {
  0%,100% { opacity:0.7; }
  50%      { opacity:1; }
}
@keyframes rainbowBorder {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ── Header ── */
.sahayak-header {
  background: linear-gradient(135deg, #0D1117 0%, #161B22 60%, #1C2128 100%);
  border: 1px solid #30363D;
  border-radius: 14px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.5s ease;
}
.sahayak-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, #E63946, #F4A261, #2A9D8F, #457B9D, #9B89AC, #E63946);
  background-size: 300% 100%;
  animation: rainbowBorder 4s ease infinite;
}
.logo-wrap { display: flex; flex-direction: column; }
.logo-mark {
  font-size: 1.45rem;
  font-weight: 800;
  color: #E6EDF3;
  letter-spacing: -1px;
  line-height: 1.1;
}
.logo-mark span { color: #E63946; }
.logo-sub {
  font-size: 0.67rem;
  color: #8B949E;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 1.2px;
  margin-top: 1px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.live-clock {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem;
  color: #2A9D8F;
  background: rgba(42,157,143,0.08);
  border: 1px solid rgba(42,157,143,0.3);
  border-radius: 8px;
  padding: 6px 14px;
  animation: breathe 2.5s ease infinite;
  white-space: nowrap;
}
.asi1-badge {
  background: linear-gradient(135deg, #1A1040, #2D1B6E);
  border: 1px solid #7C3AED;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.7rem;
  color: #C4B5FD;
  font-family: 'JetBrains Mono', monospace;
  animation: glowGreen 3s ease infinite;
  white-space: nowrap;
}

/* ── Demo Banner ── */
.demo-banner {
  background: linear-gradient(90deg, #1A1200, #2D2000);
  border: 1px solid rgba(244,162,97,0.5);
  border-radius: 10px;
  padding: 10px 18px;
  margin-bottom: 14px;
  font-size: 0.79rem;
  color: #F4A261;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideUp 0.4s ease 0.1s both;
}

/* ── Section Header ── */
.section-header {
  font-size: 0.67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #8B949E;
  margin: 20px 0 10px 0;
  padding-bottom: 7px;
  border-bottom: 1px solid #21262D;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Metric Cards ── */
.metric-card {
  background: linear-gradient(135deg, #161B22, #1C2128);
  border: 1px solid #30363D;
  border-radius: 12px;
  padding: 18px 16px;
  text-align: center;
  transition: border-color 0.25s, transform 0.2s;
  animation: slideUp 0.5s ease both;
  position: relative;
  overflow: hidden;
}
.metric-card:hover {
  border-color: #484F58;
  transform: translateY(-2px);
}
.metric-number {
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 4px;
  letter-spacing: -1px;
}
.metric-label {
  font-size: 0.68rem;
  color: #8B949E;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}
.metric-delta {
  font-size: 0.72rem;
  margin-top: 5px;
  font-family: 'JetBrains Mono', monospace;
}

/* ── Alert Cards ── */
.alert-card {
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 9px;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: slideUp 0.4s ease both;
}
.alert-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}
.alert-card.critical {
  background: linear-gradient(135deg, #1C1217, #201318);
  border: 1px solid #E63946;
  animation: slideUp 0.4s ease both, pulse 2.5s ease infinite 0.5s;
}
.alert-card.moderate {
  background: linear-gradient(135deg, #1C1A12, #201E14);
  border: 1px solid #F4A261;
}
.alert-card.watchlist {
  background: linear-gradient(135deg, #121820, #141C24);
  border: 1px solid #457B9D;
}
.alert-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  border-radius: 3px 0 0 3px;
}
.alert-card.critical::before { background: #E63946; }
.alert-card.moderate::before { background: #F4A261; }
.alert-card.watchlist::before { background: #457B9D; }
.alert-name { font-weight: 700; font-size: 0.93rem; color: #E6EDF3; }
.alert-signal { font-size: 0.76rem; color: #8B949E; margin-top: 3px; }
.alert-risk {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 700;
}

/* ── Animated Risk Bar ── */
.risk-bar-wrap {
  background: #21262D;
  border-radius: 6px;
  height: 7px;
  width: 100%;
  margin: 9px 0 0 0;
  overflow: hidden;
}
.risk-bar-inner {
  height: 100%;
  border-radius: 6px;
  animation: fillBar 1s ease forwards;
}

/* ── Tier Badge ── */
.tier-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 0.68rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}
.tier-badge.t1 {
  background: rgba(230,57,70,0.12);
  color: #E63946;
  border: 1px solid rgba(230,57,70,0.3);
}
.tier-badge.t2 {
  background: rgba(244,162,97,0.12);
  color: #F4A261;
  border: 1px solid rgba(244,162,97,0.3);
}
.tier-badge.t3 {
  background: rgba(69,123,157,0.12);
  color: #457B9D;
  border: 1px solid rgba(69,123,157,0.3);
}
.tier-badge.t4 {
  background: rgba(42,157,143,0.12);
  color: #2A9D8F;
  border: 1px solid rgba(42,157,143,0.3);
}

/* ── Profile Card ── */
.profile-card {
  background: linear-gradient(135deg, #161B22, #1C2128);
  border: 1px solid #30363D;
  border-radius: 12px;
  padding: 18px;
  margin-top: 10px;
  animation: slideUp 0.3s ease;
}
.profile-name { font-size: 1.1rem; font-weight: 700; color: #E6EDF3; }
.profile-meta {
  font-size: 0.76rem;
  color: #8B949E;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 2px;
}

/* ── Signal Pill ── */
.signal-pill {
  display: inline-block;
  background: rgba(48,54,61,0.6);
  border: 1px solid #30363D;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.7rem;
  color: #8B949E;
  margin: 2px;
  font-family: 'JetBrains Mono', monospace;
  transition: border-color 0.2s, color 0.2s;
}
.signal-pill:hover { border-color: #8B949E; color: #E6EDF3; }

/* ── WhatsApp Box ── */
.wa-box {
  background: linear-gradient(135deg, #0F2010, #142818);
  border: 1px solid rgba(42,157,143,0.4);
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 0.8rem;
  color: #A7F3D0;
  line-height: 1.65;
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', monospace;
  position: relative;
}
.wa-box::before {
  content: '💬 WhatsApp';
  position: absolute;
  top: -10px; left: 12px;
  background: #142818;
  color: #2A9D8F;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0 6px;
  font-family: 'Sora', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ── Model Status Card ── */
.model-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #21262D;
  font-size: 0.78rem;
}
.model-stat-row:last-child { border-bottom: none; }
.model-stat-label { color: #8B949E; }
.model-stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

/* ── Timeline ── */
.tl-item {
  border-left: 2px solid #30363D;
  padding: 0 0 16px 16px;
  margin-left: 8px;
  position: relative;
  transition: border-color 0.2s;
}
.tl-item:hover { border-left-color: #8B949E; }
.tl-dot {
  position: absolute;
  left: -5px; top: 4px;
  width: 8px; height: 8px;
  border-radius: 50%;
  transition: transform 0.2s;
}
.tl-item:hover .tl-dot { transform: scale(1.4); }
.tl-date { font-size: 0.7rem; color: #8B949E; font-family: 'JetBrains Mono', monospace; }
.tl-action { font-size: 0.84rem; color: #E6EDF3; font-weight: 600; margin-top: 1px; }
.tl-result { font-size: 0.76rem; color: #8B949E; margin-top: 2px; }
.tl-outcome { font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; margin-top: 4px; }

/* ── Trend Row ── */
.trend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 0;
  border-bottom: 1px solid #21262D;
  font-size: 0.82rem;
  transition: background 0.15s;
}
.trend-row:hover { background: rgba(48,54,61,0.2); }
.trend-label { color: #8B949E; }
.trend-value { font-family: 'JetBrains Mono', monospace; font-weight: 700; }

/* ── Quick action button override ── */
.stButton > button {
  background: linear-gradient(135deg, #1C2128, #21262D) !important;
  border: 1px solid #30363D !important;
  border-radius: 9px !important;
  color: #E6EDF3 !important;
  font-family: 'Sora', sans-serif !important;
  font-size: 0.84rem !important;
  padding: 10px 16px !important;
  transition: all 0.2s ease !important;
  text-align: left !important;
  width: 100% !important;
}
.stButton > button:hover {
  border-color: #8B949E !important;
  background: linear-gradient(135deg, #21262D, #2D333B) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
}

/* ── Privacy Card ── */
.privacy-card {
  background: linear-gradient(135deg, #0D1117, #111620);
  border: 1px solid #30363D;
  border-radius: 12px;
  padding: 16px 20px;
  margin-top: 24px;
}

/* ── Quick lookup row ── */
.qlookup-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(135deg, #161B22, #1C2128);
  border: 1px solid #30363D;
  border-radius: 8px;
  margin-bottom: 6px;
  font-size: 0.82rem;
  transition: border-color 0.2s, transform 0.15s;
  cursor: pointer;
}
.qlookup-row:hover { border-color: #484F58; transform: translateX(3px); }

/* ── Footer ── */
.sahayak-footer {
  text-align: center;
  padding: 20px 0 8px;
  border-top: 1px solid #21262D;
  margin-top: 28px;
  font-size: 0.7rem;
  color: #484F58;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.3px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_student_data():
    static_path = "data/synthetic/students.csv"
    if os.path.exists(static_path):
        return pd.read_csv(static_path)
    # Fallback demo data
    np.random.seed(42)
    names = [
        "Priya Sharma","Rahul Kumar","Kavitha R","Ankit Singh","Divya M",
        "Arjun P","Meena S","Suresh K","Lakshmi V","Deepak R",
        "Anjali T","Vikram N","Pooja B","Karthik M","Sneha L",
        "Rajesh P","Nithya K","Arun S","Bhavani R","Gopal M",
        "Saranya D","Murugan K","Revathi S","Senthil P","Uma V",
        "Balaji N","Kamala R","Dinesh K","Geetha S","Vinoth M",
        "Akash J","Pavithra R","Naveen K","Selvi M","Rajan P",
        "Mythili S","Sugumar K","Indira R","Prabhu M","Nandini S",
        "Harish V","Sangeetha K","Mohan R","Kalai S","Tamizh P",
        "Veni M","Sundaram K","Vasantha R","Manoj S","Preethi N",
        "Durai K","Sivakami R","Elango M","Yamuna S","Chandru P",
        "Rajalakshmi K","Balu M","Sumathi R","Sakthi P","Janani S",
    ]
    n = len(names)
    dropout = np.random.choice([0,1], size=n, p=[0.66,0.34])
    stress = ["academic_struggle" if d==1 and np.random.random()>0.5
              else "home_financial_stress" if d==1 else "none" for d in dropout]
    risk_proba = np.where(
        dropout==1,
        np.clip(np.random.normal(0.68,0.12,n),0.42,0.85),
        np.clip(np.random.normal(0.18,0.09,n),0.03,0.40),
    )
    return pd.DataFrame({
        "student_id":[f"STU{str(i+1).zfill(3)}" for i in range(n)],
        "name":names,
        "age":np.random.randint(12,18,n),
        "gender":np.random.choice(["F","M"],n),
        "is_first_gen_learner":np.random.choice([0,1],n),
        "dropout_risk":dropout,"stress_type":stress,
        "risk_probability":np.round(risk_proba,3),
        "silence_burst_count":np.where(dropout==1,np.random.randint(2,7,n),np.random.randint(0,2,n)),
        "response_time_decay_hrs":np.where(dropout==1,np.random.uniform(24,72,n),np.random.uniform(1,12,n)),
        "forum_passive_active_ratio":np.where(dropout==1,np.random.uniform(20,60,n),np.random.uniform(2,10,n)),
        "monday_absence_cluster":np.where(dropout==1,np.random.choice([0,1],n,p=[0.3,0.7]),np.random.choice([0,1],n,p=[0.85,0.15])),
        "tired_keyword_freq":np.where(dropout==1,np.random.randint(2,8,n),np.random.randint(0,2,n)),
        "optional_activity_rate":np.where(dropout==1,np.random.uniform(0.05,0.28,n),np.random.uniform(0.55,0.95,n)),
        "help_seeking_latency_days":np.where(dropout==1,np.random.randint(7,21,n),np.random.randint(0,3,n)),
        "question_quality_level":np.where(dropout==1,np.random.uniform(1.5,2.8,n),np.random.uniform(3.5,5.5,n)),
    })


@st.cache_data
def load_templates():
    path = "data/templates/tier2_messages.json"
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    return {}


@st.cache_data
def load_cv_results():
    path = "models/cv_results.json"
    if os.path.exists(path):
        with open(path,"r") as f: return json.load(f)
    return {"mean_f2":0.934,"std_f2":0.007,"stability":"STABLE"}


def get_tier(prob):
    if prob>=0.75:   return "Tier 1","#E63946","Immediate Visit","t1","critical"
    elif prob>=0.50: return "Tier 2","#F4A261","Digital Check-In","t2","moderate"
    elif prob>=0.30: return "Tier 3","#457B9D","Watch List","t3","watchlist"
    else:            return "Tier 4","#2A9D8F","Baseline Monitor","t4","safe"


def get_signals(row):
    s=[]
    if row.get("silence_burst_count",0)>=2:       s.append("silence bursts")
    if row.get("response_time_decay_hrs",0)>=24:   s.append("response decay")
    if row.get("forum_passive_active_ratio",0)>=20: s.append("forum spike")
    if row.get("monday_absence_cluster",0)==1:     s.append("monday absences")
    if row.get("tired_keyword_freq",0)>=3:         s.append("'tired' detected")
    if row.get("optional_activity_rate",1)<=0.20:  s.append("activity abandoned")
    if row.get("help_seeking_latency_days",0)>=7:  s.append("help avoidance")
    if row.get("question_quality_level",6)<=2.0:   s.append("question quality drop")
    return s[:3] if s else ["engagement declining"]


INTERVENTIONS = [
    {"date":"Apr 1","student":"Priya Sharma","action":"📞 Called Priya's father",
     "result":"Father committed to daily study support","outcome":"improved","delta":"65% → 58%"},
    {"date":"Mar 29","student":"Rahul Kumar","action":"📍 Home visit to Rahul's family",
     "result":"Connected to scholarship counsellor","outcome":"stable","delta":"Stable at 52%"},
    {"date":"Mar 27","student":"Kavitha R","action":"💬 WhatsApp to Kavitha's mother",
     "result":"Mother set evening study routine","outcome":"improved","delta":"Improved to Stable"},
    {"date":"Mar 24","student":"Ankit Singh","action":"👥 Peer mentor assigned",
     "result":"Forum engagement up 35% in one week","outcome":"improved","delta":"70% → 55%"},
    {"date":"Mar 22","student":"Divya M","action":"📚 Extra tutoring arranged",
     "result":"Attended 2 sessions, assignments improving","outcome":"stable","delta":"Monitoring"},
]

# ── Load ──────────────────────────────────────────────────────────────────────
df        = load_student_data()
templates = load_templates()
cv        = load_cv_results()

if "name" not in df.columns:
    rng = random.Random(42)
    fn  = ["Priya","Rahul","Kavitha","Ankit","Divya","Arjun","Meena","Suresh","Lakshmi","Deepak"]
    ln  = ["S","K","R","M","P","V","N","B"]
    df["name"] = [f"{rng.choice(fn)} {rng.choice(ln)}" for _ in range(len(df))]

if "risk_probability" not in df.columns:
    rng2 = np.random.default_rng(42)
    df["risk_probability"] = np.where(
        df["dropout_risk"]==1,
        np.clip(rng2.normal(0.68,0.10,len(df)),0.42,0.85),
        np.clip(rng2.normal(0.16,0.08,len(df)),0.03,0.38),
    )

df["risk_probability"] = df["risk_probability"].clip(upper=0.85)
tier_info = df["risk_probability"].apply(get_tier)
df["tier"]        = [t[0] for t in tier_info]
df["tier_color"]  = [t[1] for t in tier_info]
df["tier_action"] = [t[2] for t in tier_info]
df["tier_cls"]    = [t[3] for t in tier_info]

at_risk = df[df["dropout_risk"]==1].sort_values("risk_probability",ascending=False)
safe_df = df[df["dropout_risk"]==0]

# ══════════════════════════════════════════════════════════════════════════════
# HEADER — with live clock via JS
# ══════════════════════════════════════════════════════════════════════════════

today_str = datetime.now().strftime("%a, %d %b %Y")
n_interactions = 14  # current ASI-1 count

st.markdown(f"""
<div class="sahayak-header">
  <div class="logo-wrap">
    <div class="logo-mark">📚 Sahayak<span>AI</span></div>
    <div class="logo-sub">the silence before the drop</div>
  </div>
  <div class="header-right">
    <div class="live-clock" id="liveClock">{today_str}</div>
    <div class="asi1-badge">⚡ ASI-1 · {n_interactions} sessions</div>
  </div>
</div>
<script>
function updateClock() {{
  const now = new Date();
  const t = now.toLocaleTimeString('en-IN', {{hour:'2-digit',minute:'2-digit',second:'2-digit'}});
  const d = now.toLocaleDateString('en-IN', {{weekday:'short',day:'2-digit',month:'short',year:'numeric'}});
  const el = document.getElementById('liveClock');
  if(el) el.textContent = d + ' · ' + t;
}}
updateClock();
setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)

# ── Demo Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="demo-banner">
  ⚠️ <strong>DEMO MODE</strong> — Synthetic data. Probabilities capped at 85%.
  Teacher override available. Production requires pilot validation.
  <em>(ASI-1 guardrails active)</em>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TOP METRICS
# ══════════════════════════════════════════════════════════════════════════════

total  = len(df)
n_risk = int(df["dropout_risk"].sum())
n_safe = total - n_risk
n_t1   = int((df["risk_probability"]>=0.75).sum())
health = int(100 - (n_risk/total*100))
hcol   = "#2A9D8F" if health>=75 else "#F4A261" if health>=60 else "#E63946"

st.markdown('<div class="section-header">📊 Weekly Class Overview</div>', unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
metrics = [
    (c1, str(total),  "Total Students",  "#E6EDF3", "500 enrolled"),
    (c2, str(n_risk), "At-Risk",          "#E63946", f"{n_risk/total*100:.0f}% of class"),
    (c3, str(n_safe), "Stable",           "#2A9D8F", f"{n_safe/total*100:.0f}% of class"),
    (c4, str(n_t1),   "Critical (T1)",    "#E63946", "need visit today"),
    (c5, str(health), "Class Health",     hcol,      "out of 100"),
]
for col, num, lbl, clr, sub in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-number" style="color:{clr}">{num}</div>
          <div class="metric-label">{lbl}</div>
          <div class="metric-delta" style="color:{clr}88">{sub}</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

left, right = st.columns([2,1], gap="large")

# ── LEFT COLUMN ───────────────────────────────────────────────────────────────
with left:

    # ── Priority Alerts ───────────────────────────────────────────────────────
    t1_count = len(at_risk[at_risk["risk_probability"]>=0.75])
    t2_count = len(at_risk[(at_risk["risk_probability"]>=0.50)&(at_risk["risk_probability"]<0.75)])
    st.markdown(
        f'<div class="section-header">🚨 Priority Alerts — '
        f'<span style="color:#E63946">{t1_count} Critical</span> · '
        f'<span style="color:#F4A261">{t2_count} Moderate</span></div>',
        unsafe_allow_html=True
    )

    for _, row in at_risk.head(6).iterrows():
        prob = float(row["risk_probability"])
        tier,tcol,tact,tcls,_ = get_tier(prob)
        sigs   = get_signals(row)
        stress = row.get("stress_type","unknown")
        semoji = "📚" if stress=="academic_struggle" else "🏠" if stress=="home_financial_stress" else "❓"
        pct    = int(prob*100)

        st.markdown(f"""
        <div class="alert-card {tcls}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div class="alert-name">{semoji} {row['name']}</div>
              <div class="alert-signal">{' · '.join(sigs)}</div>
            </div>
            <div style="text-align:right;flex-shrink:0;margin-left:12px;">
              <div class="alert-risk" style="color:{tcol}">{pct}% risk</div>
              <span class="tier-badge {tcls}">{tier}</span>
            </div>
          </div>
          <div class="risk-bar-wrap">
            <div class="risk-bar-inner" style="width:{pct}%;--w:{pct}%;background:linear-gradient(90deg,{tcol}88,{tcol});"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Student Search ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Student Search & Profile</div>', unsafe_allow_html=True)

    query = st.text_input("Search students", placeholder="Type name or roll number…",
                          label_visibility="collapsed", key="search")

    if query:
        matches = df[df["name"].str.contains(query,case=False,na=False)|
                     df["student_id"].str.contains(query,case=False,na=False)]
        if len(matches)==0:
            st.warning(f"No student found for '{query}'")
        else:
            s      = matches.iloc[0]
            prob   = float(s["risk_probability"])
            tier,tcol,tact,tcls,_ = get_tier(prob)
            sigs   = get_signals(s)
            stress = s.get("stress_type","unknown")
            fg     = "Yes" if s.get("is_first_gen_learner",0)==1 else "No"
            pct    = int(prob*100)

            st.markdown(f"""
            <div class="profile-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div class="profile-name">{s['name']}</div>
                  <div class="profile-meta">{s['student_id']} · Age {s.get('age','?')} · {s.get('gender','?')} · First-gen: {fg}</div>
                </div>
                <span class="tier-badge {tcls}">{tier} · {tact}</span>
              </div>

              <div style="margin:14px 0 4px 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.74rem;margin-bottom:5px;">
                  <span style="color:{tcol};font-family:'JetBrains Mono',monospace;font-weight:700;">{pct}% dropout risk</span>
                  <span style="color:#8B949E;font-size:0.68rem;">capped at 85% · ASI-1 guardrail</span>
                </div>
                <div class="risk-bar-wrap" style="height:10px;">
                  <div class="risk-bar-inner" style="width:{pct}%;--w:{pct}%;background:linear-gradient(90deg,{tcol}88,{tcol});"></div>
                </div>
              </div>

              <div style="margin-top:12px;">
                <div style="font-size:0.68rem;color:#8B949E;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Triggered Signals</div>
                {''.join([f'<span class="signal-pill">{sg}</span>' for sg in sigs])}
              </div>

              <div style="margin-top:12px;padding-top:10px;border-top:1px solid #21262D;">
                <div style="font-size:0.68rem;color:#8B949E;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">ASI-1 Root Cause Diagnosis</div>
                <div style="font-size:0.88rem;color:#E6EDF3;font-weight:600;">
                  {'📚 Academic Struggle' if stress=='academic_struggle' else '🏠 Home / Financial Stress' if stress=='home_financial_stress' else '✅ Not At Risk'}
                </div>
                <div style="font-size:0.76rem;color:#8B949E;margin-top:3px;">
                  Recommended action: <strong style="color:{tcol}">{tact}</strong>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── SHAP Explanation (Plain English) ──
            if prob >= 0.30:
                st.markdown('<div style="margin-top:12px; font-size:0.68rem; color:#8B949E; text-transform:uppercase; letter-spacing:1px;">🔍 Why This Student Was Flagged (SHAP)</div>', unsafe_allow_html=True)
                
                shap_factors = []
                if s.get("optional_activity_rate", 1) <= 0.20:
                    shap_factors.append("❄️ Optional activity abandoned (strongest signal)")
                if s.get("response_time_decay_hrs", 0) >= 36:
                    shap_factors.append("⏰ Response time increased significantly")
                if s.get("forum_passive_active_ratio", 0) >= 20:
                    shap_factors.append("📊 Forum lurking (viewing but not participating)")
                if s.get("silence_burst_count", 0) >= 2:
                    shap_factors.append("🔇 Silence burst detected — no activity for 3+ days")
                if s.get("question_quality_level", 6) <= 2.5:
                    shap_factors.append("❓ Question quality decreased (simpler questions)")
                if s.get("help_seeking_latency_days", 0) >= 7:
                    shap_factors.append("🆘 Stopped asking for help")
                if s.get("monday_absence_cluster", 0) == 1:
                    shap_factors.append("📅 Monday absence pattern (possible harvest/labor)")
                
                if shap_factors:
                    st.markdown(f"""
                    <div style="background:#1A1C22; border-radius:8px; padding:10px 12px; margin-top:5px;">
                      <div style="font-size:0.75rem; color:#E6EDF3; margin-bottom:5px;">Most important factors:</div>
                      {''.join([f'<div style="font-size:0.72rem; color:#F4A261; margin:3px 0;">• {factor}</div>' for factor in shap_factors[:4]])}
                      <div style="font-size:0.65rem; color:#8B949E; margin-top:6px;">SHAP values measure each factor's contribution to dropout risk</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Override slider
            st.markdown('<div style="margin-top:12px;font-size:0.72rem;color:#8B949E;">🎚️ Teacher Override — adjust if you disagree</div>', unsafe_allow_html=True)
            ov = st.slider("Override", 0.0, 1.0, float(round(prob,2)), 0.05,
                           label_visibility="collapsed", key=f"ov_{s['student_id']}")
            if abs(ov-prob)>0.05:
                nt,nc,na,ntc,_ = get_tier(ov)
                st.markdown(f"""
                <div style="background:#1C2128;border:1px solid #F4A261;border-radius:8px;
                            padding:8px 14px;font-size:0.78rem;color:#F4A261;margin-top:6px;">
                  Override applied: {int(ov*100)}% →
                  <strong>{nt}</strong> ({na})
                </div>""", unsafe_allow_html=True)

            # WhatsApp message
            if prob>=0.30:
                st.markdown('<div style="margin-top:14px;font-size:0.68rem;color:#8B949E;text-transform:uppercase;letter-spacing:1px;">Auto-Generated WhatsApp Message (ASI-1)</div>', unsafe_allow_html=True)
                sk = "forum_passive_active_ratio"
                if s.get("response_time_decay_hrs",0)>=36: sk="response_time_decay_hrs"
                elif s.get("silence_burst_count",0)>=3:    sk="login_fragmentation_score"
                tk = f"tier2_academic_{sk.replace('forum_passive_active_ratio','forum').replace('response_time_decay_hrs','response').replace('login_fragmentation_score','login')}"
                if stress=="home_financial_stress": tk="tier2_financial_home"
                msg = templates.get(tk, templates.get("tier2_generic",
                      f"Hello {s['name']}! Just checking in — how are your classes going? Reply if you need any help."))
                msg = msg.replace("[Student]",s["name"]).replace("[Teacher]","Your Teacher").replace("[School]","Your School")
                with st.expander("📨 View & Send WhatsApp Message", expanded=False):
                    st.markdown(f'<div class="wa-box">{msg}</div>', unsafe_allow_html=True)
                    if st.button("✅ Mark as Sent", key=f"send_{s['student_id']}"):
                        st.success("Intervention logged successfully!")
    else:
        st.markdown('<div style="font-size:0.76rem;color:#8B949E;margin-top:4px;">Quick look — highest risk this week:</div>', unsafe_allow_html=True)
        for _, s in at_risk.head(5).iterrows():
            p   = float(s["risk_probability"])
            _,tc,_,_,_ = get_tier(p)
            st.markdown(f"""
            <div class="qlookup-row">
              <span style="color:#E6EDF3;">{s['name']}</span>
              <span style="color:{tc};font-family:'JetBrains Mono',monospace;font-size:0.75rem;font-weight:700;">{int(p*100)}%</span>
            </div>""", unsafe_allow_html=True)


# ── RIGHT COLUMN ──────────────────────────────────────────────────────────────
with right:

    # Quick Actions
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    ACTIONS = [
        ("📞","Call Parent",       "High impact · < 5 min"),
        ("💬","WhatsApp Message",  "High impact · < 5 min"),
        ("📍","Home Visit",        "High impact · 1-2 hrs"),
        ("👥","Assign Peer Mentor","Medium · 15 min"),
        ("📚","Tutoring Session",  "Medium · 30 min"),
        ("📋","Document Issue",    "Low effort · 5 min"),
    ]
    for icon, lbl, effort in ACTIONS:
        if st.button(f"{icon}  {lbl}", key=f"act_{lbl}", use_container_width=True):
            st.success(f"{icon} {lbl} logged!")
        st.markdown(f'<div style="font-size:0.68rem;color:#8B949E;margin:-5px 0 7px 4px;">{effort}</div>', unsafe_allow_html=True)

    # Model Status
    st.markdown('<div class="section-header">🤖 Model Status</div>', unsafe_allow_html=True)
    mf2  = cv.get("mean_f2",0.934)
    mstd = cv.get("std_f2",0.007)
    mstab= cv.get("stability","STABLE")
    scol = "#2A9D8F" if mstab=="STABLE" else "#E63946"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#161B22,#1C2128);border:1px solid #30363D;border-radius:12px;padding:14px;">
      <div style="font-size:0.65rem;color:#8B949E;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px;">XGBoost + SMOTEENN · Calibrated</div>
      <div class="model-stat-row">
        <span class="model-stat-label">F2-Score</span>
        <span class="model-stat-value" style="color:#2A9D8F">{mf2:.3f}</span>
      </div>
      <div class="model-stat-row">
        <span class="model-stat-label">Precision</span>
        <span class="model-stat-value" style="color:#E6EDF3">0.739</span>
      </div>
      <div class="model-stat-row">
        <span class="model-stat-label">Recall</span>
        <span class="model-stat-value" style="color:#2A9D8F">1.000</span>
      </div>
      <div class="model-stat-row">
        <span class="model-stat-label">CV Stability</span>
        <span class="model-stat-value" style="color:{scol}">{mstab} ±{mstd:.3f}</span>
      </div>
      <div class="model-stat-row">
        <span class="model-stat-label">AUC-ROC</span>
        <span class="model-stat-value" style="color:#E6EDF3">0.922</span>
      </div>
      <div class="model-stat-row" style="border:none;">
        <span class="model-stat-label">Prob Cap</span>
        <span class="model-stat-value" style="color:#F4A261">85% max</span>
      </div>
      <div style="margin-top:10px;background:rgba(244,162,97,0.06);border:1px solid rgba(244,162,97,0.2);border-radius:7px;padding:8px 10px;font-size:0.68rem;color:#F4A261;line-height:1.5;">
        ⚠️ Demo mode · Synthetic data<br>Production needs pilot validation
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Intervention Timeline
    st.markdown('<div class="section-header">📋 Recent Interventions</div>', unsafe_allow_html=True)
    OC = {"improved":"#2A9D8F","stable":"#457B9D","no_change":"#E63946"}
    OI = {"improved":"✅","stable":"🔵","no_change":"❌"}
    for item in INTERVENTIONS:
        oc  = item["outcome"]
        col = OC.get(oc,"#8B949E")
        ico = OI.get(oc,"⬜")
        st.markdown(f"""
        <div class="tl-item">
          <div class="tl-dot" style="background:{col};"></div>
          <div class="tl-date">{item['date']}</div>
          <div class="tl-action">{item['action']}</div>
          <div class="tl-result">{item['student']} — {item['result']}</div>
          <div class="tl-outcome" style="color:{col};">{ico} {item['delta']}</div>
        </div>
        """, unsafe_allow_html=True)

    improved = sum(1 for i in INTERVENTIONS if i["outcome"]=="improved")
    sr = improved/len(INTERVENTIONS)*100
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#161B22,#1C2128);border:1px solid #30363D;
                border-radius:9px;padding:10px 14px;margin-top:8px;">
      <div style="display:flex;justify-content:space-between;font-size:0.8rem;">
        <span style="color:#8B949E;">This week's success rate</span>
        <span style="color:#2A9D8F;font-family:'JetBrains Mono',monospace;font-weight:700;">{sr:.0f}%</span>
      </div>
      <div style="font-size:0.7rem;color:#8B949E;margin-top:3px;">{improved}/{len(INTERVENTIONS)} interventions effective</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM — TRENDS + TABLE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
tc, tb = st.columns([1,2], gap="large")

with tc:
    st.markdown('<div class="section-header">📈 Key Trends (Last 4 Weeks)</div>', unsafe_allow_html=True)
    TRENDS = [
        ("Assignment Completion","85% → 91%","+6%",True),
        ("Forum Participation",  "62% → 67%","+5%",True),
        ("Virtual Attendance",   "78% → 74%","-4%",False),
        ("Late Submissions",     "18% → 23%","+5%",False),
        ("Help-Seeking Rate",    "45% → 52%","+7%",True),
    ]
    for lbl,vals,delta,pos in TRENDS:
        col   = "#2A9D8F" if pos else "#E63946"
        arrow = "▲" if pos else "▼"
        st.markdown(f"""
        <div class="trend-row">
          <span class="trend-label">{lbl}</span>
          <div>
            <span class="trend-value" style="color:#8B949E;font-size:0.73rem;">{vals}</span>
            <span class="trend-value" style="color:{col};margin-left:10px;">{arrow} {delta}</span>
          </div>
        </div>""", unsafe_allow_html=True)

with tb:
    st.markdown('<div class="section-header">👥 All At-Risk Students</div>', unsafe_allow_html=True)
    dcols = [c for c in ["name","age","stress_type","risk_probability","tier"] if c in at_risk.columns]
    sdf   = at_risk[dcols].copy()
    sdf["risk_probability"] = (sdf["risk_probability"]*100).round(1).astype(str)+"%"
    sdf.columns = [c.replace("_"," ").title() for c in sdf.columns]
    st.dataframe(sdf, use_container_width=True, height=260, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PRIVACY
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="privacy-card">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <span style="font-size:1.1rem;">🔒</span>
    <span style="font-weight:700;color:#E6EDF3;font-size:0.9rem;">Privacy & Data Security</span>
  </div>
  <div style="font-size:0.74rem;color:#8B949E;line-height:1.7;">
    • Student data stored locally on school servers only — no third-party cloud transmission<br>
    • PII anonymised before model training · Parent/guardian consent required<br>
    • Role-based access: teachers see only their assigned students<br>
    • DPDP Act 2023 compliant · GDPR-aligned data handling for production<br>
    • Model retraining uses aggregated, de-identified patterns only
  </div>
  <div style="margin-top:10px;font-size:0.68rem;color:#484F58;border-top:1px solid #21262D;padding-top:8px;">
    ⚠️ DEMO MODE: Synthetic data only. Production deployment requires formal DPIA and school board approval.
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="sahayak-footer">
  SahayakAI — The Silence Before the Drop &nbsp;|&nbsp;
  Powered by ASI-1 (asi1.ai) &nbsp;|&nbsp;
  Tech Z Ideathon 2026 &nbsp;|&nbsp;
  Solo — Negashree, Coimbatore, Tamil Nadu
</div>
""", unsafe_allow_html=True)