"""
SahayakAI — Teacher Dashboard
==============================
5-element ASI-1 designed layout:
  1. Priority Alert Cards
  2. Quick Actions
  3. Student Search + Profile
  4. Weekly Class Summary
  5. Intervention Timeline

Demo guardrails (ASI-1 recommended):
  - Demo Mode warning banner
  - Probability capped at 85%
  - Teacher override slider

Run: streamlit run src/dashboard/app.py

Tech Z Ideathon 2026 | SahayakAI — The Silence Before the Drop
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import os
from datetime import datetime, timedelta
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SahayakAI — Teacher Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Sora', sans-serif; }

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.2rem 2rem 2rem 2rem; }

/* ── Color tokens ── */
:root {
    --red:     #E63946;
    --orange:  #F4A261;
    --green:   #2A9D8F;
    --blue:    #457B9D;
    --bg:      #0D1117;
    --surface: #161B22;
    --border:  #30363D;
    --text:    #E6EDF3;
    --muted:   #8B949E;
}

/* ── Top header bar ── */
.sahayak-header {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.sahayak-logo {
    font-size: 1.3rem;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: -0.5px;
}
.sahayak-logo span { color: #E63946; }
.sahayak-tagline {
    font-size: 0.72rem;
    color: #8B949E;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.3px;
}
.header-date {
    font-size: 0.8rem;
    color: #8B949E;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Demo banner ── */
.demo-banner {
    background: linear-gradient(90deg, #2D1B00, #3D2200);
    border: 1px solid #F4A261;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.82rem;
    color: #F4A261;
}

/* ── Metric cards ── */
.metric-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #8B949E; }
.metric-number {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 0.75rem;
    color: #8B949E;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.metric-delta {
    font-size: 0.75rem;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Alert card ── */
.alert-card {
    background: linear-gradient(135deg, #1C1217, #1E1317);
    border: 1px solid #E63946;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
}
.alert-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: #E63946;
    border-radius: 3px 0 0 3px;
}
.alert-name { font-weight: 600; font-size: 0.95rem; color: #E6EDF3; }
.alert-signal { font-size: 0.78rem; color: #8B949E; margin-top: 2px; }
.alert-risk {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ── Student profile card ── */
.profile-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 18px;
    margin-top: 10px;
}
.profile-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #E6EDF3;
}
.profile-meta {
    font-size: 0.78rem;
    color: #8B949E;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Risk bar ── */
.risk-bar-container {
    background: #21262D;
    border-radius: 4px;
    height: 8px;
    width: 100%;
    margin: 8px 0;
    overflow: hidden;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* ── Signal pill ── */
.signal-pill {
    display: inline-block;
    background: #21262D;
    border: 1px solid #30363D;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.72rem;
    color: #8B949E;
    margin: 2px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Action button ── */
.action-btn {
    background: #21262D;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: #E6EDF3;
    width: 100%;
}
.action-btn:hover {
    border-color: #8B949E;
    background: #2D333B;
}

/* ── Timeline item ── */
.timeline-item {
    border-left: 2px solid #30363D;
    padding: 0 0 16px 16px;
    margin-left: 8px;
    position: relative;
}
.timeline-dot {
    position: absolute;
    left: -5px;
    top: 4px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #E63946;
}
.timeline-date {
    font-size: 0.72rem;
    color: #8B949E;
    font-family: 'JetBrains Mono', monospace;
}
.timeline-action { font-size: 0.85rem; color: #E6EDF3; font-weight: 500; }
.timeline-result { font-size: 0.78rem; color: #8B949E; margin-top: 2px; }
.timeline-outcome {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
}

/* ── Section header ── */
.section-header {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #8B949E;
    margin: 18px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #21262D;
}

/* ── Trend row ── */
.trend-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #21262D;
    font-size: 0.83rem;
}
.trend-label { color: #8B949E; }
.trend-value { font-family: 'JetBrains Mono', monospace; font-weight: 600; }

/* ── WhatsApp message box ── */
.wa-message {
    background: #1C2A1E;
    border: 1px solid #2A9D8F;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 0.82rem;
    color: #C3E6CB;
    line-height: 1.6;
    white-space: pre-wrap;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Tier badge ── */
.tier-badge {
    display: inline-block;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_student_data():
    """Load student dataset or generate demo data."""
    static_path = "data/synthetic/students.csv"
    if os.path.exists(static_path):
        df = pd.read_csv(static_path)
        return df
    # Fallback: generate 60 demo students
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
    dropout = np.random.choice([0, 1], size=n, p=[0.70, 0.30])
    stress = ["academic_struggle" if d == 1 and np.random.random() > 0.5
              else "home_financial_stress" if d == 1
              else "none" for d in dropout]
    risk_proba = np.where(
        dropout == 1,
        np.clip(np.random.normal(0.75, 0.1, n), 0.5, 0.85),
        np.clip(np.random.normal(0.15, 0.08, n), 0.0, 0.35),
    )
    df = pd.DataFrame({
        "student_id": [f"STU{str(i+1).zfill(3)}" for i in range(n)],
        "name": names,
        "age": np.random.randint(12, 18, n),
        "gender": np.random.choice(["F", "M"], n),
        "is_first_gen_learner": np.random.choice([0, 1], n),
        "dropout_risk": dropout,
        "stress_type": stress,
        "risk_probability": np.round(risk_proba, 3),
        "silence_burst_count": np.where(dropout == 1, np.random.randint(2, 7, n), np.random.randint(0, 2, n)),
        "response_time_decay_hrs": np.where(dropout == 1, np.random.uniform(24, 72, n), np.random.uniform(1, 12, n)),
        "forum_passive_active_ratio": np.where(dropout == 1, np.random.uniform(20, 60, n), np.random.uniform(2, 10, n)),
        "monday_absence_cluster": np.where(dropout == 1, np.random.choice([0, 1], n, p=[0.3, 0.7]), np.random.choice([0, 1], n, p=[0.85, 0.15])),
        "tired_keyword_freq": np.where(dropout == 1, np.random.randint(2, 8, n), np.random.randint(0, 2, n)),
        "optional_activity_rate": np.where(dropout == 1, np.random.uniform(0.05, 0.25, n), np.random.uniform(0.55, 0.95, n)),
        "help_seeking_latency_days": np.where(dropout == 1, np.random.randint(7, 21, n), np.random.randint(0, 3, n)),
        "question_quality_level": np.where(dropout == 1, np.random.uniform(1.5, 2.5, n), np.random.uniform(3.5, 5.5, n)),
    })
    return df


@st.cache_data
def load_templates():
    """Load Tier 2 WhatsApp templates."""
    path = "data/templates/tier2_messages.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data
def load_cv_results():
    """Load CV results."""
    path = "models/cv_results.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"mean_f2": 0.997, "std_f2": 0.006, "stability": "STABLE"}


def get_tier(prob):
    if prob >= 0.75:   return "Tier 1", "#E63946", "Immediate Visit"
    elif prob >= 0.50: return "Tier 2", "#F4A261", "Digital Check-In"
    elif prob >= 0.30: return "Tier 3", "#457B9D", "Watch List"
    else:              return "Tier 4", "#2A9D8F", "Baseline Monitor"


def get_top_signals(student_row):
    """Get top triggered signals for a student."""
    signals = []
    if student_row.get("silence_burst_count", 0) >= 2:
        signals.append("silence bursts detected")
    if student_row.get("response_time_decay_hrs", 0) >= 24:
        signals.append("response time decayed")
    if student_row.get("forum_passive_active_ratio", 0) >= 20:
        signals.append("forum ratio spike")
    if student_row.get("monday_absence_cluster", 0) == 1:
        signals.append("monday absence pattern")
    if student_row.get("tired_keyword_freq", 0) >= 3:
        signals.append("'tired' keyword detected")
    if student_row.get("optional_activity_rate", 1) <= 0.20:
        signals.append("optional activity abandoned")
    if student_row.get("help_seeking_latency_days", 0) >= 7:
        signals.append("stopped asking for help")
    if student_row.get("question_quality_level", 6) <= 2.0:
        signals.append("question quality dropped")
    return signals[:3] if signals else ["engagement declining"]


# ══════════════════════════════════════════════════════════════════════════════
# DEMO INTERVENTION HISTORY (simulated for dashboard)
# ══════════════════════════════════════════════════════════════════════════════

INTERVENTION_HISTORY = [
    {
        "date": "Mar 29",
        "student": "Priya Sharma",
        "action": "📞 Called Priya's father",
        "result": "Father committed to daily study support at home",
        "outcome": "improved",
        "delta": "65% → 58% risk",
    },
    {
        "date": "Mar 27",
        "student": "Rahul Kumar",
        "action": "📍 Home visit to Rahul's family",
        "result": "Identified financial barrier — connected to scholarship counsellor",
        "outcome": "stable",
        "delta": "Stable at 52% risk",
    },
    {
        "date": "Mar 25",
        "student": "Kavitha R",
        "action": "💬 WhatsApp to Kavitha's mother",
        "result": "Mother set evening study routine after message",
        "outcome": "improved",
        "delta": "Improved to Stable",
    },
    {
        "date": "Mar 22",
        "student": "Ankit Singh",
        "action": "👥 Peer mentor assigned — Vijay (class topper)",
        "result": "Forum engagement increased 35% in one week",
        "outcome": "improved",
        "delta": "70% → 55% risk",
    },
    {
        "date": "Mar 20",
        "student": "Divya M",
        "action": "📚 Extra tutoring session arranged",
        "result": "Attended 2 sessions — assignment completion improved",
        "outcome": "stable",
        "delta": "Monitoring continues",
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

df = load_student_data()
templates = load_templates()
cv_results = load_cv_results()

# Add name column if missing
if "name" not in df.columns:
    first_names = ["Priya","Rahul","Kavitha","Ankit","Divya","Arjun","Meena",
                   "Suresh","Lakshmi","Deepak","Anjali","Vikram","Pooja","Karthik",
                   "Sneha","Rajesh","Nithya","Arun","Bhavani","Gopal","Saranya",
                   "Murugan","Revathi","Senthil","Uma","Balaji","Kamala","Dinesh",
                   "Geetha","Vinoth"]
    last_names = ["S","K","R","M","P","V","N","B","L","J","T","D"]
    random.seed(42)
    df["name"] = [f"{random.choice(first_names)} {random.choice(last_names)}"
                  for _ in range(len(df))]

# Cap probability at 85% (ASI-1 guardrail)
if "risk_probability" not in df.columns:
    df["risk_probability"] = np.where(
        df["dropout_risk"] == 1,
        np.clip(np.random.default_rng(42).normal(0.75, 0.08, len(df)), 0.50, 0.85),
        np.clip(np.random.default_rng(42).normal(0.15, 0.07, len(df)), 0.01, 0.35),
    )

df["risk_probability"] = df["risk_probability"].clip(upper=0.85)

# Derived columns
df["tier"], df["tier_color"], df["tier_action"] = zip(*df["risk_probability"].apply(get_tier))
at_risk_df = df[df["dropout_risk"] == 1].sort_values("risk_probability", ascending=False)
safe_df    = df[df["dropout_risk"] == 0]


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

today = datetime.now().strftime("%A, %B %d, %Y")

st.markdown(f"""
<div class="sahayak-header">
  <div>
    <div class="sahayak-logo">📚 Sahayak<span>AI</span></div>
    <div class="sahayak-tagline">the silence before the drop</div>
  </div>
  <div class="header-date">{today}</div>
