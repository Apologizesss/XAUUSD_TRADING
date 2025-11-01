# 🤖 Phase A: Model Training - Complete Summary

**Status:** ✅ **COMPLETED**  
**Date:** November 1, 2025  
**Duration:** ~45 minutes

---

## 🎯 Mission Accomplished

Successfully completed comprehensive model training pipeline including:
- ✅ Feature selection (143 → 42 features)
- ✅ Data preprocessing pipeline
- ✅ XGBoost baseline model
- ✅ Random Forest model
- ✅ Ensemble model (soft voting)

---

## 📊 Phase A Results Summary

### **1. Feature Selection** 🎯

**Objective:** Reduce feature set from 143 to optimal size

**Methodology:**
- Remove perfect duplicates (r = 1.000)
- Remove redundant moving averages
- Remove constant/low-variance features
- Remove high correlation features (|r| ≥ 0.95)

**Results:**
- **Original features:** 143
- **Removed features:** 101 (-70.6%)
- **Final features:** 42

**Breakdown of Removals:**
- Perfect duplicates: 14 features
- Redundant moving averages: 4 features
- Constant/low-variance: 11 features
- High correlation: 25 features
- Others: 47 features

**Final 42 Features by Category:**

| Category | Count | Examples |
|----------|-------|----------|
| **Moving Averages** | 3 | VOL_SMA_10, VOL_SMA_20, VOL_SMA_50 |
| **Momentum** | 10 | MACD, RSI_14/28, CCI, STOCH_K, WILLR, ROC_20/50, MOM |
| **Volatility** | 4 | ATR_14, BB_pct_b, DONCH_lower, HL_range_pct |
| **Volume** | 2 | MFI, VOL_ratio |
| **Time** | 11 | hour, hour_cos/sin, day_sin, week_of_year, sessions, is_liquid_hours |
| **Statistical** | 6 | kurt_10/20/50, skew_10/20/50 |
| **Price Action** | 1 | body_size_pct |
| **Other** | 5 | ADX, ADX_plus/minus, dist_to_resistance, lower_shadow |

**Key Removals:**
- All SMA/EMA price moving averages (too correlated with DONCH_lower)
- Bollinger/Keltner middle bands (duplicates of SMA_20/EMA_20)
- Support/Resistance (duplicates of Donchian bands)
- Time duplicates (is_first_day_of_week, is_last_day_of_week, etc.)

---

### **2. Data Preprocessing Pipeline** 🔧

**Features Implemented:**
- ✅ Multiple scaling methods (Standard, MinMax, Robust)
- ✅ Time-series aware train/val/test splits
- ✅ Multiple target types (classification, regression, multiclass)
- ✅ Sequence generation for LSTM/RNN (60-period lookback)
- ✅ Class weighting for imbalance handling
- ✅ Data validation and quality checks

**Data Splits:**
```
Total samples: 5,961 (M15 timeframe)

Train:      4,291 samples (71.98%)
Validation:   477 samples ( 8.00%)
Test:       1,193 samples (20.01%)
```

**Target Distribution (Binary Classification):**
```
Class 0 (Down/Hold):  2,898 samples (48.62%)
Class 1 (Up/Buy):     3,063 samples (51.38%)

Class weights:
  Class 0: 1.0241
  Class 1: 0.9770
```

**Sequence Data (for LSTM):**
```
X_train_seq: (4,231, 60, 42)  # samples, timesteps, features
X_val_seq:     (417, 60, 42)
X_test_seq:  (1,133, 60, 42)
```

---

### **3. Model Training Results** 🤖

#### **A) XGBoost Baseline Model**

**Hyperparameters:**
```python
{
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 3,
    'gamma': 0.1,
    'reg_alpha': 0.1,      # L1 regularization
    'reg_lambda': 1.0,     # L2 regularization
    'scale_pos_weight': 1.048
}
```

**Performance:**

| Dataset | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---------|----------|-----------|--------|-----|---------|
| **Train** | 95.74% | 95.15% | 96.58% | 95.86% | 99.26% |
| **Validation** | 48.01% | 52.81% | 60.38% | 56.34% | 48.30% |
| **Test** | **50.29%** | 50.51% | 74.58% | 60.23% | **51.42%** |

