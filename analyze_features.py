"""
Feature Correlation & Importance Analysis
=========================================
Comprehensive analysis of engineered features:
1. Correlation matrix and heatmap
2. Feature importance ranking (XGBoost)
3. High correlation detection
4. Feature selection recommendations
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def load_processed_data(timeframe="M15"):
    """Load processed feature data for analysis."""

    data_dir = project_root / "data" / "processed"
    file_path = data_dir / f"XAUUSD_{timeframe}_features_complete.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    print(f"📂 Loading: {file_path.name}")
    df = pd.read_csv(file_path)
    print(f"   Rows: {len(df):,} | Columns: {len(df.columns)}")

    return df


def correlation_analysis(df, threshold=0.95):
    """
    Analyze feature correlations.

    Args:
        df: DataFrame with features
        threshold: Correlation threshold for high correlation detection

    Returns:
        Correlation matrix and highly correlated pairs
    """

    print("\n" + "=" * 80)
    print("📊 CORRELATION ANALYSIS")
    print("=" * 80)

    # Select only numeric columns (exclude time, original OHLCV)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Exclude original columns
    exclude_cols = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
        "spread",
        "real_volume",
    ]
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]

    print(f"\n📈 Analyzing {len(feature_cols)} features...")

    # Calculate correlation matrix
    corr_matrix = df[feature_cols].corr()

    # Find highly correlated pairs
    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) >= threshold:
                high_corr_pairs.append(
                    {
                        "feature1": corr_matrix.columns[i],
                        "feature2": corr_matrix.columns[j],
                        "correlation": corr_matrix.iloc[i, j],
                    }
                )

    # Sort by absolute correlation
    high_corr_pairs = sorted(
        high_corr_pairs, key=lambda x: abs(x["correlation"]), reverse=True
    )

    print(
        f"\n⚠️  Found {len(high_corr_pairs)} highly correlated pairs (|r| >= {threshold})"
    )

    if high_corr_pairs:
        print("\nTop 20 highly correlated pairs:")
        print("-" * 80)
        for i, pair in enumerate(high_corr_pairs[:20], 1):
            print(
                f"{i:2d}. {pair['feature1']:30s} <-> {pair['feature2']:30s} | r = {pair['correlation']:6.3f}"
            )

    return corr_matrix, high_corr_pairs


def plot_correlation_heatmap(corr_matrix, output_dir, top_n=50):
    """
    Plot correlation heatmap for top N features.

    Args:
        corr_matrix: Correlation matrix
        output_dir: Output directory
        top_n: Number of top features to plot
    """

    print(f"\n📊 Generating correlation heatmap (top {top_n} features)...")

    # Select top N features by average absolute correlation
    avg_corr = corr_matrix.abs().mean().sort_values(ascending=False)
    top_features = avg_corr.head(top_n).index.tolist()

    # Create heatmap
    plt.figure(figsize=(20, 16))
    sns.heatmap(
        corr_matrix.loc[top_features, top_features],
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        vmin=-1,
        vmax=1,
        fmt=".2f",
    )

    plt.title(
        f"Feature Correlation Heatmap (Top {top_n} Features)",
        fontsize=16,
        fontweight="bold",
    )
    plt.xlabel("Features", fontsize=12)
    plt.ylabel("Features", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()

    output_path = output_dir / "correlation_heatmap_top50.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved: {output_path.name}")


def feature_importance_xgboost(df, target_type="classification", n_periods=1):
    """
    Calculate feature importance using XGBoost.

    Args:
        df: DataFrame with features
        target_type: 'classification' or 'regression'
        n_periods: Number of periods ahead to predict

    Returns:
        Feature importance DataFrame
    """

    print("\n" + "=" * 80)
    print("🤖 FEATURE IMPORTANCE ANALYSIS (XGBoost)")
    print("=" * 80)

    try:
        import xgboost as xgb
        from sklearn.model_selection import train_test_split
    except ImportError:
        print("❌ XGBoost not installed. Skipping importance analysis.")
        return None

    # Prepare features
    exclude_cols = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "tick_volume",
        "spread",
        "real_volume",
    ]
    feature_cols = [
        col
        for col in df.columns
        if col not in exclude_cols and df[col].dtype in [np.float64, np.int64]
    ]

    # Remove constant features
    constant_features = [col for col in feature_cols if df[col].nunique() <= 1]
    if constant_features:
        print(f"\n⚠️  Removing {len(constant_features)} constant features...")
        feature_cols = [col for col in feature_cols if col not in constant_features]

    print(f"\n📈 Using {len(feature_cols)} features for importance analysis...")

    # Create target variable
    if target_type == "classification":
        # Binary: price goes up (1) or down (0) in next n periods
        df["target"] = (df["close"].shift(-n_periods) > df["close"]).astype(int)
        print(
            f"🎯 Target: Price direction (up=1, down=0) in next {n_periods} period(s)"
        )
    else:
        # Regression: actual return in next n periods
        df["target"] = (df["close"].shift(-n_periods) - df["close"]) / df["close"] * 100
        print(f"🎯 Target: Price return (%) in next {n_periods} period(s)")

    # Remove NaN target rows
    df_clean = df.dropna(subset=["target"])

    X = df_clean[feature_cols].fillna(0)
    y = df_clean["target"]

    print(f"   Samples: {len(X):,}")
    print(f"   Features: {len(feature_cols)}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=False,  # Time-series: no shuffle
    )

    print(f"   Train: {len(X_train):,} | Test: {len(X_test):,}")

    # Train XGBoost model
    print("\n🔧 Training XGBoost model...")

    if target_type == "classification":
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        )
    else:
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        )

    model.fit(X_train, y_train)

    # Get feature importance
    importance = model.feature_importances_

    # Create DataFrame
    importance_df = pd.DataFrame(
        {"feature": feature_cols, "importance": importance}
    ).sort_values("importance", ascending=False)

    # Calculate cumulative importance
    importance_df["cumulative_importance"] = importance_df["importance"].cumsum()
    importance_df["cumulative_pct"] = (
        importance_df["cumulative_importance"] / importance_df["importance"].sum() * 100
    )

    # Score
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    print(f"\n✅ Model trained!")
    print(f"   Train Score: {train_score:.4f}")
    print(f"   Test Score: {test_score:.4f}")

    # Display top 30 features
    print(f"\n📊 Top 30 Most Important Features:")
    print("-" * 80)
    print(f"{'Rank':<6} {'Feature':<35} {'Importance':>12} {'Cumulative %':>14}")
    print("-" * 80)

    for i, row in importance_df.head(30).iterrows():
        print(
            f"{row.name + 1:<6} {row['feature']:<35} {row['importance']:>12.6f} {row['cumulative_pct']:>13.2f}%"
        )

    return importance_df


def plot_feature_importance(importance_df, output_dir, top_n=30):
    """Plot top N important features."""

    print(f"\n📊 Generating feature importance plot (top {top_n})...")

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # 1. Bar plot
    top_features = importance_df.head(top_n)

    axes[0].barh(
        range(len(top_features)), top_features["importance"], color="steelblue"
    )
    axes[0].set_yticks(range(len(top_features)))
    axes[0].set_yticklabels(top_features["feature"], fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Importance", fontsize=12, fontweight="bold")
    axes[0].set_title(
        f"Top {top_n} Most Important Features", fontsize=14, fontweight="bold"
    )
    axes[0].grid(axis="x", alpha=0.3)

    # 2. Cumulative importance
    axes[1].plot(
        range(1, len(importance_df) + 1),
        importance_df["cumulative_pct"],
        linewidth=2,
        color="darkblue",
    )
    axes[1].axhline(
        y=80, color="red", linestyle="--", linewidth=1, label="80% threshold"
    )
    axes[1].axhline(
        y=95, color="orange", linestyle="--", linewidth=1, label="95% threshold"
    )
    axes[1].set_xlabel("Number of Features", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Cumulative Importance (%)", fontsize=12, fontweight="bold")
    axes[1].set_title("Cumulative Feature Importance", fontsize=14, fontweight="bold")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    # Find features needed for 80% and 95%
    n_80 = (importance_df["cumulative_pct"] <= 80).sum()
    n_95 = (importance_df["cumulative_pct"] <= 95).sum()
    axes[1].axvline(x=n_80, color="red", linestyle=":", alpha=0.5)
    axes[1].axvline(x=n_95, color="orange", linestyle=":", alpha=0.5)
    axes[1].text(n_80, 85, f"{n_80} features", fontsize=10, color="red")
    axes[1].text(n_95, 97, f"{n_95} features", fontsize=10, color="orange")

    plt.tight_layout()

    output_path = output_dir / "feature_importance_xgboost.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"✅ Saved: {output_path.name}")
    print(f"\n💡 Insight:")
    print(f"   • {n_80} features explain 80% of importance")
    print(f"   • {n_95} features explain 95% of importance")


def generate_feature_selection_report(
    corr_matrix, high_corr_pairs, importance_df, output_dir
):
    """Generate comprehensive feature selection report."""

    print("\n" + "=" * 80)
    print("📝 GENERATING FEATURE SELECTION REPORT")
    print("=" * 80)

    report_path = output_dir / "feature_selection_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("FEATURE SELECTION & ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 1. Summary
        f.write("📊 SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total features analyzed: {len(corr_matrix.columns)}\n")
        f.write(f"Highly correlated pairs (|r| >= 0.95): {len(high_corr_pairs)}\n")

        if importance_df is not None:
            n_80 = (importance_df["cumulative_pct"] <= 80).sum()
            n_95 = (importance_df["cumulative_pct"] <= 95).sum()
            f.write(f"Features for 80% importance: {n_80}\n")
            f.write(f"Features for 95% importance: {n_95}\n")

        f.write("\n")

        # 2. High correlations
        f.write("⚠️  HIGHLY CORRELATED FEATURE PAIRS (|r| >= 0.95)\n")
        f.write("-" * 80 + "\n")
        if high_corr_pairs:
            for i, pair in enumerate(high_corr_pairs, 1):
                f.write(
                    f"{i:3d}. {pair['feature1']:35s} <-> {pair['feature2']:35s} | r = {pair['correlation']:7.4f}\n"
                )
        else:
            f.write("No highly correlated pairs found.\n")

        f.write("\n")

        # 3. Feature importance
        if importance_df is not None:
            f.write("🏆 TOP 50 MOST IMPORTANT FEATURES\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Rank':<6} {'Feature':<40} {'Importance':>12} {'Cum %':>10}\n")
            f.write("-" * 80 + "\n")

            for idx, row in importance_df.head(50).iterrows():
                f.write(
                    f"{idx + 1:<6} {row['feature']:<40} {row['importance']:>12.6f} {row['cumulative_pct']:>9.2f}%\n"
                )

            f.write("\n")

            # 4. Recommendations
            f.write("💡 FEATURE SELECTION RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")

            # Features to consider removing (low importance + high correlation)
            low_importance = importance_df[importance_df["importance"] < 0.001][
                "feature"
            ].tolist()

            # Features in high correlation pairs
            high_corr_features = set()
            for pair in high_corr_pairs:
                high_corr_features.add(pair["feature1"])
                high_corr_features.add(pair["feature2"])

            # Intersection
            remove_candidates = [f for f in low_importance if f in high_corr_features]

            f.write(f"\n1. CONSIDER REMOVING ({len(remove_candidates)} features):\n")
            f.write("   (Low importance + highly correlated)\n\n")
            for feat in remove_candidates[:30]:
                f.write(f"   • {feat}\n")

            f.write(f"\n2. KEEP FOR SURE (Top 30 by importance):\n\n")
            for feat in importance_df.head(30)["feature"]:
                f.write(f"   ✓ {feat}\n")

            f.write(f"\n3. STRATEGY:\n")
            f.write(f"   • Start with top {n_80} features (80% importance)\n")
            f.write(f"   • Remove one feature from each high-correlation pair\n")
            f.write(f"   • Test model performance with reduced feature set\n")
            f.write(f"   • Iterate and fine-tune\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")

    print(f"✅ Report saved: {report_path.name}")

    return str(report_path)


def main():
    """Main analysis pipeline."""

    print("=" * 80)
    print("🔬 FEATURE CORRELATION & IMPORTANCE ANALYSIS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create output directory
    output_dir = project_root / "results" / "feature_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data (using M15 as representative timeframe)
    timeframe = "M15"
    df = load_processed_data(timeframe)

    # 1. Correlation Analysis
    corr_matrix, high_corr_pairs = correlation_analysis(df, threshold=0.95)

    # 2. Plot correlation heatmap
    plot_correlation_heatmap(corr_matrix, output_dir, top_n=50)

    # 3. Feature Importance
    importance_df = feature_importance_xgboost(
        df, target_type="classification", n_periods=1
    )

    if importance_df is not None:
        # 4. Plot importance
        plot_feature_importance(importance_df, output_dir, top_n=30)

        # 5. Save importance to CSV
        importance_path = output_dir / "feature_importance_ranking.csv"
        importance_df.to_csv(importance_path, index=False)
        print(f"\n✅ Importance rankings saved: {importance_path.name}")

    # 6. Generate comprehensive report
    report_path = generate_feature_selection_report(
        corr_matrix, high_corr_pairs, importance_df, output_dir
    )

    # Summary
    print("\n" + "=" * 80)
    print("✨ ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nOutput files in: results/feature_analysis/")
    print(f"  • correlation_heatmap_top50.png")
    print(f"  • feature_importance_xgboost.png")
    print(f"  • feature_importance_ranking.csv")
    print(f"  • feature_selection_report.txt")
    print("\n📊 Next steps:")
    print("  1. Review feature_selection_report.txt")
    print("  2. Identify features to remove (low importance + high correlation)")
    print("  3. Create reduced feature set")
    print("  4. Proceed to model training!")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
