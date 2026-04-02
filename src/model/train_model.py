"""
SahayakAI — Model Training Pipeline (FINAL WITH CALIBRATION)
==============================================================
XGBoost + SMOTEENN + Multi-Task Architecture
Based on ASI-1 recommendations (Day 2-3 sessions)

UPGRADES INCLUDED:
✅ XGBoost with SMOTEENN
✅ Model Calibration (Isotonic Regression)
✅ Cross-Validation Stability Check
✅ 4-tier adaptive threshold system
✅ Feature importance visualization
✅ Precision-Recall curve
✅ Tier 2 WhatsApp message templates
✅ Inference helper for Streamlit dashboard

Run: python src/model/train_model.py
Output:
  - models/dropout_model.pkl (uncalibrated)
  - models/dropout_model_calibrated.pkl (RECOMMENDED)
  - models/stress_model.pkl
  - models/label_encoder.pkl
  - models/feature_names.pkl
  - models/inference_helper.py
  - models/cv_results.json
  - models/training_report.txt
  - models/plots/feature_importance.png
  - models/plots/precision_recall_curve.png
  - models/plots/calibration_curve.png
  - data/templates/tier2_messages.json

Tech Z Ideathon 2026 | SahayakAI — The Silence Before the Drop
"""

import pandas as pd
import numpy as np
import os
import pickle
import json
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, precision_recall_curve,
    brier_score_loss, make_scorer
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

try:
    from xgboost import XGBClassifier
    USE_XGB = True
    print("  ✅ XGBoost available")
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    USE_XGB = False
    print("  ⚠️  XGBoost not found — using GradientBoosting")
    print("      Install: pip install xgboost")

try:
    from imblearn.combine import SMOTEENN
    USE_SMOTEENN = True
    print("  ✅ imbalanced-learn available")
except ImportError:
    USE_SMOTEENN = False
    print("  ⚠️  imbalanced-learn not found — using class_weight")
    print("      Install: pip install imbalanced-learn")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Output folders ──────────────────────────────────────────────────────────
os.makedirs("models/plots", exist_ok=True)
os.makedirs("data/templates", exist_ok=True)

print("\n" + "=" * 70)
print("  SahayakAI — Model Training Pipeline (FINAL WITH CALIBRATION)")
print("  Tech Z Ideathon 2026 | The Silence Before the Drop")
print("=" * 70)


# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

print("\n📂 Loading dataset...")

static_path   = "data/synthetic/students.csv"
temporal_path = "data/synthetic/students_timeseries.csv"

if not os.path.exists(static_path):
    raise FileNotFoundError(
        f"Dataset not found at {static_path}\n"
        "Run data/generate_dataset.py first!"
    )

df_static   = pd.read_csv(static_path)
df_temporal = pd.read_csv(temporal_path) if os.path.exists(temporal_path) else None

print(f"  Static  : {df_static.shape[0]} students × {df_static.shape[1]} columns")
if df_temporal is not None:
    print(f"  Temporal: {df_temporal.shape[0]} rows × {df_temporal.shape[1]} columns")
print(f"  At-risk : {df_static['dropout_risk'].sum()} ({df_static['dropout_risk'].mean()*100:.1f}%)")
print(f"  Safe    : {(df_static['dropout_risk']==0).sum()} ({(1-df_static['dropout_risk'].mean())*100:.1f}%)")


# ══════════════════════════════════════════════════════════════════════════════
# 2. FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════

print("\n🔧 Engineering features...")

# ── Drop leaking columns (prevent data leakage) ──────────────────────────────
LEAKING_COLS = ["dropout_probability", "intervention_effectiveness",
                "intervention_type", "intervention_week"]
for col in LEAKING_COLS:
    if col in df_static.columns:
        df_static = df_static.drop(columns=[col])
        print(f"  ℹ️  Dropped leaking column: {col}")

SIGNAL_FEATURES = [
    "response_time_decay_hrs",
    "forum_passive_active_ratio",
    "login_fragmentation_score",
    "resource_depth_shift",
    "collaborative_tool_drift_days",
    "question_quality_level",
    "peer_centrality_score",
    "optional_activity_rate",
    "submission_rush_hrs",
    "silence_burst_count",
    "help_seeking_latency_days",
    "feedback_response_rate",
]

INDIA_FEATURES = [
    "device_count",
    "monday_absence_cluster",
    "tired_keyword_freq",
    "whatsapp_study_silence",
]

DEMO_FEATURES = ["age", "is_first_gen_learner"]