**Issues:**
- ❌ **Severe overfitting:** Train: 95.74%, Test: 50.29% (gap of 45.45%)
- ❌ **Poor generalization:** Test accuracy barely above random (50%)
- ❌ **Low ROC-AUC:** 51.42% (only 1.42% better than coin flip)

**Top 5 Features (by importance):**
1. ROC_50 (2.87%)
2. CCI (2.70%)
3. MACD_hist (2.69%)
4. ADX (2.66%)
5. HL_range_pct (2.65%)

---

#### **B) Random Forest Model**

**Hyperparameters:**
```python
{
    'n_estimators': 200,
    'max_depth': 10,
    'min_samples_split': 20,
    'min_samples_leaf': 10,
    'max_features': 'sqrt',
    'max_samples': 0.8,
    'bootstrap': True,
    'oob_score': True,
    'class_weight': 'balanced'
}
```

**Performance:**

| Dataset | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---------|----------|-----------|--------|-----|---------|
| **Train** | 87.07% | 86.88% | 88.02% | 87.45% | 94.36% |
| **Validation** | 53.25% | 55.41% | 81.13% | 65.85% | 49.84% |
| **Test** | **50.71%** | 50.67% | 89.70% | 64.75% | **52.38%** |
| **OOB Score** | **51.74%** | - | - | - | - |

**Issues:**
- ❌ **Still overfitting:** Train: 87.07%, Test: 50.71% (gap of 36.36%)
- ⚠️ **Barely better than random:** Test accuracy only 0.71% above 50%
- ⚠️ **High recall, low precision:** Predicts "up" too often (89.70% recall)

**Improvements over XGBoost:**
- ✅ Less overfitting (87.07% vs 95.74% train)
- ✅ Better validation accuracy (53.25% vs 48.01%)
- ✅ Slightly better test accuracy (50.71% vs 50.29%)
- ✅ Better ROC-AUC (52.38% vs 51.42%)

**Top 5 Features (by importance):**
1. ATR_14 (3.58%)
2. lower_shadow (3.57%)
3. VOL_ratio (3.52%)
4. VOL_SMA_10 (3.52%)
5. HL_range_pct (3.45%)

---

#### **C) Ensemble Model (Soft Voting)**

**Configuration:**
- Models: XGBoost + Random Forest
- Voting: Soft (probability averaging)
- Weights: Equal (1.0, 1.0)

**Performance:**

| Dataset | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---------|----------|-----------|--------|-----|---------|
| **Train** | 94.55% | 93.68% | 95.81% | 94.73% | 98.94% |
| **Validation** | 52.41% | 55.69% | 70.19% | 62.10% | 51.03% |
| **Test** | **50.21%** | 50.40% | 83.55% | 62.88% | **51.93%** |

**Result:**
- ⚠️ Ensemble performs **between** the two individual models
- ⚠️ Not better than Random Forest alone
- ✅ More balanced recall (83.55%) than Random Forest (89.70%)

---

### **4. Model Comparison** ⚔️

**Test Set Rankings:**

| Rank | Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|------|-------|----------|-----------|--------|-----|---------|
| 🥇 **1st** | **Random Forest** | **50.71%** | 50.67% | 89.70% | 64.75% | **52.38%** |
| 🥈 **2nd** | XGBoost | 50.29% | 50.51% | 74.58% | 60.23% | 51.42% |
| 🥉 **3rd** | Ensemble | 50.21% | 50.40% | 83.55% | 62.88% | 51.93% |

**Winner: Random Forest** 🏆
- Best test accuracy: 50.71%
- Best ROC-AUC: 52.38%
- Less overfitting than XGBoost

---

## ⚠️ Critical Issues Identified

### **Problem 1: All Models Perform Near Random (50%)**

**Evidence:**
- XGBoost: 50.29% accuracy (0.29% above random)
- Random Forest: 50.71% accuracy (0.71% above random)
- Ensemble: 50.21% accuracy (0.21% above random)
- ROC-AUC scores: 51-52% (barely above 50%)

**Interpretation:**
- Models cannot predict price direction better than coin flip
- Features don't contain enough predictive signal
- Target (next bar direction) may be too noisy/random

### **Problem 2: Severe Overfitting**

**Evidence:**
- XGBoost gap: 95.74% (train) → 50.29% (test) = **45.45% drop**
- Random Forest gap: 87.07% (train) → 50.71% (test) = **36.36% drop**
- Ensemble gap: 94.55% (train) → 50.21% (test) = **44.34% drop**

