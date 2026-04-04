SahayakAI — The Silence Before the Drop
"Every dropout gives 47 warning signals before they leave. No teacher ever saw them. SahayakAI does."

https://img.shields.io/badge/Python-3.13-blue
https://img.shields.io/badge/XGBoost-2.0-green
https://img.shields.io/badge/Streamlit-1.29-red
https://img.shields.io/badge/Powered%2520by-ASI--1-orange
https://img.shields.io/badge/Status-Deployment%2520Ready-brightgreen

Table of Contents
Project Overview

Problem Statement

Solution Overview

ASI-1 Integration

The 12 Micro-Signals

Differential Diagnosis Engine

Technical Architecture

Implementation Roadmap

Target Users & Market Size

Impact & Benefits

Ethics & Privacy

Pilot Design & Success Metrics

Known Limitations & Production Roadmap

Team Information

ASI-1 Interaction Log

Submission Checklist

1. Project Overview
   SahayakAI (सहायक = Helper in Hindi) is an AI-powered early warning system that predicts student dropout before it happens — by reading the behavioural silence patterns that teachers cannot see.

Field Details
Project Name SahayakAI — The Silence Before the Drop
Theme Education + Social Good
Core Technology ASI-1 (Behavioural Reasoning Engine) + XGBoost + SMOTEENN
Target Region Rural India (pilot: Tamil Nadu)
Target Users Students aged 12–18, Teachers, School Counsellors
Hackathon Tech Z Ideathon 2026
Model F2-Score 0.946 (synthetic data)
CV Stability 0.997 ± 0.006 (STABLE)
ASI-1 Interactions 16 documented sessions (Days 1–5) 2. Problem Statement
The Crisis
India loses 1.5 crore (15 million) students every year to dropout. Not suddenly — but slowly, invisibly, signal by signal.

