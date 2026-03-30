"""
SahayakAI — Model Training Pipeline
=====================================
XGBoost + SMOTEENN + Multi-Task Architecture
Based on ASI-1 recommendations (Day 2 session)

Run: python src/model/train_model.py
Output:
  - models/dropout_model.pkl
  - models/stress_model.pkl
  - models/plots/feature_importance.png
  - models/plots/precision_recall_curve.png
  - models/training_report.txt

Tech Z Ideathon 2026 | SahayakAI — The Silence Before the Drop
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, precision_recall_curve
)

try:
    from xgboost import XGBClassifier
    USE_XGB = True
    print("  ✅ XGBoost available")
except ImportError:
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

print("\n" + "=" * 65)
print("  SahayakAI — Model Training Pipeline")
print("  Tech Z Ideathon 2026 | The Silence Before the Drop")
print("=" * 65)


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

df_static["gender_encoded"] = (df_static["gender"] == "F").astype(int)
ALL_FEATURES = SIGNAL_FEATURES + INDIA_FEATURES + DEMO_FEATURES + ["gender_encoded"]

# Temporal lag features from time series
if df_temporal is not None:
    print("  Adding temporal lag features (weeks 8-12)...")
    late_weeks   = df_temporal[df_temporal["week"] >= 8].copy()
    temporal_agg = late_weeks.groupby("student_id")[SIGNAL_FEATURES].agg(["mean", "std"]).reset_index()
    temporal_agg.columns = (
        ["student_id"] +
        [f"{col}_{stat}" for col in SIGNAL_FEATURES for stat in ["mean_last4w", "std_last4w"]]
    )
    df_static    = df_static.merge(temporal_agg, on="student_id", how="left")
    temporal_cols = [c for c in df_static.columns if "last4w" in c]
    ALL_FEATURES  = ALL_FEATURES + temporal_cols
    print(f"  Added {len(temporal_cols)} temporal features")

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
# 4. TRAIN / TEST SPLIT  (stratified — ASI-1: time-based in production)
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
# 5. CLASS IMBALANCE  (SMOTEENN preferred, fallback to scale_pos_weight)
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
# 6. BUILD & TRAIN MODELS
# ══════════════════════════════════════════════════════════════════════════════

print("\n🤖 Training models...")

# Dropout predictor
if USE_XGB:
    dropout_model = XGBClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=6,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr", random_state=42, verbosity=0,
    )
else:
    dropout_model = GradientBoostingClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42,
    )

dropout_model.fit(X_train_res, y_dropout_train_res)
print("  ✅ Dropout predictor trained")

# Stress classifier (at-risk students only)
STRESS_MODEL_TRAINED = False
at_risk_mask = y_dropout_train == 1
if at_risk_mask.sum() >= 10:
    if USE_XGB:
        stress_model = XGBClassifier(
            n_estimators=200, learning_rate=0.05, max_depth=5,
            random_state=42, verbosity=0,
        )
    else:
        stress_model = GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42,
        )
    stress_model.fit(X_train[at_risk_mask], y_stress_train[at_risk_mask])
    STRESS_MODEL_TRAINED = True
    print("  ✅ Stress classifier trained")


# ══════════════════════════════════════════════════════════════════════════════
# 7. EVALUATE — F2-SCORE + AUC-PR  (ASI-1 primary metrics)
# ══════════════════════════════════════════════════════════════════════════════

print("\n📊 Evaluating (threshold=0.50)...")

y_proba = dropout_model.predict_proba(X_test)[:, 1]
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
  ┌────────────────────────────────────────┐
  │  Precision : {precision_val:.3f}                      │
  │  Recall    : {recall_val:.3f}                      │
  │  F1-Score  : {f1_val:.3f}                      │
  │  F2-Score  : {f2_val:.3f}  ← PRIMARY METRIC    │
  │  AUC-ROC   : {auc_roc:.3f}                      │
  │  TP={tp:3d}  FP={fp:3d}  FN={fn:3d}  TN={tn:3d}       │
  └────────────────────────────────────────┘
""")


# ══════════════════════════════════════════════════════════════════════════════
# 8. 4-TIER ADAPTIVE THRESHOLD  (ASI-1 recommended)
# ══════════════════════════════════════════════════════════════════════════════

print("🎯 4-Tier Adaptive Threshold Analysis...")

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
# 9. FEATURE IMPORTANCE PLOT
# ══════════════════════════════════════════════════════════════════════════════

print("\n📈 Generating plots...")

if hasattr(dropout_model, "feature_importances_"):
    importances = dropout_model.feature_importances_
    indices     = np.argsort(importances)[::-1][:15]
    top_names   = [ALL_FEATURES[i] for i in indices]
    top_values  = [importances[i] for i in indices]

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
# 10. SAVE MODELS & REPORT
# ══════════════════════════════════════════════════════════════════════════════

print("\n💾 Saving models...")
for obj, path in [
    (dropout_model, "models/dropout_model.pkl"),
    (le,            "models/label_encoder.pkl"),
    (ALL_FEATURES,  "models/feature_names.pkl"),
]:
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print(f"  ✅ {path}")

if STRESS_MODEL_TRAINED:
    with open("models/stress_model.pkl", "wb") as f:
        pickle.dump(stress_model, f)
    print("  ✅ models/stress_model.pkl")

# Text report
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

report_txt = f"""SahayakAI — Model Training Report
===================================
Tech Z Ideathon 2026

DATASET
  Students   : {len(df_static)}
  Features   : {len(ALL_FEATURES)}
  At-risk    : {int(y_dropout.sum())} ({y_dropout.mean()*100:.1f}%)

MODEL
  Type       : {'XGBoost' if USE_XGB else 'GradientBoosting'}
  Resampling : {'SMOTEENN' if USE_SMOTEENN else 'class_weight'}

EVALUATION (threshold=0.50)
  Precision  : {precision_val:.3f}
  Recall     : {recall_val:.3f}
  F1-Score   : {f1_val:.3f}
  F2-Score   : {f2_val:.3f}  ← PRIMARY METRIC
  AUC-ROC    : {auc_roc:.3f}
  TP={tp}  FP={fp}  FN={fn}  TN={tn}

4-TIER THRESHOLD RESULTS
{tier_report}

TOP 5 FEATURES
{top5}

Co-designed with ASI-1 (asi1.ai) | Tech Z Ideathon 2026
"""

with open("models/training_report.txt", "w", encoding="utf-8") as f:
    f.write(report_txt)
print("\n" + report_txt)

print("=" * 65)
print("  🎯 Day 3 Complete! Next: Streamlit Dashboard (Day 4)")
print("=" * 65)