**Interpretation:**
- Models memorize training patterns that don't generalize
- Regularization (reg_alpha, reg_lambda) insufficient
- May need simpler models or different approach

### **Problem 3: High Recall, Low Precision**

**Evidence:**
- Random Forest recall: 89.70% (predicts "up" on 89.7% of up-moves)
- Random Forest precision: 50.67% (only half of "up" predictions correct)
- Class imbalance: 51.38% up vs 48.62% down (nearly balanced)

**Interpretation:**
- Models bias toward predicting "up" (majority class)
- Many false positives
- Not useful for actual trading (too many bad signals)

---

## 🔍 Root Cause Analysis

### **Why Are Models Failing?**

**1. Target Variable Problem:**
- Predicting next-bar direction (M15 = 15 minutes)
- 15-minute movements are extremely noisy
- Market microstructure dominates over trends
- **Solution:** Try longer prediction horizons (predict 1-hour, 4-hour, or daily moves)

**2. Feature Quality:**
- Current features may not capture predictive patterns
- Removed too many price-based features (all SMAs/EMAs)
- Time-based features may not be relevant for 15-min prediction
- **Solution:** Re-engineer features, focus on volatility/momentum

**3. Market Efficiency:**
- Gold (XAUUSD) is highly liquid and efficient
- Short-term price movements (~50% predictable = random walk)
- Technical indicators lag price (by definition)
- **Solution:** Add external factors (sentiment, macro data, order flow)

**4. Model Architecture:**
- Tree-based models (XGBoost, RF) may not capture temporal dependencies
- Need sequential models (LSTM, GRU) for time-series
- **Solution:** Train LSTM with 60-period sequences

**5. Overfitting Strategy:**
- Current regularization insufficient
- Need stronger constraints: lower depth, higher min_samples
- **Solution:** More aggressive regularization, simpler models

---

## 💡 Lessons Learned

### **What Worked:**
✅ Feature selection reduced dimensions effectively (143→42)  
✅ Random Forest less prone to overfitting than XGBoost  
✅ Data preprocessing pipeline robust and reusable  
✅ Time-series aware splits prevent data leakage  
✅ Class weighting handles imbalance properly  

### **What Didn't Work:**
❌ Predicting next-bar (15-min) direction too noisy  
❌ Technical indicators alone insufficient  
❌ Tree-based models overfit despite regularization  
❌ Ensemble didn't improve over best individual model  

### **Surprising Findings:**
- Top features: Volatility (ATR, HL_range) > Price (removed EMAs)
- Time features (hour, sessions) less important than expected
- Statistical features (kurt, skew) moderately useful
- Momentum indicators (ROC, MACD) rank high but don't translate to accuracy

---

## 📁 Deliverables

### **Code:**
```
src/models/
├── feature_selector.py           (Feature selection module)
├── data_preprocessor.py          (Data preprocessing pipeline)
├── train_xgboost.py              (XGBoost training script)
├── train_random_forest.py        (Random Forest training script)
└── ensemble.py                   (Ensemble model creation)
```

### **Models:**
```
results/models/
├── xgboost/
│   ├── xgboost_baseline.pkl
│   ├── model_metadata.json
│   └── feature_importance.png
├── random_forest/
│   ├── random_forest_baseline.pkl
│   ├── model_metadata.json
│   └── feature_importance.png
└── ensemble/
    ├── ensemble_soft_voting.pkl
    ├── ensemble_metadata.json
    └── model_comparison.csv
```

### **Data:**
```
results/feature_selection/
├── selected_features.json        (42 selected features)
├── XAUUSD_M15_selected_features.csv
└── feature_selection_report.txt
```

---

## 🚀 Recommendations for Next Steps

### **Phase A (Continued) - Improvements:**

**1. Change Target Variable** ⏰
```python
# Instead of next bar:
target = (close.shift(-1) > close).astype(int)

# Try longer horizons:
target = (close.shift(-4) > close).astype(int)  # 1 hour (4 x 15min)
target = (close.shift(-16) > close).astype(int)  # 4 hours
target = (close.shift(-96) > close).astype(int)  # 1 day
```

**2. Better Features** 🔧
- Add back some price moving averages (EMA_20, SMA_50)
- Create feature interactions (RSI * ATR, MACD / volatility)
- Add volatility regime indicators (VIX-like)
- Volume analysis features
- Order imbalance indicators

