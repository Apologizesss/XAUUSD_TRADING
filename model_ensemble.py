"""
Model Ensemble System
---------------------
รวมหลายโมเดลเพื่อเพิ่มความแม่นยำ

Supported Models:
- XGBoost
- Random Forest (ถ้ามี)
- LightGBM (ถ้ามี)

Ensemble Methods:
- Voting (Majority Vote)
- Weighted Average
- Stacking

วิธีใช้:
    python model_ensemble.py --data-path data/price_with_sentiment.csv
"""

import argparse
import pickle
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

try:
    import lightgbm as lgb

    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️ LightGBM not available. Using XGBoost and RandomForest only.")


class ModelEnsemble:
    """
    Ensemble หลายโมเดล
    """

    def __init__(self, ensemble_method="voting"):
        """
        Initialize Ensemble

        Args:
            ensemble_method: 'voting', 'weighted', or 'stacking'
        """
        self.ensemble_method = ensemble_method
        self.models = {}
        self.ensemble = None
        self.scaler = StandardScaler()
        self.feature_names = None

    def create_models(self):
        """สร้างโมเดลทั้งหมด"""
        print("\n🤖 Creating individual models...")

        # 1. XGBoost
        print("  1. XGBoost...")
        self.models["xgboost"] = xgb.XGBClassifier(
            max_depth=5,
            learning_rate=0.05,
            n_estimators=200,
            objective="binary:logistic",
            eval_metric="logloss",
            use_label_encoder=False,
            random_state=42,
        )

        # 2. Random Forest
        print("  2. Random Forest...")
        self.models["random_forest"] = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        # 3. LightGBM (ถ้ามี)
        if LIGHTGBM_AVAILABLE:
            print("  3. LightGBM...")
            self.models["lightgbm"] = lgb.LGBMClassifier(
                num_leaves=31, learning_rate=0.05, n_estimators=200, random_state=42
            )

        print(f"\n✅ Created {len(self.models)} models")

        return self.models

    def train_individual_models(self, X_train, y_train, X_val, y_val):
        """เทรนโมเดลแต่ละตัว"""
        print("\n" + "=" * 70)
        print("TRAINING INDIVIDUAL MODELS")
        print("=" * 70)

        results = {}

        for name, model in self.models.items():
            print(f"\n🔧 Training {name.upper()}...")

            try:
                # Train
                model.fit(X_train, y_train)

                # Evaluate
                y_pred = model.predict(X_val)
                y_proba = (
                    model.predict_proba(X_val)[:, 1]
                    if hasattr(model, "predict_proba")
                    else y_pred
                )

                accuracy = accuracy_score(y_val, y_pred)
                precision = precision_score(y_val, y_pred)
                recall = recall_score(y_val, y_pred)
                f1 = f1_score(y_val, y_pred)
                auc = roc_auc_score(y_val, y_proba)

                results[name] = {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "auc": auc,
                }

                print(f"  Accuracy:  {accuracy:.4f}")
                print(f"  Precision: {precision:.4f}")
                print(f"  Recall:    {recall:.4f}")
                print(f"  F1-Score:  {f1:.4f}")
                print(f"  AUC-ROC:   {auc:.4f}")

            except Exception as e:
                print(f"  ❌ Error training {name}: {e}")
                continue

        return results

    def create_voting_ensemble(self):
        """สร้าง Voting Ensemble"""
        print("\n🗳️ Creating Voting Ensemble...")

        estimators = [(name, model) for name, model in self.models.items()]

        self.ensemble = VotingClassifier(
            estimators=estimators,
            voting="soft",  # soft voting (use probabilities)
            n_jobs=-1,
        )

        print(f"✅ Voting Ensemble created with {len(estimators)} models")

        return self.ensemble

    def create_weighted_ensemble(self, weights=None):
        """สร้าง Weighted Ensemble"""
        print("\n⚖️ Creating Weighted Ensemble...")

        if weights is None:
            # Default: เท่ากันทุกโมเดล
            weights = [1.0 / len(self.models)] * len(self.models)

        estimators = [(name, model) for name, model in self.models.items()]

        self.ensemble = VotingClassifier(
            estimators=estimators, voting="soft", weights=weights, n_jobs=-1
        )

        print(f"✅ Weighted Ensemble created")
        print(f"   Weights: {dict(zip(self.models.keys(), weights))}")

        return self.ensemble

    def train_ensemble(self, X_train, y_train):
        """เทรน Ensemble"""
        print("\n" + "=" * 70)
        print(f"TRAINING ENSEMBLE ({self.ensemble_method.upper()})")
        print("=" * 70)

        if self.ensemble_method == "voting":
            self.create_voting_ensemble()
        elif self.ensemble_method == "weighted":
            # น้ำหนักอิงจาก F1-score ของแต่ละโมเดล
            # (คำนวณจาก validation set)
            self.create_weighted_ensemble()

        print("\n🔧 Training ensemble...")
        self.ensemble.fit(X_train, y_train)
        print("✅ Ensemble training complete")

        return self.ensemble

    def evaluate_ensemble(self, X_test, y_test):
        """ประเมิน Ensemble"""
        print("\n" + "=" * 70)
        print("ENSEMBLE EVALUATION")
        print("=" * 70)

        # Predictions
        y_pred = self.ensemble.predict(X_test)
        y_proba = self.ensemble.predict_proba(X_test)[:, 1]

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        print(f"\n📊 Ensemble Performance:")
        print(f"  Test Accuracy:  {accuracy:.4f} ({accuracy * 100:.2f}%)")
        print(f"  Test Precision: {precision:.4f}")
        print(f"  Test Recall:    {recall:.4f}")
        print(f"  Test F1-Score:  {f1:.4f}")
        print(f"  Test AUC-ROC:   {auc:.4f}")

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n📈 Confusion Matrix:")
        print(f"  TN: {cm[0, 0]:4d}  FP: {cm[0, 1]:4d}")
        print(f"  FN: {cm[1, 0]:4d}  TP: {cm[1, 1]:4d}")

        # Classification Report
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=["DOWN", "UP"]))

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "auc": auc,
        }

    def save_ensemble(self, output_dir="results/ensemble"):
        """บันทึก Ensemble"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save ensemble
        ensemble_file = output_path / "ensemble_model.pkl"
        joblib.dump(self.ensemble, ensemble_file)
        print(f"\n💾 Ensemble saved: {ensemble_file}")

        # Save scaler
        scaler_file = output_path / "ensemble_scaler.pkl"
        joblib.dump(self.scaler, scaler_file)
        print(f"💾 Scaler saved: {scaler_file}")

        # Save feature names
        if self.feature_names is not None:
            features_file = output_path / "feature_names.txt"
            with open(features_file, "w") as f:
                f.write("\n".join(self.feature_names))
            print(f"💾 Feature names saved: {features_file}")

    def load_ensemble(self, input_dir="results/ensemble"):
        """โหลด Ensemble"""
        input_path = Path(input_dir)

        # Load ensemble
        ensemble_file = input_path / "ensemble_model.pkl"
        self.ensemble = joblib.load(ensemble_file)
        print(f"✅ Ensemble loaded: {ensemble_file}")

        # Load scaler
        scaler_file = input_path / "ensemble_scaler.pkl"
        self.scaler = joblib.load(scaler_file)
        print(f"✅ Scaler loaded: {scaler_file}")

        return self.ensemble


def main():
    """ฟังก์ชันหลัก"""
    parser = argparse.ArgumentParser(description="Train Ensemble Model")
    parser.add_argument(
        "--data-path", "-d", required=True, help="Path to processed data CSV"
    )
    parser.add_argument(
        "--test-size", type=float, default=0.2, help="Test set size (default: 0.2)"
    )
    parser.add_argument(
        "--method",
        choices=["voting", "weighted"],
        default="voting",
        help="Ensemble method",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("MODEL ENSEMBLE TRAINER")
    print("=" * 70)
    print(f"\nData: {args.data_path}")
    print(f"Test size: {args.test_size * 100}%")
    print(f"Method: {args.method}")

    # Load data
    print("\n" + "=" * 70)
    print("LOADING DATA")
    print("=" * 70)

    df = pd.read_csv(args.data_path)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    # Prepare features
    exclude_cols = [
        "target",
        "future_price",
        "time",
        "timestamp",
        "symbol",
        "timeframe",
    ]
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    print(f"  Found {len(feature_cols)} features")

    # Handle missing values
    if df[feature_cols].isnull().any().any():
        print("  Warning: Found NaN, filling with 0")
        df[feature_cols] = df[feature_cols].fillna(0)

    # Check target distribution
    target_dist = df["target"].value_counts()
    print(f"  Target distribution:")
    for label, count in target_dist.items():
        label_name = "UP" if label == 1 else "DOWN"
        percentage = (count / len(df)) * 100
        print(f"    {label_name}: {count}/{len(df)} ({percentage:.1f}%)")

    # Split data
    print("\n" + "=" * 70)
    print("SPLITTING DATA")
    print("=" * 70)

    X = df[feature_cols].values
    y = df["target"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )

    print(
        f"  Train: {len(X_train)} samples ({(y_train == 1).sum() / len(y_train) * 100:.1f}% UP)"
    )
    print(
        f"  Test:  {len(X_test)} samples ({(y_test == 1).sum() / len(y_test) * 100:.1f}% UP)"
    )

    # Scale features
    print("\n" + "=" * 70)
    print("SCALING FEATURES")
    print("=" * 70)

    ensemble = ModelEnsemble(ensemble_method=args.method)
    ensemble.feature_names = feature_cols

    X_train_scaled = ensemble.scaler.fit_transform(X_train)
    X_test_scaled = ensemble.scaler.transform(X_test)

    # Create and train individual models
    ensemble.create_models()

    # Split train into train+val for individual model evaluation
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train_scaled, y_train, test_size=0.2, random_state=42, stratify=y_train
    )

    individual_results = ensemble.train_individual_models(X_tr, y_tr, X_val, y_val)

    # Train ensemble
    ensemble.train_ensemble(X_train_scaled, y_train)

    # Evaluate ensemble
    ensemble_results = ensemble.evaluate_ensemble(X_test_scaled, y_test)

    # Compare with individual models
    print("\n" + "=" * 70)
    print("COMPARISON: ENSEMBLE vs INDIVIDUAL MODELS")
    print("=" * 70)

    print(f"\n{'Model':<20} {'Accuracy':<12} {'F1-Score':<12} {'AUC-ROC':<12}")
    print("-" * 70)

    for name, results in individual_results.items():
        print(
            f"{name.upper():<20} {results['accuracy']:<12.4f} {results['f1']:<12.4f} {results['auc']:<12.4f}"
        )

    print("-" * 70)
    print(
        f"{'ENSEMBLE':<20} {ensemble_results['accuracy']:<12.4f} {ensemble_results['f1']:<12.4f} {ensemble_results['auc']:<12.4f}"
    )
    print("=" * 70)

    # Save
    ensemble.save_ensemble()

    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"\nFinal Ensemble Accuracy: {ensemble_results['accuracy'] * 100:.2f}%")
    print(f"F1-Score: {ensemble_results['f1']:.4f}")
    print(f"AUC-ROC: {ensemble_results['auc']:.4f}")


if __name__ == "__main__":
    main()