# Encode gender
df_static["gender_encoded"] = (df_static["gender"] == "F").astype(int)
ALL_FEATURES = SIGNAL_FEATURES + INDIA_FEATURES + DEMO_FEATURES + ["gender_encoded"]

# Temporal lag features from time series
if df_temporal is not None:
    print("  Adding temporal lag features (weeks 8-12)...")
    late_weeks   = df_temporal[df_temporal["week"] >= 8].copy()
    temporal_agg = late_weeks.groupby("student_id")[SIGNAL_FEATURES].agg(["mean"]).reset_index()
    temporal_agg.columns = (
        ["student_id"] +
        [f"{col}_mean_last4w" for col in SIGNAL_FEATURES]
    )
    df_static    = df_static.merge(temporal_agg, on="student_id", how="left")
    temporal_cols = [c for c in df_static.columns if "last4w" in c]
    ALL_FEATURES  = ALL_FEATURES + temporal_cols
    print(f"  Added {len(temporal_cols)} temporal features")

# Fill missing values
df_static[ALL_FEATURES] = df_static[ALL_FEATURES].fillna(df_static[ALL_FEATURES].median())
print(f"  Total features: {len(ALL_FEATURES)}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. ENCODE TARGETS
# ══════════════════════════════════════════════════════════════════════════════

print("\n🏷️  Encoding targets...")

y_dropout = df_static["dropout_risk"].values
le        = LabelEncoder()
df_static["stress_encoded"] = le.fit_transform(df_static["stress_type"])
y_stress  = df_static["stress_encoded"].values
print(f"  Stress classes : {list(le.classes_)}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. TRAIN / TEST SPLIT (stratified)
# ══════════════════════════════════════════════════════════════════════════════

print("\n✂️  Splitting data (80/20 stratified)...")

X = df_static[ALL_FEATURES].values

(X_train, X_test,
 y_dropout_train, y_dropout_test,
 y_stress_train,  y_stress_test) = train_test_split(
    X, y_dropout, y_stress,
    test_size=0.20, random_state=42, stratify=y_dropout
)

print(f"  Train : {X_train.shape[0]} | Test: {X_test.shape[0]}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. CLASS IMBALANCE (SMOTEENN)
# ══════════════════════════════════════════════════════════════════════════════

print("\n⚖️  Handling class imbalance...")

pos = int(y_dropout_train.sum())
neg = int(len(y_dropout_train) - pos)
scale_pos_weight = neg / pos
print(f"  Positive={pos}  Negative={neg}  scale_pos_weight={scale_pos_weight:.2f}")

if USE_SMOTEENN:
    print("  Applying SMOTEENN...")
    smoteenn = SMOTEENN(random_state=42)
    X_train_res, y_dropout_train_res = smoteenn.fit_resample(X_train, y_dropout_train)
    print(f"  After SMOTEENN : {X_train_res.shape[0]} samples  "
          f"({y_dropout_train_res.mean()*100:.1f}% at-risk)")
else:
    X_train_res       = X_train
    y_dropout_train_res = y_dropout_train


# ══════════════════════════════════════════════════════════════════════════════
# 6. TRAIN DROPOUT MODEL (XGBoost)
# ══════════════════════════════════════════════════════════════════════════════

print("\n🤖 Training dropout predictor...")

if USE_XGB:
    dropout_model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        random_state=42,
        verbosity=0,
    )
    
    dropout_model.fit(X_train_res, y_dropout_train_res)
    print("  ✅ Dropout predictor trained (XGBoost)")
else:
    dropout_model = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
    )
    dropout_model.fit(X_train_res, y_dropout_train_res)
    print("  ✅ Dropout predictor trained (GradientBoosting)")


# ══════════════════════════════════════════════════════════════════════════════
# 6.5. CALIBRATE MODEL PROBABILITIES
# ══════════════════════════════════════════════════════════════════════════════

print("\n🎚️  Calibrating model probabilities...")

# Create calibration set (20% of resampled training)
X_cal, X_remaining, y_cal, y_remaining = train_test_split(
    X_train_res, y_dropout_train_res,
    test_size=0.2, random_state=42, stratify=y_dropout_train_res
)

# Fit calibration
calibrated_model = CalibratedClassifierCV(
    dropout_model, 
    method='isotonic',
    cv='prefit'
)

calibrated_model.fit(X_cal, y_cal)

# Compare reliability
y_proba_uncal = dropout_model.predict_proba(X_test)[:, 1]
y_proba_cal = calibrated_model.predict_proba(X_test)[:, 1]

brier_uncal = brier_score_loss(y_dropout_test, y_proba_uncal)
brier_cal = brier_score_loss(y_dropout_test, y_proba_cal)

print(f"  Uncalibrated Brier Score: {brier_uncal:.4f}")
print(f"  Calibrated Brier Score:   {brier_cal:.4f}")

if brier_cal < brier_uncal:
    improvement = ((brier_uncal - brier_cal) / brier_uncal * 100)
    print(f"  ✅ Calibration improved Brier Score by {improvement:.1f}%")

# Save calibrated model
with open("models/dropout_model_calibrated.pkl", "wb") as f:
    pickle.dump(calibrated_model, f)
print("  ✅ Calibrated model saved to models/dropout_model_calibrated.pkl")

# Calibration curve plot
prob_true, prob_pred = calibration_curve(y_dropout_test, y_proba_cal, n_bins=10)

fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor("#0D1117")
ax.set_facecolor("#161B22")
ax.plot([0, 1], [0, 1], linestyle='--', color='white', alpha=0.5, label='Perfect Calibration')
ax.plot(prob_pred, prob_true, marker='o', color='#E63946', linewidth=2, label='Calibrated Model')
ax.set_xlabel('Mean Predicted Probability', color='white', fontsize=11)
ax.set_ylabel('Fraction of Positives', color='white', fontsize=11)
ax.set_title('SahayakAI — Model Calibration Curve', color='white', fontsize=13, fontweight='bold')
ax.tick_params(colors='white')
ax.legend(facecolor='#161B22', labelcolor='white', fontsize=9)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color("#30363D")
ax.grid(color='#30363D', alpha=0.3)
plt.tight_layout()
cal_path = "models/plots/calibration_curve.png"
plt.savefig(cal_path, dpi=150, bbox_inches='tight', facecolor="#0D1117")
plt.close()
print(f"  ✅ Calibration curve saved to {cal_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 6.6. CROSS-VALIDATION STABILITY CHECK
# ══════════════════════════════════════════════════════════════════════════════

print("\n🔁 Cross-validation stability check (5-fold)...")

def f2_scorer(y_true, y_pred):
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    return (5 * p * r) / (4 * p + r + 1e-9)

f2_custom = make_scorer(f2_scorer)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_scores = cross_val_score(
    dropout_model,
    X_train_res,
    y_dropout_train_res,
    cv=skf,
    scoring=f2_custom,
    n_jobs=1
)

print(f"  F2-Score: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
print(f"  Individual folds: {[f'{s:.3f}' for s in cv_scores]}")

cv_results = {
    'mean_f2': float(cv_scores.mean()),
    'std_f2': float(cv_scores.std()),
    'individual_scores': cv_scores.tolist(),
    'stability': 'STABLE' if cv_scores.std() < 0.03 else 'UNSTABLE'
}

with open("models/cv_results.json", "w", encoding="utf-8") as f:
    json.dump(cv_results, f, indent=2)
print(f"  ✅ CV results saved to models/cv_results.json")
print(f"  Model stability: {cv_results['stability']}")


# ══════════════════════════════════════════════════════════════════════════════
# 7. TRAIN STRESS CLASSIFIER (at-risk students only)
# ══════════════════════════════════════════════════════════════════════════════

print("\n🤖 Training stress classifier...")

STRESS_MODEL_TRAINED = False
stress_model = None

at_risk_mask = y_dropout_train == 1
if at_risk_mask.sum() >= 10:
    X_stress_train = X_train[at_risk_mask]
    y_stress_train_filtered = y_stress_train[at_risk_mask]
    
    if USE_XGB:
        stress_model = XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            random_state=42,
            verbosity=0,
        )
    else:
        stress_model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=5,
            random_state=42,
        )
    
    stress_model.fit(X_stress_train, y_stress_train_filtered)
    STRESS_MODEL_TRAINED = True
    print(f"  ✅ Stress classifier trained on {X_stress_train.shape[0]} at-risk students")
else:
    print(f"  ⚠️  Not enough at-risk students ({at_risk_mask.sum()}) — skipping stress model")


# ══════════════════════════════════════════════════════════════════════════════
# 8. EVALUATE MODEL (Using calibrated model for final evaluation)
# ══════════════════════════════════════════════════════════════════════════════

print("\n📊 Evaluating model (using calibrated model)...")

y_proba = calibrated_model.predict_proba(X_test)[:, 1]
y_pred  = (y_proba >= 0.50).astype(int)

precision_val = precision_score(y_dropout_test, y_pred, zero_division=0)
recall_val    = recall_score(y_dropout_test, y_pred, zero_division=0)
f1_val        = f1_score(y_dropout_test, y_pred, zero_division=0)
f2_val        = (5 * precision_val * recall_val) / (4 * precision_val + recall_val + 1e-9)

try:
    auc_roc = roc_auc_score(y_dropout_test, y_proba)
except Exception:
    auc_roc = 0.0

cm = confusion_matrix(y_dropout_test, y_pred)
tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

print(f"""
  ┌────────────────────────────────────────────────────┐
  │  SahayakAI — Test Set Performance (Calibrated)     │
  ├────────────────────────────────────────────────────┤
  │  Precision : {precision_val:.3f}                               │
  │  Recall    : {recall_val:.3f}                               │
  │  F1-Score  : {f1_val:.3f}                               │
  │  F2-Score  : {f2_val:.3f}  ← PRIMARY METRIC        │
  │  AUC-ROC   : {auc_roc:.3f}                               │
  │                                                      │
  │  TP={tp:3d}  FP={fp:3d}  FN={fn:3d}  TN={tn:3d}              │
  └────────────────────────────────────────────────────┘
""")


# ══════════════════════════════════════════════════════════════════════════════
# 9. 4-TIER ADAPTIVE THRESHOLD
# ══════════════════════════════════════════════════════════════════════════════

print("\n🎯 4-Tier Adaptive Threshold Analysis...")

TIERS = [
    {"name": "Tier 1 — Immediate Visit",  "threshold": 0.75,
     "action": "In-person teacher visit + counsellor"},
    {"name": "Tier 2 — Digital Check-In", "threshold": 0.50,
     "action": "WhatsApp message + peer mentor"},
    {"name": "Tier 3 — Watch List",       "threshold": 0.30,
     "action": "Passive monitoring, weekly review"},
    {"name": "Tier 4 — Baseline Monitor", "threshold": 0.20,
     "action": "Data logging only"},
]

tier_results = []
print(f"\n  {'Tier':<32} {'Thresh':>6} {'Prec':>6} {'Recall':>7} {'F2':>6} {'Flagged':>8}")
print("  " + "-" * 70)

for tier in TIERS:
    t   = tier["threshold"]
    yp  = (y_proba >= t).astype(int)
    p   = precision_score(y_dropout_test, yp, zero_division=0)
    r   = recall_score(y_dropout_test, yp, zero_division=0)
    f2t = (5 * p * r) / (4 * p + r + 1e-9)
    flagged = int(yp.sum())
    tier_results.append({**tier, "precision": p, "recall": r, "f2": f2t, "flagged": flagged})
    print(f"  {tier['name']:<32} {t:>6.2f} {p:>6.3f} {r:>7.3f} {f2t:>6.3f} {flagged:>8}")


# ══════════════════════════════════════════════════════════════════════════════
# 10. FEATURE IMPORTANCE PLOT
# ══════════════════════════════════════════════════════════════════════════════

print("\n📈 Generating feature importance plot...")

if hasattr(dropout_model, "feature_importances_"):
    importances = dropout_model.feature_importances_
    indices     = np.argsort(importances)[::-1][:15]
    top_names   = [ALL_FEATURES[i] for i in indices if i < len(ALL_FEATURES)]
    top_values  = [importances[i] for i in indices if i < len(ALL_FEATURES)]

    colors = []
    for n in top_names:
        if n in SIGNAL_FEATURES:   colors.append("#E63946")
        elif n in INDIA_FEATURES:  colors.append("#F4A261")
        elif "last4w" in n:        colors.append("#457B9D")
        else:                      colors.append("#2A9D8F")

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#0D1117")
    ax.set_facecolor("#161B22")
    bars = ax.barh(range(len(top_names)), top_values, color=colors, height=0.7)
    ax.set_yticks(range(len(top_names)))
    ax.set_yticklabels(top_names, fontsize=10, color="white")
    ax.invert_yaxis()
    ax.set_xlabel("Feature Importance Score", color="white", fontsize=11)
    ax.set_title(
        "SahayakAI — Top 15 Dropout Prediction Features\n"
        "(ASI-1 Co-Designed Signal Architecture)",
        color="white", fontsize=13, fontweight="bold", pad=15
    )
    ax.tick_params(colors="white")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#30363D")

    legend_patches = [
        mpatches.Patch(color="#E63946", label="Core Micro-Signal (ASI-1)"),
        mpatches.Patch(color="#F4A261", label="India-Specific Signal"),
        mpatches.Patch(color="#457B9D", label="Temporal (Last 4 Weeks)"),
        mpatches.Patch(color="#2A9D8F", label="Demographic"),
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              facecolor="#161B22", labelcolor="white", fontsize=9)
    for bar, val in zip(bars, top_values):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", color="white", fontsize=8)

    plt.tight_layout()
    fi_path = "models/plots/feature_importance.png"
    plt.savefig(fi_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
    plt.close()
    print(f"  ✅ {fi_path}")

# Precision-Recall curve
prec_c, rec_c, thresh_c = precision_recall_curve(y_dropout_test, y_proba)
fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor("#0D1117")
ax.set_facecolor("#161B22")
ax.plot(rec_c, prec_c, color="#E63946", linewidth=2.5, label="SahayakAI")
ax.fill_between(rec_c, prec_c, alpha=0.15, color="#E63946")

tier_colors_pr = ["#F4A261", "#2A9D8F", "#457B9D", "#9B89AC"]
for tier, col in zip(TIERS, tier_colors_pr):
    t  = tier["threshold"]
    yp = (y_proba >= t).astype(int)
    p  = precision_score(y_dropout_test, yp, zero_division=0)
    r  = recall_score(y_dropout_test, yp, zero_division=0)
    ax.scatter(r, p, s=120, color=col, zorder=5,
               label=f"{tier['name'][:6]} ({t})")
    ax.annotate(f"T{TIERS.index(tier)+1}", (r, p),
                textcoords="offset points", xytext=(6, 4),
                color=col, fontsize=9, fontweight="bold")

ax.set_xlabel("Recall", color="white", fontsize=11)
ax.set_ylabel("Precision", color="white", fontsize=11)
ax.set_title(
    "SahayakAI — Precision-Recall Curve\n4-Tier Adaptive Threshold System",
    color="white", fontsize=13, fontweight="bold"
)
ax.tick_params(colors="white")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color("#30363D")
ax.legend(facecolor="#161B22", labelcolor="white", fontsize=8)
ax.set_xlim([0, 1.05]); ax.set_ylim([0, 1.05])
plt.tight_layout()
pr_path = "models/plots/precision_recall_curve.png"
plt.savefig(pr_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
plt.close()
print(f"  ✅ {pr_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 11. GENERATE TIER 2 WHATSAPP TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

print("\n💬 Generating Tier 2 intervention templates...")

def generate_tier2_message(
    student_name="[Student]",
    teacher_name="[Teacher]",
    school_name="[School]",
    pattern="academic_struggle",
    signal="forum_passive_active_ratio"
):
    """Generate Tier 2 WhatsApp check-in message based on detected pattern."""
    
    if pattern == "academic_struggle":
        if signal == "forum_passive_active_ratio":
            msg = f"""📚 Hello {student_name}! 👋

This is {teacher_name} from {school_name}.

Just wanted to check in — how are classes going this week?

I noticed you haven't posted any forum questions in the last 2 weeks. That's okay! 😊 But I remember you used to be very active and ask good doubts. I miss seeing your questions in the class chat!

Is there any topic you're finding difficult? Or maybe having a hard time with understanding something?

If you need any extra help — explain again, give more examples, or practice problems — just reply here.

I can also connect you with a peer mentor who is very good at this subject. They can help explain in easier ways. No problem at all! 👍

Remember: asking for help is not weakness. You are doing great, and we are here to support you. 💪

Do you want me to arrange a quick 10 minute explanation call this week? Just reply YES and I will arrange.

Or if everything is okay and you just needed a study break, that is also fine! 😊

Take care, and keep going!

💬 {teacher_name}
{school_name}"""
        
        elif signal == "submission_rush_hrs":
            msg = f"""📚 Hello {student_name}! 👋

This is {teacher_name} from {school_name}.

I noticed your last assignment was submitted close to the deadline.

This happens sometimes — I understand! Maybe you had a busy week, or work at home, or maybe the topic took more time to understand. All okay! 😊

Did any part of the assignment feel difficult? If you tell me which topic, I can explain in simpler ways or give practice problems. Or I can arrange a 15 minute help session this weekend.

Remember: submitting on time is important, but understanding is more important. I am here to help you understand better. 💪

Do you want extra support? Just reply YES.

💬 {teacher_name}
{school_name}"""
        
        elif signal == "response_time_decay_hrs":
            msg = f"""📚 Hello {student_name}! 👋

How are you doing this week? I hope your studies are going well.

I noticed you haven't replied to forum messages as quickly in the last few weeks. Maybe you are very busy, or maybe your phone/internet connection is slow, or you are working at home. It's completely okay! 😊

But I wanted to make sure you understand the topics being discussed. If any topic is confusing, you can always ask me privately. No need to worry about what others think.

I can send you summary notes, or explain in a video call, or connect you with a peer helper.

What would help you? Just reply: NOTES, CALL, or PEER.

Take care — and remember, we are all supporting you! 💪

💬 {teacher_name}
{school_name}"""
        
        elif signal == "login_fragmentation_score":
            msg = f"""📚 Hello {student_name}! 👋

Hope you are doing well!

I noticed you have been logging in at different times and some days not at all. This is common for many students who share devices or have internet issues at home. I completely understand!

Just wanted to check — are there any problems with your phone or internet connection? Or maybe you are working at home?

If you cannot login regularly, I can send you study materials over WhatsApp so you can download when you have connection. Or I can give you printouts at school.

You can also come to school early and use the computer lab — I can arrange for you.

What would help you study better? Reply DEVICE, INTERNET, or SCHOOL.

I am here to support you! 💪

💬 {teacher_name}
{school_name}"""
        
        else:
            msg = f"""📚 Hello {student_name}! 👋

This is {teacher_name} from {school_name}.

Just wanted to check in — how are your classes going this week?

I noticed you seem to be having some trouble with your studies in the last few weeks. This happens to many students, and it's completely okay! 😊

Is there any topic you're finding difficult? Or maybe something is making it hard to focus?

Remember — you are not alone in this. I am here to help you. You can always ask questions, ask for examples, or for more explanation. There is no silly question!

If you want, I can also connect you with a peer mentor who can help explain things in simpler ways.

Would you like some extra help this week? Just reply YES, and I will arrange.

Keep going — you can do this! 💪

💬 {teacher_name}
{school_name}"""
    
    elif pattern == "home_financial_stress":
        msg = f"""📚 Hello {student_name}! 👋

This is {teacher_name} from {school_name}.

How is everything at home? I hope you and your family are okay.

I noticed you've been having some difficulty with your studies recently. Sometimes family situations or other challenges make it hard to focus on classes — I completely understand.

If there is anything I can help with — maybe flexible assignment deadlines, or accessing study materials in different ways — just let me know. We can always work something out together.

I can also connect you with our school counselor who can help if you have any concerns.

Remember: your education is important. We want to support you however we can. 💪

Just reply here anytime, or talk to me at school.

Take care!

💬 {teacher_name}
{school_name}"""
    
    return msg


# Save templates
templates = {
    "tier2_academic_forum": generate_tier2_message(signal="forum_passive_active_ratio"),
    "tier2_academic_submission": generate_tier2_message(signal="submission_rush_hrs"),
    "tier2_academic_response": generate_tier2_message(signal="response_time_decay_hrs"),
    "tier2_academic_login": generate_tier2_message(signal="login_fragmentation_score"),
    "tier2_financial_home": generate_tier2_message(pattern="home_financial_stress"),
    "tier2_generic": generate_tier2_message(pattern="academic_struggle", signal="generic"),
}

with open("data/templates/tier2_messages.json", "w", encoding="utf-8") as f:
    json.dump(templates, f, ensure_ascii=False, indent=2)

print("  ✅ Tier 2 templates saved to data/templates/tier2_messages.json")


# ══════════════════════════════════════════════════════════════════════════════
# 12. INFERENCE HELPER FOR STREAMLIT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

print("\n🔮 Creating inference helper for dashboard...")

with open("models/inference_helper.py", "w", encoding="utf-8") as f:
    f.write('''
"""
SahayakAI — Inference Helper (UPDATED WITH CALIBRATED MODEL)
==============================================================
Load trained models and predict dropout risk for Streamlit dashboard.

Usage:
    from inference_helper import predict_dropout_risk, load_model, load_feature_names
    
    # Load once at startup
    model = load_model(use_calibrated=True)  # Prefers calibrated model
    features = load_feature_names()
    
    # Predict for a student
    result = predict_dropout_risk(student_features, model, features)
    print(result["risk_probability"])
    print(result["tier"])
"""

import pickle
import numpy as np
import os

def load_model(path="models/dropout_model.pkl", use_calibrated=True):
    """Load trained model. Prefers calibrated model if available."""
    # Try calibrated first
    if use_calibrated:
        cal_path = "models/dropout_model_calibrated.pkl"
        if os.path.exists(cal_path):
            with open(cal_path, "rb") as f:
                model = pickle.load(f)
            print(f"✅ Using calibrated model: {cal_path}")
            return model
    
    # Fallback to uncalibrated
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Model not found at {path}. Run train_model.py first."
        )
    with open(path, "rb") as f:
        model = pickle.load(f)
    print(f"⚠️  Using uncalibrated model: {path}")
    return model

def load_stress_model(path="models/stress_model.pkl"):
    """Load stress classifier model."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def load_label_encoder(path="models/label_encoder.pkl"):
    """Load label encoder for stress types."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def load_feature_names(path="models/feature_names.pkl"):
    """Load feature names list."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Feature names not found at {path}. Run train_model.py first.")
    with open(path, "rb") as f:
        return pickle.load(f)

def load_tier2_templates(path="data/templates/tier2_messages.json"):
    """Load Tier 2 WhatsApp message templates."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            import json
            return json.load(f)
    return {}

def load_cv_results(path="models/cv_results.json"):
    """Load cross-validation results."""
    if os.path.exists(path):
        with open(path, "r") as f:
            import json
            return json.load(f)
    return None

def predict_dropout_risk(student_features, model=None, feature_names=None):
    """
    Predict dropout risk for a student.
    
    Args:
        student_features: Dict or array-like with feature values
        model: Pre-loaded model (optional, will load calibrated if available)
        feature_names: Pre-loaded feature names (optional, will load if None)
    
    Returns:
        Dictionary with risk_probability, tier, confidence, risk_level
    """
    if model is None:
        model = load_model(use_calibrated=True)
    if feature_names is None:
        feature_names = load_feature_names()
    
    # Convert input to array
    if isinstance(student_features, dict):
        feature_array = np.array([student_features.get(f, 0) for f in feature_names])
    else:
        feature_array = np.array(student_features).reshape(1, -1)
    
    # Predict probability
    risk_probability = model.predict_proba(feature_array)[0, 1]
    
    # Determine tier and confidence
    if risk_probability >= 0.75:
        tier = "Tier 1 — Immediate Visit"
        confidence = "High"
        risk_level = "Critical"
    elif risk_probability >= 0.50:
        tier = "Tier 2 — Digital Check-In"
        confidence = "High"
        risk_level = "Moderate"
    elif risk_probability >= 0.30:
        tier = "Tier 3 — Watch List"
        confidence = "Medium"
        risk_level = "Low"
    else:
        tier = "Tier 4 — Baseline Monitor"
        confidence = "Low"
        risk_level = "Very Low"
    
    return {
        "risk_probability": float(risk_probability),
        "tier": tier,
        "confidence": confidence,
        "risk_level": risk_level
    }

def predict_stress_type(student_features, model=None, label_encoder=None):
    """Predict stress type for at-risk students."""
    if model is None:
        model = load_stress_model()
    if model is None:
        return "Unknown"
    
    if label_encoder is None:
        label_encoder = load_label_encoder()
    
    if isinstance(student_features, dict):
        feature_names = load_feature_names()
        feature_array = np.array([student_features.get(f, 0) for f in feature_names])
    else:
        feature_array = np.array(student_features).reshape(1, -1)
    
    stress_proba = model.predict_proba(feature_array)[0]
    stress_idx = np.argmax(stress_proba)
    
    if label_encoder:
        return label_encoder.inverse_transform([stress_idx])[0]
    return f"Class_{stress_idx}"

def get_intervention_message(student_name, teacher_name, school_name, 
                              pattern="academic_struggle", signal="forum_passive_active_ratio"):
    """Get personalized Tier 2 WhatsApp message."""
    templates = load_tier2_templates()
    
    key = f"tier2_{pattern}_{signal}" if pattern == "academic_struggle" else f"tier2_{pattern}"
    
    if key in templates:
        message = templates[key]
    else:
        message = templates.get("tier2_generic", "Hello! Need any help with studies?")
    
    # Personalize
    message = message.replace("[Student]", student_name)
    message = message.replace("[Teacher]", teacher_name)
    message = message.replace("[School]", school_name)
    
    return message
''')

print("  ✅ Inference helper saved to models/inference_helper.py")


# ══════════════════════════════════════════════════════════════════════════════
# 13. SAVE MODELS
# ══════════════════════════════════════════════════════════════════════════════

print("\n💾 Saving models...")

# Save uncalibrated model (for reference)
with open("models/dropout_model.pkl", "wb") as f:
    pickle.dump(dropout_model, f)
print("  ✅ models/dropout_model.pkl")

# Calibrated model already saved in Section 6.5
if os.path.exists("models/dropout_model_calibrated.pkl"):
    print("  ✅ models/dropout_model_calibrated.pkl")

# Save label encoder and feature names
with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)
print("  ✅ models/label_encoder.pkl")

with open("models/feature_names.pkl", "wb") as f:
    pickle.dump(ALL_FEATURES, f)
print("  ✅ models/feature_names.pkl")

if STRESS_MODEL_TRAINED and stress_model is not None:
    with open("models/stress_model.pkl", "wb") as f:
        pickle.dump(stress_model, f)
    print("  ✅ models/stress_model.pkl")

# NOTE: StandardScaler removed as XGBoost is scale-invariant
print("  ℹ️  No scaler saved — XGBoost is scale-invariant")


# ══════════════════════════════════════════════════════════════════════════════
# 14. SAVE TRAINING REPORT
# ══════════════════════════════════════════════════════════════════════════════

print("\n📝 Generating training report...")

# Prepare calibration note
calibration_note = ""
if os.path.exists("models/dropout_model_calibrated.pkl"):
    improvement = ((brier_uncal - brier_cal) / brier_uncal * 100) if brier_uncal > 0 else 0
    calibration_note = f"\n  Calibration improved Brier Score by {improvement:.1f}%"

# Prepare CV note
cv_note = ""
if os.path.exists("models/cv_results.json"):
    with open("models/cv_results.json", "r") as f:
        cv_data = json.load(f)
    cv_note = f"\n  CV Stability: {cv_data['stability']}\n  CV F2-Score: {cv_data['mean_f2']:.3f} ± {cv_data['std_f2']:.3f}"

top5 = ""
if hasattr(dropout_model, "feature_importances_"):
    top5_list = sorted(
        zip(ALL_FEATURES, dropout_model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )[:5]
    top5 = "\n".join(f"  {i+1}. {n:<42}: {v:.4f}" for i, (n, v) in enumerate(top5_list))

tier_report = "\n".join(
    f"  {tr['name']:<32} thresh={tr['threshold']}  "
    f"P={tr['precision']:.2f}  R={tr['recall']:.2f}  "
    f"F2={tr['f2']:.2f}  flagged={tr['flagged']}"
    for tr in tier_results
)

report_txt = f"""SahayakAI — Model Training Report (FINAL WITH CALIBRATION)
==============================================================
Tech Z Ideathon 2026 | The Silence Before the Drop

DATASET
  Students   : {len(df_static)}
  Features   : {len(ALL_FEATURES)}
  At-risk    : {int(y_dropout.sum())} ({y_dropout.mean()*100:.1f}%)

MODEL
  Type       : {'XGBoost' if USE_XGB else 'GradientBoosting'}
  Resampling : {'SMOTEENN' if USE_SMOTEENN else 'class_weight'}{calibration_note}

MODEL STABILITY{cv_note}

EVALUATION (Calibrated Model, threshold=0.50)
  Precision  : {precision_val:.4f}
  Recall     : {recall_val:.4f}
  F1-Score   : {f1_val:.4f}
  F2-Score   : {f2_val:.4f}  ← PRIMARY METRIC
  AUC-ROC    : {auc_roc:.4f}
  TP={tp}  FP={fp}  FN={fn}  TN={tn}

4-TIER THRESHOLD RESULTS
{tier_report}

TOP 5 FEATURES
{top5}

OUTPUT FILES GENERATED
  - models/dropout_model.pkl (uncalibrated)
  - models/dropout_model_calibrated.pkl (RECOMMENDED FOR PRODUCTION)
  - models/stress_model.pkl
  - models/label_encoder.pkl
  - models/feature_names.pkl
  - models/inference_helper.py (UPDATED to use calibrated model)
  - models/cv_results.json
  - models/plots/feature_importance.png
  - models/plots/precision_recall_curve.png
  - models/plots/calibration_curve.png
  - data/templates/tier2_messages.json
  - models/training_report.txt

RECOMMENDATION: Use dropout_model_calibrated.pkl in Streamlit dashboard
for production deployment to ensure reliable probability estimates.

Co-designed with ASI-1 (asi1.ai) | Tech Z Ideathon 2026
"""

with open("models/training_report.txt", "w", encoding="utf-8") as f:
    f.write(report_txt)

print("\n" + report_txt)

print("\n" + "=" * 70)
print("  🎯 Day 3 Complete! All models, calibration, and templates ready.")
print("")
print("  📁 Files created:")
print("     • models/dropout_model.pkl (uncalibrated)")
print("     • models/dropout_model_calibrated.pkl (RECOMMENDED)")
print("     • models/stress_model.pkl")
print("     • models/label_encoder.pkl")
print("     • models/feature_names.pkl")
print("     • models/inference_helper.py")
print("     • models/cv_results.json")
print("     • models/plots/feature_importance.png")
print("     • models/plots/precision_recall_curve.png")
print("     • models/plots/calibration_curve.png")
print("     • data/templates/tier2_messages.json")
print("     • models/training_report.txt")
print("")
print("  🚀 Next: Build Streamlit Dashboard (Day 4)")
print("=" * 70)