**3. Train LSTM Model** 🧠
- Use 60-period sequences (already prepared)
- Capture temporal patterns
- Bidirectional LSTM architecture
- Add attention mechanism

**4. Stronger Regularization** 🔒
```python
# XGBoost:
max_depth = 3  # (was 6)
min_child_weight = 10  # (was 3)
reg_alpha = 2.0  # (was 0.1)
reg_lambda = 10.0  # (was 1.0)

# Random Forest:
max_depth = 5  # (was 10)
min_samples_leaf = 50  # (was 10)
```

**5. Alternative Approaches** 🎯
- **Regression:** Predict return magnitude (not just direction)
- **Multi-class:** 3 classes (down, neutral, up) with thresholds
- **Binary with threshold:** Only trade if probability > 0.6
- **Anomaly detection:** Detect unusual patterns for entries

---

### **Phase B - Backtesting & Strategy:**

**1. Strategy Design**
- Only trade high-confidence signals (prob > 0.65)
- Add stop-loss and take-profit levels
- Position sizing based on confidence
- Risk management (max 2% per trade)

**2. Backtest Metrics**
- Sharpe ratio (target: > 1.5)
- Max drawdown (target: < 15%)
- Win rate (target: > 55%)
- Profit factor (target: > 1.5)
- Total return vs buy-and-hold

**3. Walk-Forward Analysis**
- Retrain every month
- Out-of-sample testing
- Parameter stability over time

---

### **Phase C - Advanced Models:**

**1. LSTM/GRU**
- 2-3 layer LSTM with dropout
- 60-period lookback window
- Batch normalization
- Early stopping

**2. CNN for Time Series**
- 1D convolutions
- Extract local patterns
- Combine with LSTM (CNN-LSTM)

**3. Transformer/Attention**
- Self-attention mechanism
- Positional encoding for time
- Multi-head attention

**4. Advanced Ensemble**
- Stacking with meta-learner
- Weighted by recent performance
- Dynamic weight adjustment

---

## 📊 Performance Targets (Revised)

**Realistic Targets for Gold Trading:**

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| Test Accuracy | > 52% | > 55% | > 58% |
| ROC-AUC | > 0.55 | > 0.60 | > 0.65 |
| Sharpe Ratio | > 1.0 | > 1.5 | > 2.0 |
| Max Drawdown | < 20% | < 15% | < 10% |
| Win Rate | > 52% | > 55% | > 60% |
| Profit Factor | > 1.2 | > 1.5 | > 2.0 |

**Note:** Current models (50-51% accuracy) are **below minimum targets** and not tradeable.

---

## 🎯 Phase A Status

**Overall Completion:** 🟡 **60% Complete**

**Completed:** ✅
- Feature selection (42 features)
- Data preprocessing pipeline
- XGBoost baseline (50.29% test)
- Random Forest model (50.71% test)
- Ensemble model (50.21% test)

**Needs Improvement:** ⚠️
- Model accuracy (target: >55%, actual: ~50%)
- Overfitting (train-test gap: 35-45%)
- Feature engineering (need better features)

**Not Started:** ⏳
- LSTM model with sequences
- CNN model
- Hyperparameter optimization (full grid search)
- Advanced ensemble (stacking)
- Model interpretation (SHAP values)

---

## 💭 Final Thoughts

**What We Learned:**
1. **Short-term prediction is hard:** 15-minute gold price movements are essentially random
2. **Technical indicators have limits:** Lagging indicators can't predict future well
3. **Overfitting is real:** Complex models memorize noise
4. **Random Forest > XGBoost** (for this problem): Less overfitting, slightly better accuracy

**Path Forward:**
- **Option A:** Improve current approach (longer horizons, better features, LSTM)
- **Option B:** Pivot to longer timeframes (H4, D1) where trends are stronger
- **Option C:** Combine with fundamental/sentiment data
- **Option D:** Focus on volatility/regime prediction instead of direction

**Recommendation:** **Try Option A first** (longer prediction horizons + LSTM), then consider Option B if still unsuccessful.

---

**Last Updated:** November 1, 2025, 18:02:30  
**Status:** Phase A models trained but performance below targets  
**Next:** Improve features, train LSTM, or change prediction target

---

*"In trading, being right 51% of the time can be profitable... if you have proper risk management."*