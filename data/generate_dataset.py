"""
SahayakAI — Synthetic Student Dataset Generator (UPGRADED)
===========================================================
Generates realistic synthetic data for 500 students
based on the 12 behavioural micro-signals defined with ASI-1.

UPGRADES INCLUDED:
✅ Temporal Decay Simulation (12-week time series)
✅ Early Warning Labels (predict dropout before it happens)
✅ Teacher Intervention History (for dashboard demo)

Run: python generate_dataset.py
Output: 
  - data/synthetic/students.csv (static snapshot)
  - data/synthetic/students_timeseries.csv (12-week temporal data)
  - data/synthetic/students_info.txt (summary report)

Tech Z Ideathon 2026 | SahayakAI — The Silence Before the Drop
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ── Output folder ─────────────────────────────────────────────────────────────
os.makedirs("data/synthetic", exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────
N_STUDENTS      = 500
DROPOUT_RATE    = 0.30   # 30% dropout — realistic for rural India
N_DROPOUT       = int(N_STUDENTS * DROPOUT_RATE)
N_SAFE          = N_STUDENTS - N_DROPOUT
WEEKS           = 12      # 12-week observation window

print("=" * 70)
print("  SahayakAI — Synthetic Dataset Generator (UPGRADED)")
print("  Tech Z Ideathon 2026 | The Silence Before the Drop")
print("=" * 70)
print(f"\n  📊 Generating {N_STUDENTS} students...")
print(f"     At-risk (dropout=1) : {N_DROPOUT}")
print(f"     Safe    (dropout=0) : {N_SAFE}")
print(f"     Temporal window     : {WEEKS} weeks\n")

# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def clip(value, lo, hi):
    """Clip a value between lo and hi."""
    return max(lo, min(hi, value))

def noisy(base, std, lo, hi, dtype=float):
    """Add Gaussian noise to a base value, then clip."""
    val = base + np.random.normal(0, std)
    val = clip(val, lo, hi)
    return round(val, 2) if dtype == float else int(round(val))

def intervention_type():
    """Random intervention type for at-risk students."""
    return random.choice(["voice_message", "peer_buddy", "counsellor", "parent_call", "motivational_story"])

def intervention_effectiveness(intervention, week, risk_level):
    """
    Simulate intervention effectiveness.
    Earlier interventions = more effective.
    """
    if intervention == "none":
        return 0
    
    # Effectiveness decays if intervention is late
    base_effect = {
        "voice_message": 0.65,
        "peer_buddy": 0.72,
        "counsellor": 0.58,
        "parent_call": 0.45,
        "motivational_story": 0.55
    }.get(intervention, 0.50)
    
    # Late interventions (after week 8) are less effective
    if week > 8:
        base_effect *= 0.6
    elif week > 5:
        base_effect *= 0.85
    
    # Add randomness
    effectiveness = base_effect + np.random.normal(0, 0.1)
    return clip(effectiveness, 0, 1)


# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL GENERATION — AT-RISK STUDENTS (dropout = 1)
# ══════════════════════════════════════════════════════════════════════════════

def generate_at_risk(student_id_num):
    """Generate one at-risk student record."""
    
    # Randomly assign root cause — critical for Differential Diagnosis Engine
    stress_type = random.choice(["academic_struggle", "home_financial_stress"])
    
    # Intervention history (randomized for realism)
    has_intervention = random.choices([0, 1], weights=[0.4, 0.6])[0]
    intervention_week = random.randint(2, 10) if has_intervention else 0
    intervention = intervention_type() if has_intervention else "none"
    
    # ── Signal 1: Response Time Decay (hours) ───────────────────────────────
    response_time_decay = noisy(48, 12, 24, 96)
    
    # ── Signal 2: Forum Passive-Active Ratio ────────────────────────────────
    forum_passive_active_ratio = noisy(40, 10, 20, 80)
    
    # ── Signal 3: Login Pattern Fragmentation (0–1 score) ───────────────────
    login_fragmentation_score = noisy(0.75, 0.10, 0.50, 1.0)
    
    # ── Signal 4: Resource Access Depth Shift (0=deep → 1=shallow) ──────────
    resource_depth_shift = noisy(0.80, 0.10, 0.50, 1.0)
    
    # ── Signal 5: Collaborative Tool Drift (days since last group join) ──────
    collaborative_tool_drift = noisy(18, 5, 7, 30, dtype=int)
    
    # ── Signal 6: Question Quality De-escalation (Bloom level 1–6) ──────────
    question_quality_level = noisy(1.8, 0.5, 1.0, 3.0)
    
    # ── Signal 7: Peer Interaction Centrality Drop (0–1) ────────────────────
    peer_centrality_score = noisy(0.15, 0.08, 0.0, 0.40)
    
    # ── Signal 8: Optional Activity Abandonment (% attended) ────────────────
    optional_activity_rate = noisy(0.10, 0.05, 0.0, 0.25)
    
    # ── Signal 9: Submission Timing Rush Window (hours before deadline) ──────
    submission_rush_hours = noisy(1.5, 1.0, 0.0, 5.0)
    
    # ── Signal 10: Silence Burst Episodes (count in past 30 days) ───────────
    silence_burst_count = noisy(3.5, 1.0, 2, 7, dtype=int)
    
    # ── Signal 11: Help-Seeking Avoidance Gradient (days before asking help) ─
    help_seeking_latency = noisy(12, 4, 5, 21, dtype=int)
    
    # ── Signal 12: Feedback Response Dampening (0=ignores, 1=responds) ──────
    feedback_response_rate = noisy(0.15, 0.08, 0.0, 0.35)
    
    # ── Stress type modifiers ─────────────────────────────────────────────────
    if stress_type == "academic_struggle":
        login_fragmentation_score = clip(login_fragmentation_score - 0.15, 0.30, 0.80)
        question_quality_level    = clip(question_quality_level - 0.3, 1.0, 2.5)
        peer_centrality_score     = clip(peer_centrality_score - 0.05, 0.0, 0.30)
    else:
        login_fragmentation_score = clip(login_fragmentation_score + 0.10, 0.60, 1.0)
        question_quality_level    = clip(question_quality_level + 0.4, 1.5, 4.0)
        peer_centrality_score     = clip(peer_centrality_score + 0.10, 0.05, 0.50)
    
    # ── India-specific contextual features ────────────────────────────────────
    device_count           = random.choices([1, 2], weights=[0.7, 0.3])[0]
    monday_absence_cluster = random.choices([0, 1], weights=[0.3, 0.7])[0]
    tired_keyword_freq     = noisy(4.2, 1.5, 1, 10, dtype=int)
    whatsapp_study_silence = random.choices([0, 1], weights=[0.2, 0.8])[0]
    
    return {
        # Identity
        "student_id"                   : None,
        "age"                          : random.randint(12, 18),
        "gender"                       : random.choice(["F", "M"]),
        "is_first_gen_learner"         : random.choices([0, 1], weights=[0.4, 0.6])[0],
        
        # 12 Micro-Signals
        "response_time_decay_hrs"      : response_time_decay,
        "forum_passive_active_ratio"   : forum_passive_active_ratio,
        "login_fragmentation_score"    : login_fragmentation_score,
        "resource_depth_shift"         : resource_depth_shift,
        "collaborative_tool_drift_days": collaborative_tool_drift,
        "question_quality_level"       : question_quality_level,
        "peer_centrality_score"        : peer_centrality_score,
        "optional_activity_rate"       : optional_activity_rate,
        "submission_rush_hrs"          : submission_rush_hours,
        "silence_burst_count"          : silence_burst_count,
        "help_seeking_latency_days"    : help_seeking_latency,
        "feedback_response_rate"       : feedback_response_rate,
        
        # India-specific contextual signals
        "device_count"                 : device_count,
        "monday_absence_cluster"       : monday_absence_cluster,
        "tired_keyword_freq"           : tired_keyword_freq,
        "whatsapp_study_silence"       : whatsapp_study_silence,
        
        # Intervention History
        "intervention_received"        : 1 if has_intervention else 0,
        "intervention_week"            : intervention_week,
        "intervention_type"            : intervention,
        "intervention_effectiveness"   : intervention_effectiveness(intervention, intervention_week, 1),
        
        # Labels
        "stress_type"                  : stress_type,
        "dropout_risk"                 : 1,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SIGNAL GENERATION — SAFE STUDENTS (dropout = 0)
# ══════════════════════════════════════════════════════════════════════════════

def generate_safe(student_id_num):
    """Generate one safe (not at-risk) student record."""
    
    return {
        # Identity
        "student_id"                   : None,
        "age"                          : random.randint(12, 18),
        "gender"                       : random.choice(["F", "M"]),
        "is_first_gen_learner"         : random.choices([0, 1], weights=[0.6, 0.4])[0],
        
        # 12 Micro-Signals (healthy ranges)
        "response_time_decay_hrs"      : noisy(6, 3, 0.5, 18),
        "forum_passive_active_ratio"   : noisy(6, 2, 2.0, 15),
        "login_fragmentation_score"    : noisy(0.20, 0.08, 0.0, 0.45),
        "resource_depth_shift"         : noisy(0.20, 0.08, 0.0, 0.45),
        "collaborative_tool_drift_days": noisy(3, 1.5, 0, 7, dtype=int),
        "question_quality_level"       : noisy(4.0, 0.8, 2.5, 6.0),
        "peer_centrality_score"        : noisy(0.65, 0.12, 0.35, 1.0),
        "optional_activity_rate"       : noisy(0.72, 0.12, 0.40, 1.0),
        "submission_rush_hrs"          : noisy(22, 8, 6, 48),
        "silence_burst_count"          : noisy(0.5, 0.5, 0, 2, dtype=int),
        "help_seeking_latency_days"    : noisy(1.5, 0.8, 0, 4, dtype=int),
        "feedback_response_rate"       : noisy(0.85, 0.08, 0.60, 1.0),
        
        # India-specific contextual signals
        "device_count"                 : random.choices([1, 2], weights=[0.4, 0.6])[0],
        "monday_absence_cluster"       : random.choices([0, 1], weights=[0.85, 0.15])[0],
        "tired_keyword_freq"           : noisy(0.8, 0.5, 0, 3, dtype=int),
        "whatsapp_study_silence"       : random.choices([0, 1], weights=[0.85, 0.15])[0],
        
        # Intervention History (minimal for safe students)
        "intervention_received"        : 0,
        "intervention_week"            : 0,
        "intervention_type"            : "none",
        "intervention_effectiveness"   : 0,
        
        # Labels
        "stress_type"                  : "none",
        "dropout_risk"                 : 0,
    }


# ══════════════════════════════════════════════════════════════════════════════
# UPGRADE 1: TEMPORAL DECAY SIMULATION
# Shows how signals worsen over 12 weeks before dropout
# ══════════════════════════════════════════════════════════════════════════════

def add_temporal_decay(df, weeks=12):
    """
    Convert static signals into weekly time series.
    At-risk students show signal decay over time.
    Safe students remain stable or slightly improve.
    """
    print("  📈 Adding temporal decay simulation...")
    records = []
    
    for _, student in df.iterrows():
        risk = student['dropout_risk']
        
        for week in range(1, weeks + 1):
            row = student.to_dict()
            row['week'] = week
            
            if risk == 1:
                # At-risk: signals worsen exponentially
                decay_factor = (week / weeks) ** 1.5
                
                # Worsening signals
                row['response_time_decay_hrs'] = min(
                    student['response_time_decay_hrs'] * (1 + decay_factor * 0.8), 
                    96
                )
                row['silence_burst_count'] = min(
                    student['silence_burst_count'] + (week * 0.3), 
                    10
                )
                row['help_seeking_latency_days'] = min(
                    student['help_seeking_latency_days'] + (week * 0.5), 
                    30
                )
                row['peer_centrality_score'] = max(
                    student['peer_centrality_score'] * (1 - decay_factor * 0.6), 
                    0
                )
                row['question_quality_level'] = max(
                    student['question_quality_level'] * (1 - decay_factor * 0.4), 
                    1
                )
                row['login_fragmentation_score'] = min(
                    student['login_fragmentation_score'] + (decay_factor * 0.2), 
                    1
                )
                row['optional_activity_rate'] = max(
                    student['optional_activity_rate'] * (1 - decay_factor * 0.7), 
                    0
                )
                
                # Intervention effect (if intervention was received before this week)
                if student['intervention_received'] == 1 and week >= student['intervention_week']:
                    effectiveness = student['intervention_effectiveness']
                    # Apply intervention effect: reduces signal severity
                    row['response_time_decay_hrs'] = max(
                        row['response_time_decay_hrs'] * (1 - effectiveness * 0.5),
                        student['response_time_decay_hrs'] * 0.7
                    )
                    row['silence_burst_count'] = max(
                        row['silence_burst_count'] * (1 - effectiveness * 0.6),
                        1
                    )
                    row['peer_centrality_score'] = min(
                        row['peer_centrality_score'] + (effectiveness * 0.3),
                        0.5
                    )
            else:
                # Safe: stable or slight improvement
                improvement = 1 + (week / weeks) * 0.1
                row['response_time_decay_hrs'] = max(
                    student['response_time_decay_hrs'] * (1 - week * 0.02), 
                    1
                )
                row['question_quality_level'] = min(
                    student['question_quality_level'] * improvement, 
                    6
                )
                row['peer_centrality_score'] = min(
                    student['peer_centrality_score'] * improvement,
                    1
                )
            
            records.append(row)
    
    df_temporal = pd.DataFrame(records)
    print(f"  ✅ Time series created: {df_temporal.shape[0]} rows × {df_temporal.shape[1]} columns")
    return df_temporal


# ══════════════════════════════════════════════════════════════════════════════
# UPGRADE 2: EARLY WARNING LABELS (FIXED)
# ══════════════════════════════════════════════════════════════════════════════

def add_early_warning_labels(df_temporal):
    """
    Create training labels: At week X, does student drop out by week 12?
    """
    print("  🏷️ Adding early warning labels...")
    
    df_temporal['dropout_by_week12'] = df_temporal['dropout_risk']
    df_temporal['weeks_until_dropout'] = None
    df_temporal['will_dropout_soon'] = 0  # Will drop out in next 4 weeks?
    
    for student_id in df_temporal['student_id'].unique():
        student_data = df_temporal[df_temporal['student_id'] == student_id]
        
        if student_data['dropout_risk'].iloc[0] == 1:
            # At-risk student: dropout happens at week 12
            dropout_week = 12
            for _, row in student_data.iterrows():
                current_week = row['week']  # ← FIXED: moved inside loop
                weeks_left = max(0, dropout_week - current_week)
                mask = (df_temporal['student_id'] == student_id) & (df_temporal['week'] == current_week)
                df_temporal.loc[mask, 'weeks_until_dropout'] = weeks_left
                df_temporal.loc[mask, 'will_dropout_soon'] = 1 if weeks_left <= 4 else 0
        else:
            # Safe student: never drops out
            for _, row in student_data.iterrows():
                current_week = row['week']  # ← FIXED: added this line
                mask = (df_temporal['student_id'] == student_id) & (df_temporal['week'] == current_week)
                df_temporal.loc[mask, 'weeks_until_dropout'] = 99
                df_temporal.loc[mask, 'will_dropout_soon'] = 0
    
    print("  ✅ Early warning labels added")
    return df_temporal


# ══════════════════════════════════════════════════════════════════════════════
# BUILD STATIC DATASET
# ══════════════════════════════════════════════════════════════════════════════

records = []

for i in range(N_DROPOUT):
    records.append(generate_at_risk(i))

for i in range(N_SAFE):
    records.append(generate_safe(i + N_DROPOUT))

# Shuffle
random.shuffle(records)

df = pd.DataFrame(records)

# Assign student IDs
df["student_id"] = [f"STU{str(i+1).zfill(4)}" for i in range(N_STUDENTS)]

# Reorder columns — student_id first
cols = ["student_id"] + [c for c in df.columns if c != "student_id"]
df = df[cols]

# Save static dataset
static_path = "data/synthetic/students.csv"
df.to_csv(static_path, index=False)
print(f"\n  ✅ Static dataset saved → {static_path}")
print(f"     Shape: {df.shape[0]} rows × {df.shape[1]} columns")

# ══════════════════════════════════════════════════════════════════════════════
# BUILD TEMPORAL DATASET (UPGRADE 1 + 2)
# ══════════════════════════════════════════════════════════════════════════════

df_temporal = add_temporal_decay(df, WEEKS)
df_temporal = add_early_warning_labels(df_temporal)

# Reorder columns for readability
temporal_cols = ["student_id", "week"] + [c for c in df_temporal.columns if c not in ["student_id", "week"]]
df_temporal = df_temporal[temporal_cols]

temporal_path = "data/synthetic/students_timeseries.csv"
df_temporal.to_csv(temporal_path, index=False)
print(f"  ✅ Time series dataset saved → {temporal_path}")
print(f"     Shape: {df_temporal.shape[0]} rows × {df_temporal.shape[1]} columns")


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY REPORT
# ══════════════════════════════════════════════════════════════════════════════

report_lines = []
report_lines.append("=" * 70)
report_lines.append("SahayakAI — Synthetic Dataset Summary (UPGRADED)")
report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append("=" * 70)
report_lines.append(f"Total students           : {len(df)}")
report_lines.append(f"At-risk (1)              : {df['dropout_risk'].sum()}")
report_lines.append(f"Safe (0)                 : {(df['dropout_risk'] == 0).sum()}")
report_lines.append(f"Dropout rate             : {df['dropout_risk'].mean()*100:.1f}%")
report_lines.append(f"Temporal window          : {WEEKS} weeks")
report_lines.append(f"Time series rows         : {len(df_temporal)}")
report_lines.append("")
report_lines.append("Stress Type Breakdown (at-risk students):")
at_risk = df[df["dropout_risk"] == 1]
for stype, cnt in at_risk["stress_type"].value_counts().items():
    report_lines.append(f"  {stype:<30}: {cnt}")
report_lines.append("")
report_lines.append("Intervention Coverage (at-risk students):")
intervention_received = at_risk["intervention_received"].sum()
report_lines.append(f"  Received intervention   : {intervention_received} ({intervention_received/len(at_risk)*100:.1f}%)")
report_lines.append(f"  Avg effectiveness      : {at_risk['intervention_effectiveness'].mean():.2f}")
report_lines.append("")
report_lines.append("Signal Means — At-Risk vs Safe:")
report_lines.append(f"  {'Signal':<40} {'At-Risk':>10} {'Safe':>10}")
report_lines.append("  " + "-" * 62)

signals = [
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

safe_df = df[df["dropout_risk"] == 0]
for sig in signals:
    at_mean   = at_risk[sig].mean()
    safe_mean = safe_df[sig].mean()
    report_lines.append(f"  {sig:<40} {at_mean:>10.2f} {safe_mean:>10.2f}")

report_lines.append("")
report_lines.append("India-Specific Signal Rates (at-risk vs safe):")
india_signals = ["device_count", "monday_absence_cluster",
                 "tired_keyword_freq", "whatsapp_study_silence"]
for sig in india_signals:
    at_val = at_risk[sig].mean()
    safe_val = safe_df[sig].mean()
    report_lines.append(f"  {sig:<40}: {at_val:.2f} (at-risk) | {safe_val:.2f} (safe)")

report_lines.append("")
report_lines.append("Early Warning Labels (Week 4 Snapshot):")
week4 = df_temporal[df_temporal["week"] == 4]
early_warning_count = week4[week4["will_dropout_soon"] == 1].shape[0]
report_lines.append(f"  Students predicted to drop out soon at week 4: {early_warning_count}")
report_lines.append(f"  (These are the students teachers should prioritize)")

report_path = "data/synthetic/students_info.txt"
with open(report_path, "w") as f:
    f.write("\n".join(report_lines))

for line in report_lines:
    print(line)

print(f"\n  ✅ Report saved → {report_path}")
print("\n" + "=" * 70)
print("  🎯 Day 2 Complete! Dataset ready for sklearn model (Day 3)")
print("")
print("  📁 Files created:")
print(f"     • {static_path}")
print(f"     • {temporal_path}")
print(f"     • {report_path}")
print("")
print("  🚀 Next: Train sklearn classifier on time series data")
print("=" * 70)