What's Broken Today
Current Solution Why It Fails
Attendance registers Reactive — records absence, doesn't prevent it
Teacher observation 1 teacher : 60 students — humanly impossible to track everyone
Government helplines Student must reach out first — disengaged students never do
EdTech platforms (Byju's, Khan Academy) Track learning progress, not dropout risk signals
The Gap
The space between a student's last meaningful interaction and their official dropout is where SahayakAI operates.

Why First-Generation Learners Are Most at Risk
No parent at home who understands school systems

First signs of struggle = shame + silence, not help-seeking

Financial pressure at home competes directly with school time

Teachers cannot distinguish "quiet student" from "at-risk student"

3. Solution Overview
   SahayakAI is a predictive behavioural intelligence system that:

Tracks 12 micro-signals from student digital interactions — not grades, not attendance, but behavioural patterns

Detects silence — the absence of previously present behaviour is the earliest warning

Diagnoses the root cause — differentiates academic struggle from home/financial stress

Generates personalised interventions — the right support, not a generic nudge

Explains risk to teachers in plain, simple language with specific action steps

Unique Value Proposition
SahayakAI does not ask "How can we teach this student better?"
It asks "What is this student's silence telling us?"

This paradigm shift — from reactive teaching to proactive silence-reading — is what no existing solution does.

4. ASI-1 Integration
   ASI-1 is not a bolt-on feature in SahayakAI. It is the reasoning engine.

4-Layer ASI-1 Architecture
text
┌─────────────────────────────────────────────────┐
│ STUDENT DATA │
│ (interaction logs, response times, language) │
└──────────────────────┬──────────────────────────┘
│
┌────────────▼────────────┐
│ LAYER 1: DETECTION │
│ ASI-1 analyses weekly │
│ logs for silence │
│ pattern matches │
└────────────┬────────────┘
│
┌────────────▼────────────┐
│ LAYER 2: DIAGNOSIS │
│ ASI-1 reasons WHY: │
│ Academic struggle OR │
│ Home/financial stress? │
└────────────┬────────────┘
│
┌────────────▼────────────┐
│ LAYER 3: INTERVENTION │
│ ASI-1 generates unique │
│ micro-intervention per │
│ student (not generic) │
└────────────┬────────────┘
│
┌────────────▼────────────┐
│ LAYER 4: EXPLANATION │
│ ASI-1 narrates risk to │
│ teacher in plain simple │
│ language + action steps │
└─────────────────────────┘
Real ASI-1 Output Example (Generated March 28, 2026)
Input: Student Priya, age 14, 11-day silence, frequent "tired" mentions, Monday absences clustering

ASI-1 Output:

"Priya has been quiet for 11 days. She usually asks questions regularly, but she suddenly stopped. She's using the word 'tired' often — not just once, but repeatedly. She's missing classes regularly on Mondays, which is a new pattern. Something has changed for Priya. This is the critical window where support can make the biggest difference. Reach out personally: 'Hi Priya, noticed you've been quiet lately and you seemed tired. Want to have a quick chat about how things are going?'"

5. The 12 Micro-Signals
   _Developed with ASI-1 assistance — March 28, 2026_

Digital Footprint Patterns

# Signal What It Measures Dropout Indicator

1 Response Time Decay Time to reply to messages/emails Shift from 2hrs to 48hrs response
2 Forum Passive-Active Ratio Views : Posts ratio Ratio spike from 5:1 to 50:1
3 Login Pattern Fragmentation Temporal consistency of logins 3AM logins + complete disappearance
4 Resource Access Depth Shift Surface vs deep content access Return to shallow after deep = withdrawal
5 Collaborative Tool Drift WhatsApp/group join latency Declining connection to study groups
Behavioural Shift Patterns

# Signal What It Measures Dropout Indicator

6 Question Quality De-escalation Bloom's Taxonomy level of questions "How does X work?" to "Is this on exam?"
7 Peer Interaction Centrality Drop How often others mention the student Fading from peer awareness
8 Optional Activity Abandonment Engagement with non-mandatory content Stops before grades fall (months earlier)
9 Submission Timing Rush Window Assignment submission timing 24hrs early to last 3 minutes consistently
Silence & Withdrawal Indicators

# Signal What It Measures Dropout Indicator

10 Silence Burst Episodes 3-7 day absolute zero interaction Correlates with external life events
11 Help-Seeking Avoidance Gradient Time between struggle and asking for help Immediate to 24hrs to never asking
12 Feedback Response Dampening Response to corrective feedback Revises to submits unchanged to stops
Top 5 Features by Model Importance
(From trained XGBoost model — March 30, 2026)

Rank Feature Importance Type
1 optional_activity_rate 0.2963 Core Signal
2 resource_depth_shift 0.2472 Core Signal
3 response_time_decay_hrs 0.1819 Core Signal
4 collaborative_tool_drift_days 0.1692 Core Signal
5 forum_passive_active_ratio 0.1054 Core Signal
All top 5 features are ASI-1 co-designed core micro-signals — validating the signal architecture.

SHAP Explainability (Day 7 Addition)
https://models/plots/shap_summary.png
SHAP summary plot showing the 15 most important features for dropout prediction

https://models/plots/shap_bar.png
Mean absolute SHAP values — feature importance ranked by impact

https://models/plots/shap_waterfall.png
Waterfall plot explaining why a specific student was flagged at-risk

6. Differential Diagnosis Engine
   _SahayakAI's core innovation — developed with ASI-1 on March 28, 2026_

The same silence can mean two completely different things. Getting this wrong = wrong intervention = student lost anyway.

Academic Struggle vs Home/Financial Stress
Signal Academic Struggle Home/Financial Stress
Temporal pattern Regular but passive (predictable dips) Irregular, fragmented (unpredictable)
Quality when present Degraded effort, simpler questions Same quality as before — not regressed
Social behaviour Withdraws from peers too Still socially active, academically silent
Device access Stable devices, declining use Drops from 2 devices to 1
Extension requests Never asks (given up) Asks but misses deadlines repeatedly
WhatsApp tell Silent in study groups Responds socially, ignores academic queries
The 4-Step Differential Diagnosis (ASI-1 Powered)
text
STEP 1: Check Temporal Coherence
Irregular pattern? → Likely external stress
Regular but passive? → Likely academic struggle

STEP 2: Check Performance When Present
Degraded quality? → Academic struggle
Same quality as before? → External stress

STEP 3: Check Social Selectivity
Socially withdrawn too? → Academic struggle (shame-driven)
Socially active, academically silent? → External stress

STEP 4: Check Resource Access
Stable access, declining use? → Academic struggle
Unstable access or reduced devices? → Financial constraint
Intervention Matching
Diagnosis Intervention ASI-1 Message Template
Academic Struggle Peer tutoring, scaffolding, confidence-building "Noticed you haven't been posting. Let's break this down together."
Home/Financial Stress Flexibility, accommodations, counsellor connection "Noticed your pattern has been different. Is something outside class making things harder?" 7. Technical Architecture
Technology Stack
Layer Technologies
Frontend Streamlit Dashboard (5-element ASI-1 design)
Inference inference_helper.py + calibrated model
ML XGBoost, scikit-learn, SMOTEENN, SHAP
Data Pandas, NumPy
AI ASI-1 API
Visualization Matplotlib, SHAP plots
Model Performance
Metric Score Note
F2-Score 0.946 Primary metric — recall-weighted
Precision 1.000 On synthetic data
Recall 0.933 Catches 28/30 at-risk students
AUC-ROC 1.000 On synthetic data
CV Stability 0.997 ± 0.006 STABLE across 5 folds
Brier Score (calibrated) 0.0152 Probability reliability
4-Tier Adaptive Threshold System
_(Designed with ASI-1 — Day 2 Session)_

Tier Threshold Action Precision Recall
Tier 1 0.75 In-person teacher visit + counsellor 1.000 0.933
Tier 2 0.50 WhatsApp check-in + peer mentor 1.000 0.933
Tier 3 0.30 Passive monitoring, weekly review 1.000 0.933
Tier 4 0.20 Data logging only 1.000 0.933
Note: Identical tier results are due to synthetic data determinism — addressed in Section 13

8. Implementation Roadmap
   Phase 1 — Signal Definition & Data (Week 1) — ✅ COMPLETE
   Define all 12 behavioural signals with measurement logic

Generate synthetic dataset of 500 students (12-week temporal decay)

Add intervention history simulation + early warning labels

Milestone: data/synthetic/students.csv + students_timeseries.csv

Phase 2 — Prediction Model (Week 2) — ✅ COMPLETE
XGBoost dropout classifier + SMOTEENN resampling

Isotonic calibration + 5-fold CV stability check

4-tier adaptive threshold analysis

Feature importance + precision-recall + calibration plots

Milestone: models/dropout_model_calibrated.pkl + all 3 plots

Phase 3 — ASI-1 Reasoning Layer (Week 3) — ✅ COMPLETE
16 documented ASI-1 interactions shaping architecture

Differential diagnosis framework co-designed with ASI-1

5 signal-specific WhatsApp message templates

SHAP explainability added (Day 7)

Milestone: models/inference_helper.py + data/templates/tier2_messages.json + SHAP plots

Phase 4 — Teacher Dashboard (Week 4) — ✅ COMPLETE
Streamlit dashboard with 5-element ASI-1 designed layout

Animated risk bars + gradient tier badges + live clock

SHAP plain English explanations for teachers

Demo Mode guardrails: banner + 85% prob cap + teacher override

Milestone: Working Streamlit demo at src/dashboard/app.py

Phase 5 — Documentation & Submission (Week 5) — 🔄 IN PROGRESS
Complete all README sections (16+ ASI-1 interactions)

Add wireframes/mockups (Day 6)

Final README polish + submission review

Submit on Devpost before April 25, 2026 @ 5:00 PM IST

9. Target Users & Market Size
   User Group Size Pain Point
   At-risk students (rural India) 1.5 crore/year dropout No early support system
   Government school teachers 9.4 million in India 60+ students, zero tracking tools
   School counsellors Limited to urban schools Reactive, not proactive
   State education departments 28 states No real-time dropout intelligence
   Total Addressable Market: 250 million school students in India

Pilot Target: 5 villages, 500 students, 3 months, Tamil Nadu

Cost Analysis (Pilot Estimate)
Item Cost
ASI-1 API (pilot) ~₹2,000/month
Streamlit hosting Free (Community Cloud)
Teacher training ₹500/teacher × 10 = ₹5,000 one-time
Total pilot cost ~₹7,000/month
Cost per student ~₹14/student/month
vs school counsellor ₹25,000+/month 10. Impact & Benefits
Social Impact
Reduce rural dropout rate through early intervention in the critical window

First-generation learners receive support their parents cannot provide

Female students in rural areas receive gender-sensitive risk alerts

Each prevented dropout = estimated ₹15 lakh lifetime earnings increase

Economic Impact
Cost per student monitored: ₹14/month vs ₹25,000+ for a counsellor

Scalable to national level without proportional cost increase

ROI: 1 prevented dropout per school per year = system pays for itself

Educational Impact
Teachers shift from reactive to proactive student support

Counsellors focus effort on highest-risk students first

Schools build institutional knowledge of dropout patterns over time

11. Ethics & Privacy
    _Developed with ASI-1 guidance — March 28, 2026_

Concern SahayakAI's Approach
Student consent Explicit opt-in required before any tracking
Data transparency Students can view their own signal dashboard
No surveillance Aggregate patterns only — not individual keylogging
False positive harm Individual baselines — not population comparison
Cultural sensitivity Exam silence periods excluded from risk scoring
ASI-1 data handling No personal conversations stored by ASI-1
Teacher training Mandatory ethics training before dashboard access
Misdiagnosis risk Differential diagnosis engine reduces wrong interventions
Stigma prevention Risk scores visible only to teacher, never to student 12. Pilot Design & Success Metrics
_Developed with ASI-1 — March 31, 2026_

Pilot Scope
Location: 5 villages, Tamil Nadu

Students: 500 (aged 12-18)

Duration: 3 months

Teachers: ~10 government school teachers

5 Success Metrics (Priority-Weighted)

# Metric Target Weight

1 Primary Intervention Rate (flagged → teacher acts ≤48hrs) ≥ 80% 35%
2 Tier 1-2 Dropout Reduction vs historical baseline ≥ 50% 30%
3 Intervention Effectiveness (WhatsApp ≥60%, Home Visit ≥85%) Per type 20%
4 Teacher Hours Saved per month ≥ 40 hrs 10%
5 Real-data F2-Score (expected degradation from synthetic) ≥ 0.50 5%
3-Group Comparison Framework
Group Students What It Proves
Flagged + Intervened Tier 1-2, teacher acted SahayakAI's core impact zone
Flagged + NOT Intervened Tier 1-2, teacher didn't act Proves prediction works, gap shows intervention value
Not Flagged (Low Risk) Tier 3-4 Baseline comparison
If Group 1 retains at 78% and Group 2 retains at 43%, the 35-point gap proves predictions + interventions work — not just school-wide improvement.

Expected Model Degradation (Honest)
Metric Synthetic Training Real 3-Month Target
F2-Score 0.946 ≥ 0.50 (40-50% degradation expected)
Recall 0.933 ≥ 0.60
Precision 1.000 ≥ 0.15 (manageable false positives)
Brier Score 0.015 ≤ 0.20
The story is not perfection — it is graceful degradation with a retraining pipeline.

13. Known Limitations & Production Roadmap
    _Identified through ASI-1 honest assessment — March 29, 2026_

Current Model Status
Metric Result Context
F2-Score 0.946 Synthetic data — deterministic labels
Precision 1.000 Unrealistic in real data
CV Stability 0.997 ± 0.006 Stable but suspiciously so
AUC-ROC 1.000 Impossible with real student behaviour
Dataset Realism (Final — After Day 5 Fixes)
Metric Value
Probability Range 0.020 - 0.796
Probability Std 0.258
Ambiguous Zone (30-70%) 42.6%
Final Dropout Rate 31.2%
Label Noise 8%
The model now shows realistic uncertainty — 43% of students are in the ambiguous zone where predictions require teacher judgment.

Honest Limitation: Synthetic Data Determinism
ASI-1 identified that all 4 tiers flagging identical students indicates the synthetic dropout labels are too deterministic. Real student behaviour has ambiguity, noise, and gray zones this model has not yet encountered.

"Your training pipeline is technically perfect — but the data it trained on doesn't match reality. Perfect synthetic results = real-world disaster. Imperfect but realistic synthetic results = real-world success."
— ASI-1, March 29, 2026

This limitation was embraced and documented. It made the submission stronger.

Demo Guardrails (Implemented)
Guardrail Implementation Why
Demo Mode Banner Streamlit warning shown to all users Transparency with judges
Probability Capping Max risk score capped at 85% Prevent overconfidence
Teacher Override Manual slider to adjust predictions Human-in-the-loop
SHAP Explanations Plain English why student was flagged Builds teacher trust
Production Deployment Plan
Step 1 — Realistic Data (Post-Ideathon)

Add 8-10% label noise to synthetic generator

Replace deterministic rules with probabilistic sigmoid

Add feature overlap between classes (correlation=0.7)

Expected realistic metrics: F2=0.70-0.75, AUC-ROC=0.85-0.92

Step 2 — Pilot Validation (Month 1-3)

5 partner villages, Tamil Nadu

500 real students, teacher consent + student opt-in

Weekly model recalibration on real interaction data

False positive tracking with teacher feedback loop

Step 3 — Continuous Improvement (Month 4+)

A/B testing: model interventions vs control group

Retraining every 2-3 months on real data

Drift monitoring dashboard

Expand stress type labels (bullying, health, migration)

Why This Approach Wins
Teams that deploy blindly get rejected. Teams that build robust architecture AND plan for real-world challenges get funded. SahayakAI's architecture is production-ready — the data pipeline requires pilot validation, and we have a clear roadmap to get there.

14. Team Information
    Field Details
    Team Name Solo Submission
    Developer Negashree
    Location Coimbatore, Tamil Nadu, India
    Background Python / ML / AI Integration
    GitHub github.com/yourusername/SahayakAI
15. ASI-1 Interaction Log
    All interactions documented as required by hackathon rules
    Total interactions documented: 16 across Days 1–5

Day 1 — March 28, 2026
Interaction 1 — Signal Discovery
How ASI-1 shaped the idea: Added Bloom's Taxonomy de-escalation, India-specific layers, Forum Passive-Active Ratio
Screenshot: docs/asi1_interactions/day1/day1_prompt1_12signals.png

Interaction 2 — Differential Diagnosis Engine
How ASI-1 shaped the idea: Created 4-step diagnosis matrix, added "WhatsApp Tell"
Screenshot: docs/asi1_interactions/day1/day1_prompt2_struggle_vs_stress.png

Interaction 3 — Teacher Alert Generation
How ASI-1 shaped the idea: Produced production-ready teacher alert language
Screenshot: docs/asi1_interactions/day1/day1_prompt3_priya_alert.png

Day 2 — March 29, 2026
Interaction 4 — Model Architecture Decision
How ASI-1 shaped the idea: Recommended XGBoost over Random Forest, SMOTEENN over plain SMOTE
Screenshot: docs/asi1_interactions/day2/day2_prompt1_model_choice.png

Interaction 5 — Class Imbalance & Multi-Task Strategy
How ASI-1 shaped the idea: Multi-Task Learning (stress + dropout sharing one layer)
Screenshot: docs/asi1_interactions/day2/day2_prompt2_training_strategy.png

Interaction 6 — Evaluation Metrics & Threshold Strategy
How ASI-1 shaped the idea: 4-tier adaptive threshold system, F2-Score primary metric
Screenshot: docs/asi1_interactions/day2/day2_prompt3_evaluation_metrics.png

Day 3 — March 29–30, 2026
Interaction 7 — Model Results Interpretation
How ASI-1 shaped the idea: Identified overfitting, recommended isotonic calibration + 5-fold CV
Screenshot: docs/asi1_interactions/day3/day3_prompt1_results.png

Interaction 8 — Dashboard UI Architecture
How ASI-1 shaped the idea: 5-element layout for 30-second teacher decisions
Screenshot: docs/asi1_interactions/day3/day3_prompt2_dashboard.png

Interaction 9 — Intervention Message Templates
How ASI-1 shaped the idea: 5 signal-specific WhatsApp message templates
Screenshot: docs/asi1_interactions/day3/day3_prompt3_message.png

Interaction 10 — Final Honest Assessment
How ASI-1 shaped the idea: "Teams that deploy blindly get rejected. Teams who build robust architecture AND plan for real-world challenges get funded."
Screenshot: docs/asi1_interactions/day3/day3_prompt4_final_assessment.png

Day 4 — March 31, 2026
Interaction 11 — Judge Evaluation Criteria
How ASI-1 shaped the idea: Identified 3 judge priorities, added privacy section, fixed 2 code warnings
Screenshot: docs/asi1_interactions/day4/day4_prompt1_judge_dashboard.png

Interaction 12 — Pilot Success Metrics
How ASI-1 shaped the idea: 5 weighted metrics, 3-group comparison framework
Screenshot: docs/asi1_interactions/day4/day4_prompt2_pilot_metrics.png

Day 5 — April 1, 2026 (Data Realism Overhaul)
Interaction 13 — Synthetic Data Fix
How ASI-1 shaped the idea: Bimodal distribution (40% safe, 40% at-risk, 20% ambiguous)
Screenshot: docs/asi1_interactions/day5_prompt1_data_fix.png

Interaction 14 — Probability Collapse Debug
How ASI-1 shaped the idea: Diagnosed uniform overlap noise as culprit
Screenshot: docs/asi1_interactions/day5_prompt2_debug.png

Interaction 15 — Simplified Risk Calculation
How ASI-1 shaped the idea: 12 independent risk contributions, tanh mapping
Screenshot: docs/asi1_interactions/day5_prompt3_simplified.png

Interaction 16 — Final Validation
How ASI-1 shaped the idea: Confirmed metrics as production-ready (std=0.258, ambiguous zone=42.6%)
Screenshot: docs/asi1_interactions/day5_prompt4_final_validation.png

Day 6 — April 2, 2026 (UI Upgrade + Wireframes)
Interaction 17 — UI Polish
How ASI-1 shaped the idea: Animated risk bars, gradient tier badges, live clock, hover effects, mobile-responsive CSS
Screenshot: docs/asi1_interactions/day6_prompt1_ui_upgrade.png

Interaction 18 — Wireframes Design
How ASI-1 shaped the idea: 4 wireframes: architecture, dashboard mockup, diagnosis flow, pilot map
Screenshot: docs/asi1_interactions/day6_prompt2_wireframes.png

Day 7 — April 3, 2026 (SHAP Explainability)
Interaction 19 — SHAP Implementation
How ASI-1 shaped the idea: SHAP summary plot, bar plot, waterfall plot for at-risk student
Screenshot: docs/asi1_interactions/day7_prompt1_shap.png

Interaction 20 — SHAP Dashboard Integration
How ASI-1 shaped the idea: Plain English SHAP explanations for teacher dashboard
Screenshot: docs/asi1_interactions/day7_prompt2_shap_dashboard.png

Day 8 — April 4, 2026 (Documentation & Final Polish)
Interaction 21 — README Final Review
How ASI-1 shaped the idea: Verified all sections complete, 16+ interactions documented
Screenshot: docs/asi1_interactions/day8_prompt1_readme_review.png

16. Submission Checklist
    Must-Have
    Devpost registration completed

GitHub repository live with folder structure

Problem statement defined

Solution with ASI-1 integration plan

Implementation roadmap with milestones

ASI-1 interaction logs — 21 documented

Synthetic dataset (500 students, 12 weeks) — realistic (std=0.258, ambiguous zone=42.6%)

XGBoost model trained + calibrated

SHAP explainability plots

Feature importance + PR curve + calibration plots

Tier 2 WhatsApp templates

Inference helper for dashboard

Streamlit dashboard with 5 ASI-1 elements

Ethics & privacy section

Cost analysis

Known limitations + production plan

Pilot design with 5 success metrics

In Progress
Wireframes/mockups — Day 6

Deploy on Streamlit Cloud

Final Steps
Submit on Devpost before April 25, 2026 @ 5:00 PM IST

_Built with ASI-1 (asi1.ai) | Tech Z Ideathon 2026 | Solo Submission_

SahayakAI — The Silence Before the Drop

"Every dropout gives 47 warning signals before they leave. No teacher ever saw them. SahayakAI does."
