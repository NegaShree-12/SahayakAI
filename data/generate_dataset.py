"""
SahayakAI — Synthetic Student Dataset Generator (FINAL CORRECT)
=================================================================
Generates realistic synthetic data with proper probability spread.

FIXES:
- Simplified interpretable risk calculation
- Direct per-feature risk scoring (0-1)
- Bimodal distribution (40% safe, 40% at-risk, 20% ambiguous)
- Variable overlap noise based on confusion level
- Realistic dropout rate (18-25%)

Run: python data/generate_dataset.py
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

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
N_STUDENTS = 500
WEEKS = 12
LABEL_NOISE_RATE = 0.08

print("=" * 70)
print("  SahayakAI — Synthetic Dataset Generator (FINAL CORRECT)")
print("  Tech Z Ideathon 2026 | The Silence Before the Drop")
print("=" * 70)
print(f"\n  📊 Generating {N_STUDENTS} students...")
print(f"     Label noise: {LABEL_NOISE_RATE*100:.0f}%")
print(f"     Distribution: 40% safe, 40% at-risk, 20% ambiguous")


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def clip(value, lo, hi):
    """Clip a value between lo and hi."""
    return max(lo, min(hi, value))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def intervention_type():
    return random.choice(["voice_message", "peer_buddy", "counsellor", "parent_call", "motivational_story"])

def intervention_effectiveness(intervention, week, risk_level):
    if intervention == "none":
        return 0
    base_effect = {
        "voice_message": 0.65, "peer_buddy": 0.72, "counsellor": 0.58,
        "parent_call": 0.45, "motivational_story": 0.55
    }.get(intervention, 0.50)
    if week > 8:
        base_effect *= 0.6
    elif week > 5:
        base_effect *= 0.85
    return clip(base_effect + np.random.normal(0, 0.1), 0, 1)


# ══════════════════════════════════════════════════════════════════════════════
# GENERATE STUDENT PROFILES (BIMODAL DISTRIBUTION)
# ══════════════════════════════════════════════════════════════════════════════

def generate_student_profiles(n_students):
    """
    Generate student profiles with bimodal distribution.
    40% clearly safe, 40% clearly at-risk, 20% ambiguous.
    """
    
    # Signal params with WIDE std devs
    signal_params = {
        'response_time_decay_hrs': {'at_risk': (48, 28), 'safe': (6, 24)},
        'forum_passive_active_ratio': {'at_risk': (45, 24), 'safe': (8, 16)},
        'login_fragmentation_score': {'at_risk': (0.75, 0.28), 'safe': (0.20, 0.24)},
        'resource_depth_shift': {'at_risk': (0.75, 0.28), 'safe': (0.20, 0.24)},
        'collaborative_tool_drift_days': {'at_risk': (18, 10), 'safe': (3, 7)},
        'question_quality_level': {'at_risk': (2.0, 1.5), 'safe': (4.5, 1.4)},
        'peer_centrality_score': {'at_risk': (0.20, 0.22), 'safe': (0.75, 0.22)},
        'optional_activity_rate': {'at_risk': (0.15, 0.22), 'safe': (0.75, 0.22)},
        'submission_rush_hrs': {'at_risk': (3, 12), 'safe': (24, 18)},
        'silence_burst_count': {'at_risk': (4, 3.0), 'safe': (0.5, 1.5)},
        'help_seeking_latency_days': {'at_risk': (14, 8), 'safe': (2, 5)},
        'feedback_response_rate': {'at_risk': (0.20, 0.18), 'safe': (0.85, 0.18)},
    }
    
    # Bounds for clipping
    bounds = {
        'response_time_decay_hrs': (0, 96),
        'forum_passive_active_ratio': (1, 80),
        'login_fragmentation_score': (0, 1),
        'resource_depth_shift': (0, 1),
        'collaborative_tool_drift_days': (0, 30),
        'question_quality_level': (1, 6),
        'peer_centrality_score': (0, 1),
        'optional_activity_rate': (0, 1),
        'submission_rush_hrs': (0, 48),
        'silence_burst_count': (0, 10),
        'help_seeking_latency_days': (0, 30),
        'feedback_response_rate': (0, 1),
    }
    
    all_profiles = []
    
    for i in range(n_students):
        # BIMODAL DISTRIBUTION: 40% safe, 40% at-risk, 20% ambiguous
        mode_choice = random.random()
        
        if mode_choice < 0.40:
            # 40% clearly safe (Beta with small alpha, large beta)
            true_risk_prob = np.random.beta(1.5, 6)
        elif mode_choice < 0.80:
            # 40% clearly at-risk (Beta with large alpha, small beta)
            true_risk_prob = np.random.beta(5, 1.5)
        else:
            # 20% ambiguous/uncertain (uniform in the middle)
            true_risk_prob = np.random.uniform(0.3, 0.7)
        
        true_risk = true_risk_prob > 0.5
        
        profile = {}
        
        for signal, params in signal_params.items():
            if true_risk:
                mean, std = params['at_risk']
                value = np.random.normal(mean, std)
            else:
                mean, std = params['safe']
                value = np.random.normal(mean, std)
            
            lo, hi = bounds[signal]
            profile[signal] = clip(value, lo, hi)
            
            # DIFFERENT overlap based on confusion level
            confusion = 1 - abs(true_risk_prob - 0.5) * 2  # 0 = extreme, 1 = confused
            overlap_std = (hi - lo) * 0.06 * confusion
            overlap_noise = np.random.normal(0, overlap_std)
            profile[signal] = clip(profile[signal] + overlap_noise, lo, hi)
        
        # Calculate probability using simplified method
        prob = calculate_dropout_probability(profile)
        
        all_profiles.append({
            **profile,
            '_true_risk': true_risk,
            '_true_risk_prob': true_risk_prob,
            '_raw_probability': prob,
        })
    
    return all_profiles


# ══════════════════════════════════════════════════════════════════════════════
# PROBABILITY CALCULATION (SIMPLIFIED & INTERPRETABLE)
# ══════════════════════════════════════════════════════════════════════════════

def calculate_dropout_probability(signals):
    """
    Simple, interpretable probability calculation.
    Each dimension contributes independently.
    Risk contributions are 0-1 where 1 = maximum risk.
    """
    
    risk_contributions = {}
    
    # 1. Response time decay: 0-96 hours
    # 0-12 hrs → 0.0 risk, 36-96 hrs → 1.0 risk
    rt = signals['response_time_decay_hrs']
    risk_contributions['response_time'] = clip((rt - 12) / 84, 0, 1)
    
    # 2. Forum passive-active ratio: 1-80
    # 1-5 → 0.0 risk, 20-80 → 1.0 risk
    fr = signals['forum_passive_active_ratio']
    risk_contributions['forum'] = clip((fr - 5) / 75, 0, 1)
    
    # 3. Login fragmentation: 0-1 (higher = more fragmented = more risk)
    risk_contributions['login'] = signals['login_fragmentation_score']
    
    # 4. Resource depth shift: 0-1 (higher = shallow = more risk)
    risk_contributions['resource'] = signals['resource_depth_shift']
    
    # 5. Collaborative tool drift: 0-30 days
    td = signals['collaborative_tool_drift_days']
    risk_contributions['drift'] = clip(td / 25, 0, 1)
    
    # 6. Question quality: 1-6 (lower = worse = more risk)
    qq = signals['question_quality_level']
    risk_contributions['quality'] = 1 - clip((qq - 1) / 5, 0, 1)
    
    # 7. Peer centrality: 0-1 (lower = less central = more risk)
    risk_contributions['centrality'] = 1 - signals['peer_centrality_score']
    
    # 8. Optional activity rate: 0-1 (lower = abandoned = more risk)
    risk_contributions['optional'] = 1 - signals['optional_activity_rate']
    
    # 9. Submission rush: 0-48 hours (lower = more rushed = more risk)
    sr = signals['submission_rush_hrs']
    risk_contributions['rush'] = 1 - clip(sr / 36, 0, 1)
    
    # 10. Silence bursts: 0-10
    sb = signals['silence_burst_count']
    risk_contributions['silence'] = clip(sb / 6, 0, 1)
    
    # 11. Help seeking latency: 0-30 days
    hl = signals['help_seeking_latency_days']
    risk_contributions['help'] = clip(hl / 21, 0, 1)
    
    # 12. Feedback response rate: 0-1 (lower = ignores feedback = more risk)
    risk_contributions['feedback'] = 1 - signals['feedback_response_rate']
    
    # Average of all risk contributions
    avg_risk = sum(risk_contributions.values()) / len(risk_contributions)
    
    # Apply compression to map 0-1 to 0.02-0.75 with mid at 0.4
    # This creates realistic probability spread
    prob = 0.02 + 0.73 * np.tanh(3 * (avg_risk - 0.4))
    
    # Add noise to create realistic std dev
    prob = clip(prob + np.random.normal(0, 0.09), 0.02, 0.85)
    
    return prob


# ══════════════════════════════════════════════════════════════════════════════
# GENERATE ALL STUDENTS
# ══════════════════════════════════════════════════════════════════════════════

print("  🎲 Generating student profiles...")

profiles = generate_student_profiles(N_STUDENTS)

full_profiles = []

for i, signals in enumerate(profiles):
    prob = signals.pop('_raw_probability')
    true_risk = signals.pop('_true_risk')
    true_risk_prob = signals.pop('_true_risk_prob')
    
    device_count = random.choices([1, 2], weights=[0.55, 0.45])[0]
    monday_absence = random.choices([0, 1], weights=[0.78, 0.22])[0]
    tired_freq = clip(int(np.random.normal(2.5, 1.5)), 0, 6)
    whatsapp_silence = random.choices([0, 1], weights=[0.88, 0.12])[0]
    
    has_intervention = random.choices([0, 1], weights=[0.6, 0.4])[0]
    intervention_week = random.randint(2, 10) if has_intervention else 0
    intervention = intervention_type() if has_intervention else "none"
    
    full_profiles.append({
        "student_id": f"STU{str(i+1).zfill(4)}",
        "age": random.randint(12, 18),
        "gender": random.choice(["F", "M"]),
        "is_first_gen_learner": random.choices([0, 1], weights=[0.5, 0.5])[0],
        **signals,
        "device_count": device_count,
        "monday_absence_cluster": monday_absence,
        "tired_keyword_freq": tired_freq,
        "whatsapp_study_silence": whatsapp_silence,
        "dropout_probability": prob,
        "intervention_received": 1 if has_intervention else 0,
        "intervention_week": intervention_week,
        "intervention_type": intervention,
        "intervention_effectiveness": intervention_effectiveness(intervention, intervention_week, 1),
    })

print(f"  ✅ Generated {len(full_profiles)} profiles")


# ══════════════════════════════════════════════════════════════════════════════
# ASSIGN DROPOUT LABELS
# ══════════════════════════════════════════════════════════════════════════════

print("\n  🏷️  Assigning probabilistic dropout labels...")

# Pure probabilistic assignment
for profile in full_profiles:
    prob = profile['dropout_probability']
    dropout_label = 1 if random.random() < prob else 0
    profile['dropout_risk'] = dropout_label

# Add label noise
print(f"  🔀 Adding {LABEL_NOISE_RATE*100:.0f}% label noise...")
noise_count = 0
for profile in full_profiles:
    if random.random() < LABEL_NOISE_RATE:
        profile['dropout_risk'] = 1 - profile['dropout_risk']
        noise_count += 1

print(f"     Flipped {noise_count} labels")

# Assign stress_type
for profile in full_profiles:
    if profile['dropout_risk'] == 1:
        profile['stress_type'] = random.choice(['academic_struggle', 'home_financial_stress'])
    else:
        profile['stress_type'] = 'none'


# ══════════════════════════════════════════════════════════════════════════════
# CREATE DATAFRAME AND ANALYZE
# ══════════════════════════════════════════════════════════════════════════════

df = pd.DataFrame(full_profiles)

cols = ["student_id", "dropout_probability", "dropout_risk"] + \
       [c for c in df.columns if c not in ["student_id", "dropout_probability", "dropout_risk"]]
df = df[cols]

prob_array = df['dropout_probability'].values

print(f"\n  📊 Dropout Probability Distribution:")
print(f"     Mean: {prob_array.mean():.4f}")
print(f"     Std:  {prob_array.std():.4f}")
print(f"     Min:  {prob_array.min():.4f}")
print(f"     Max:  {prob_array.max():.4f}")
print(f"     P25:  {np.percentile(prob_array, 25):.4f}")
print(f"     P50:  {np.percentile(prob_array, 50):.4f}")
print(f"     P75:  {np.percentile(prob_array, 75):.4f}")
print(f"     P90:  {np.percentile(prob_array, 90):.4f}")

ambiguous = prob_array[(prob_array >= 0.30) & (prob_array <= 0.70)]
print(f"\n  🎯 Ambiguous Zone (30-70% probability): {len(ambiguous)} students ({len(ambiguous)/len(df)*100:.1f}%)")

dropout_rate = df['dropout_risk'].mean() * 100
print(f"\n  🏷️  Final dropout rate: {dropout_rate:.1f}%")

static_path = "data/synthetic/students.csv"
df.to_csv(static_path, index=False)
print(f"\n  ✅ Static dataset saved → {static_path}")
print(f"     Shape: {df.shape[0]} rows × {df.shape[1]} columns")


# ══════════════════════════════════════════════════════════════════════════════
# TEMPORAL DECAY
# ══════════════════════════════════════════════════════════════════════════════

def add_temporal_decay(df, weeks=12):
    print("\n  📈 Adding temporal decay simulation...")
    records = []
    
    for _, student in df.iterrows():
        risk = student['dropout_risk']
        
        for week in range(1, weeks + 1):
            row = student.to_dict()
            row['week'] = week
            
            if risk == 1:
                decay_factor = (week / weeks) ** 1.2
                
                row['response_time_decay_hrs'] = min(
                    student['response_time_decay_hrs'] * (1 + decay_factor * 0.5), 96
                )
                row['silence_burst_count'] = min(
                    student['silence_burst_count'] + (week * 0.25), 10
                )
                row['question_quality_level'] = max(
                    student['question_quality_level'] * (1 - decay_factor * 0.3), 1
                )
                row['optional_activity_rate'] = max(
                    student['optional_activity_rate'] * (1 - decay_factor * 0.5), 0
                )
                
                if student['intervention_received'] == 1 and week >= student['intervention_week']:
                    eff = student['intervention_effectiveness']
                    row['response_time_decay_hrs'] = max(
                        row['response_time_decay_hrs'] * (1 - eff * 0.4),
                        student['response_time_decay_hrs'] * 0.7
                    )
            else:
                improvement = 1 + (week / weeks) * 0.05
                row['question_quality_level'] = min(
                    student['question_quality_level'] * improvement, 6
                )
                row['response_time_decay_hrs'] = max(
                    student['response_time_decay_hrs'] * (1 - week * 0.008), 1
                )
            
            records.append(row)
    
    df_temporal = pd.DataFrame(records)
    print(f"  ✅ Time series created: {df_temporal.shape[0]} rows")
    return df_temporal


def add_early_warning_labels(df_temporal):
    print("  🏷️  Adding early warning labels...")
    
    df_temporal['weeks_until_dropout'] = None
    df_temporal['will_dropout_soon'] = 0
    
    for student_id in df_temporal['student_id'].unique():
        student_data = df_temporal[df_temporal['student_id'] == student_id]
        
        if student_data['dropout_risk'].iloc[0] == 1:
            for _, row in student_data.iterrows():
                weeks_left = max(0, 12 - row['week'])
                mask = (df_temporal['student_id'] == student_id) & (df_temporal['week'] == row['week'])
                df_temporal.loc[mask, 'weeks_until_dropout'] = weeks_left
                df_temporal.loc[mask, 'will_dropout_soon'] = 1 if weeks_left <= 4 else 0
        else:
            for _, row in student_data.iterrows():
                mask = (df_temporal['student_id'] == student_id) & (df_temporal['week'] == row['week'])
                df_temporal.loc[mask, 'weeks_until_dropout'] = 99
                df_temporal.loc[mask, 'will_dropout_soon'] = 0
    
    print("  ✅ Early warning labels added")
    return df_temporal


df_temporal = add_temporal_decay(df, WEEKS)
df_temporal = add_early_warning_labels(df_temporal)

temporal_path = "data/synthetic/students_timeseries.csv"
df_temporal.to_csv(temporal_path, index=False)
print(f"\n  ✅ Time series dataset saved → {temporal_path}")


print("\n" + "=" * 70)
print("  🎯 Dataset Generation Complete!")
print("")
print("  ✅ KEY METRICS:")
print(f"     • Probability range: {df['dropout_probability'].min():.3f} - {df['dropout_probability'].max():.3f}")
print(f"     • Probability std: {df['dropout_probability'].std():.4f}")
print(f"     • Students in ambiguous zone (30-70%): {len(ambiguous)} ({len(ambiguous)/len(df)*100:.1f}%)")
print(f"     • Final dropout rate: {dropout_rate:.1f}%")
print("")
print("  📁 Files created:")
print(f"     • {static_path}")
print(f"     • {temporal_path}")
print("=" * 70)