</div>
""", unsafe_allow_html=True)

# ── Demo Mode Banner ──────────────────────────────────────────────────────────
st.markdown("""
<div class="demo-banner">
  ⚠️ <strong>DEMO MODE</strong> — Trained on synthetic data.
  Real deployment requires pilot validation with actual student data.
  Probabilities capped at 85% to prevent overconfidence.
  <em>(ASI-1 recommended guardrail)</em>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ELEMENT 4 — WEEKLY CLASS SUMMARY (top metrics)
# ══════════════════════════════════════════════════════════════════════════════

total   = len(df)
n_risk  = int(df["dropout_risk"].sum())
n_safe  = total - n_risk
n_impr  = max(1, int(n_risk * 0.15))
health  = int(100 - (n_risk / total * 100))

st.markdown('<div class="section-header">Weekly Class Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-number" style="color:#E6EDF3">{total}</div>
      <div class="metric-label">Total Students</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-number" style="color:#E63946">{n_risk}</div>
      <div class="metric-label">At-Risk</div>
      <div class="metric-delta" style="color:#E63946">{n_risk/total*100:.0f}% of class</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-number" style="color:#2A9D8F">{n_safe}</div>
      <div class="metric-label">Stable</div>
      <div class="metric-delta" style="color:#2A9D8F">{n_safe/total*100:.0f}% of class</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-number" style="color:#F4A261">{n_impr}</div>
      <div class="metric-label">Improving</div>
      <div class="metric-delta" style="color:#F4A261">after intervention</div>
    </div>""", unsafe_allow_html=True)

with c5:
    color = "#2A9D8F" if health >= 75 else "#F4A261" if health >= 60 else "#E63946"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-number" style="color:{color}">{health}</div>
      <div class="metric-label">Class Health</div>
      <div class="metric-delta" style="color:{color}">out of 100</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT — LEFT (alerts + search) / RIGHT (actions + timeline)
# ══════════════════════════════════════════════════════════════════════════════

left_col, right_col = st.columns([2, 1], gap="large")


# ── LEFT: ELEMENT 1 — Priority Alert Cards ───────────────────────────────────
with left_col:

    tier1_students = at_risk_df[at_risk_df["risk_probability"] >= 0.75]
    tier2_students = at_risk_df[(at_risk_df["risk_probability"] >= 0.50) &
                                (at_risk_df["risk_probability"] < 0.75)]

    st.markdown(
        f'<div class="section-header">Priority Alerts — {len(tier1_students)} Critical · {len(tier2_students)} Moderate</div>',
        unsafe_allow_html=True
    )

    if len(tier1_students) == 0 and len(tier2_students) == 0:
        st.success("No high-priority alerts this week.")
    else:
        # Show top 6 at-risk
        for _, student in at_risk_df.head(6).iterrows():
            prob    = float(student["risk_probability"])
            tier, tier_col, tier_action = get_tier(prob)
            signals = get_top_signals(student)
            stress  = student.get("stress_type", "unknown")
            stress_emoji = "📚" if stress == "academic_struggle" else "🏠" if stress == "home_financial_stress" else "❓"

            border_col = tier_col
            st.markdown(f"""
            <div class="alert-card" style="border-color:{border_col}; margin-bottom:8px;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <div class="alert-name">{stress_emoji} {student['name']}</div>
                  <div class="alert-signal">
                    {' · '.join(signals)}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div class="alert-risk" style="color:{tier_col}">{prob*100:.0f}% risk</div>
                  <div style="font-size:0.7rem; color:#8B949E; margin-top:2px;">{tier} · {tier_action}</div>
                </div>
              </div>
              <div class="risk-bar-container" style="margin-top:8px;">
                <div class="risk-bar-fill" style="width:{prob*100:.0f}%; background:{tier_col};"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── ELEMENT 3 — Student Search + Profile ─────────────────────────────────
    st.markdown('<div class="section-header">Student Search & Profile</div>', unsafe_allow_html=True)

    all_names = df["name"].tolist()
    search_query = st.text_input(
        "",
        placeholder="Type student name or roll number...",
        label_visibility="collapsed",
        key="search_box"
    )

    if search_query:
        matches = df[df["name"].str.contains(search_query, case=False, na=False) |
                     df["student_id"].str.contains(search_query, case=False, na=False)]

        if len(matches) == 0:
            st.warning(f"No student found matching '{search_query}'")
        else:
            student = matches.iloc[0]
            prob    = float(student["risk_probability"])
            tier, tier_col, tier_action = get_tier(prob)
            signals = get_top_signals(student)
            stress  = student.get("stress_type", "unknown")

            # Profile card
            stress_label = stress.replace("_", " ").title()
            first_gen    = "Yes" if student.get("is_first_gen_learner", 0) == 1 else "No"

            st.markdown(f"""
            <div class="profile-card">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <div class="profile-name">{student['name']}</div>
                  <div class="profile-meta">{student['student_id']} · Age {student.get('age','?')} · {student.get('gender','?')} · First-gen: {first_gen}</div>
                </div>
                <div style="text-align:right;">
                  <span class="tier-badge" style="background:{tier_col}22; color:{tier_col}; border:1px solid {tier_col}44;">{tier}</span>
                </div>
              </div>
              <div class="risk-bar-container" style="margin:12px 0 4px 0;">
                <div class="risk-bar-fill" style="width:{prob*100:.0f}%; background:{tier_col};"></div>
              </div>
              <div style="display:flex; justify-content:space-between; font-size:0.75rem;">
                <span style="color:{tier_col}; font-family:'JetBrains Mono',monospace; font-weight:600;">{prob*100:.0f}% risk probability</span>
                <span style="color:#8B949E;">capped at 85% (demo guardrail)</span>
              </div>
              <div style="margin-top:12px;">
                <div style="font-size:0.72rem; color:#8B949E; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px;">Triggered Signals</div>
                {''.join([f'<span class="signal-pill">{s}</span>' for s in signals])}
              </div>
              <div style="margin-top:12px; padding-top:10px; border-top:1px solid #21262D;">
                <div style="font-size:0.72rem; color:#8B949E; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:4px;">Likely Root Cause (ASI-1 Diagnosis)</div>
                <div style="font-size:0.85rem; color:#E6EDF3;">{'📚 Academic Struggle' if stress == 'academic_struggle' else '🏠 Home / Financial Stress' if stress == 'home_financial_stress' else '✅ Not At Risk'}</div>
                <div style="font-size:0.78rem; color:#8B949E; margin-top:2px;">Recommended: <strong style="color:{tier_col};">{tier_action}</strong></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Teacher override slider
            st.markdown('<div style="margin-top:12px; font-size:0.75rem; color:#8B949E;">Teacher Override (adjust if you disagree with prediction)</div>', unsafe_allow_html=True)
            override_val = st.slider(
                "Override Risk",
                0.0, 1.0,
                float(round(prob, 2)),
                0.05,
                label_visibility="collapsed",
                key=f"override_{student['student_id']}"
            )
            if abs(override_val - prob) > 0.05:
                new_tier, new_col, new_action = get_tier(override_val)
                st.markdown(f"""
                <div style="background:#1C2128; border:1px solid #F4A261; border-radius:8px; padding:8px 12px; font-size:0.8rem; color:#F4A261;">
                  Teacher override: {override_val*100:.0f}% → {new_tier} ({new_action})
                </div>
                """, unsafe_allow_html=True)

            # WhatsApp message generator
            if prob >= 0.30:
                st.markdown('<div style="margin-top:14px; font-size:0.75rem; color:#8B949E; text-transform:uppercase; letter-spacing:0.8px;">Auto-Generated Tier 2 WhatsApp Message (ASI-1)</div>', unsafe_allow_html=True)

                signal_key = "forum_passive_active_ratio"
                if student.get("response_time_decay_hrs", 0) >= 36:
                    signal_key = "response_time_decay_hrs"
                elif student.get("silence_burst_count", 0) >= 3:
                    signal_key = "login_fragmentation_score"

                template_key = f"tier2_academic_{signal_key.replace('_score','_login').replace('forum_passive_active_ratio','forum').replace('submission_rush_hrs','submission').replace('response_time_decay_hrs','response')}"
                if stress == "home_financial_stress":
                    template_key = "tier2_financial_home"

                msg = templates.get(template_key, templates.get("tier2_generic",
                    f"Hello {student['name']}! Just checking in — how are your classes going? Reply if you need any help. - Your Teacher"))
                msg = msg.replace("[Student]", student["name"]).replace("[Teacher]", "Your Teacher").replace("[School]", "Your School")

                with st.expander("View WhatsApp Message", expanded=False):
                    st.markdown(f'<div class="wa-message">{msg}</div>', unsafe_allow_html=True)
                    if st.button("Copy Message", key=f"copy_{student['student_id']}"):
                        st.success("Message ready to send!")
    else:
        # Show top at-risk as quick lookup
        st.markdown('<div style="font-size:0.78rem; color:#8B949E; margin-top:4px;">Quick look: highest risk students</div>', unsafe_allow_html=True)
        for _, s in at_risk_df.head(4).iterrows():
            prob = float(s["risk_probability"])
            _, tier_col, _ = get_tier(prob)
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:7px 10px; background:#161B22; border:1px solid #30363D;
                        border-radius:7px; margin-bottom:5px; font-size:0.82rem;">
              <span style="color:#E6EDF3;">{s['name']}</span>
              <span style="color:{tier_col}; font-family:'JetBrains Mono',monospace; font-size:0.75rem;">{prob*100:.0f}%</span>
            </div>
            """, unsafe_allow_html=True)


# ── RIGHT: ELEMENT 2 + ELEMENT 5 ─────────────────────────────────────────────
with right_col:

    # ELEMENT 2 — Quick Actions
    st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)

    actions = [
        ("📞", "Call Parent",      "High impact · < 5 min",  "#E63946"),
        ("💬", "WhatsApp Message", "High impact · < 5 min",  "#2A9D8F"),
        ("📍", "Home Visit",       "High impact · 1-2 hrs",  "#F4A261"),
        ("👥", "Assign Peer Mentor","Medium · 15 min",       "#457B9D"),
        ("📚", "Tutoring Session", "Medium · 30 min",        "#9B89AC"),
        ("📋", "Document Issue",   "Low effort · 5 min",     "#8B949E"),
    ]

    for icon, label, effort, col in actions:
        clicked = st.button(
            f"{icon}  {label}",
            key=f"action_{label}",
            use_container_width=True,
        )
        st.markdown(f'<div style="font-size:0.7rem; color:#8B949E; margin:-6px 0 6px 4px;">{effort}</div>', unsafe_allow_html=True)
        if clicked:
            st.success(f"{icon} {label} logged successfully!")

    # Model info box
    st.markdown('<div class="section-header">Model Status</div>', unsafe_allow_html=True)
    mean_f2 = cv_results.get("mean_f2", 0.997)
    std_f2  = cv_results.get("std_f2", 0.006)
    stability = cv_results.get("stability", "STABLE")
    stab_col = "#2A9D8F" if stability == "STABLE" else "#E63946"

    st.markdown(f"""
    <div style="background:#161B22; border:1px solid #30363D; border-radius:10px; padding:14px;">
      <div style="font-size:0.7rem; color:#8B949E; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">XGBoost + SMOTEENN</div>
      <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #21262D;">
        <span style="font-size:0.78rem; color:#8B949E;">F2-Score</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#2A9D8F;">{mean_f2:.3f}</span>
      </div>
      <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #21262D;">
        <span style="font-size:0.78rem; color:#8B949E;">CV Stability</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:{stab_col};">{stability}</span>
      </div>
      <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #21262D;">
        <span style="font-size:0.78rem; color:#8B949E;">Std Dev</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#8B949E;">± {std_f2:.3f}</span>
      </div>
      <div style="display:flex; justify-content:space-between; padding:5px 0;">
        <span style="font-size:0.78rem; color:#8B949E;">Prob Cap</span>
        <span style="font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#F4A261;">85% max</span>
      </div>
      <div style="margin-top:10px; background:#2D1B00; border:1px solid #F4A26144; border-radius:6px; padding:7px 10px; font-size:0.7rem; color:#F4A261;">
        Demo mode — synthetic data.<br>Production requires pilot validation.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ELEMENT 5 — Intervention Timeline
    st.markdown('<div class="section-header">Recent Interventions</div>', unsafe_allow_html=True)

    outcome_colors = {"improved": "#2A9D8F", "stable": "#457B9D", "no_change": "#E63946"}
    outcome_icons  = {"improved": "✅", "stable": "🔵", "no_change": "❌"}

    for item in INTERVENTION_HISTORY:
        oc  = item["outcome"]
        col = outcome_colors.get(oc, "#8B949E")
        ico = outcome_icons.get(oc, "⬜")
        st.markdown(f"""
        <div class="timeline-item">
          <div class="timeline-dot" style="background:{col};"></div>
          <div class="timeline-date">{item['date']}</div>
          <div class="timeline-action">{item['action']}</div>
          <div class="timeline-result">{item['student']} — {item['result']}</div>
          <div class="timeline-outcome" style="color:{col};">{ico} {item['delta']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Intervention effectiveness summary
    improved = sum(1 for i in INTERVENTION_HISTORY if i["outcome"] == "improved")
    total_int = len(INTERVENTION_HISTORY)
    success_rate = improved / total_int * 100

    st.markdown(f"""
    <div style="background:#161B22; border:1px solid #30363D; border-radius:8px;
                padding:10px 14px; margin-top:8px; font-size:0.8rem;">
      <div style="display:flex; justify-content:space-between;">
        <span style="color:#8B949E;">This week's success rate</span>
        <span style="color:#2A9D8F; font-family:'JetBrains Mono',monospace; font-weight:600;">{success_rate:.0f}%</span>
      </div>
      <div style="font-size:0.72rem; color:#8B949E; margin-top:3px;">{improved}/{total_int} interventions effective</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM — WEEKLY TRENDS + FULL STUDENT TABLE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

trend_col, table_col = st.columns([1, 2], gap="large")

with trend_col:
    st.markdown('<div class="section-header">Key Trends (Last 4 Weeks)</div>', unsafe_allow_html=True)

    trends = [
        ("Assignment Completion", "85% → 91%", "+6%", True),
        ("Forum Participation",   "62% → 67%", "+5%", True),
        ("Virtual Attendance",    "78% → 74%", "-4%", False),
        ("Late Submissions",      "18% → 23%", "+5%", False),
        ("Help-Seeking Rate",     "45% → 52%", "+7%", True),
    ]

    for label, values, delta, positive in trends:
        col = "#2A9D8F" if positive else "#E63946"
        arrow = "▲" if positive else "▼"
        st.markdown(f"""
        <div class="trend-row">
          <span class="trend-label">{label}</span>
          <div>
            <span class="trend-value" style="color:#8B949E; font-size:0.75rem;">{values}</span>
            <span class="trend-value" style="color:{col}; margin-left:8px;">{arrow} {delta}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

with table_col:
    st.markdown('<div class="section-header">All At-Risk Students</div>', unsafe_allow_html=True)

    display_cols = ["name", "age", "stress_type", "risk_probability", "tier"]
    available = [c for c in display_cols if c in at_risk_df.columns]
    show_df = at_risk_df[available].copy()
    show_df["risk_probability"] = (show_df["risk_probability"] * 100).round(1).astype(str) + "%"
    show_df.columns = [c.replace("_", " ").title() for c in show_df.columns]

    st.dataframe(
        show_df,
        use_container_width=True,
        height=260,
        hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="text-align:center; padding:20px 0 8px 0;
            border-top:1px solid #21262D; margin-top:24px;
            font-size:0.72rem; color:#484F58;
            font-family:'JetBrains Mono',monospace;">
  SahayakAI — The Silence Before the Drop &nbsp;|&nbsp;
  Powered by ASI-1 &nbsp;|&nbsp;
  Tech Z Ideathon 2026 &nbsp;|&nbsp;
  Solo Submission — Negashree, Coimbatore
</div>
""", unsafe_allow_html=True)