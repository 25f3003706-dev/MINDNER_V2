"""Train and evaluate an XGBoost classifier on reproducible synthetic data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from xgboost import XGBClassifier


RANDOM_STATE = 42


def build_dataset() -> tuple:
    """Create a balanced, noisy binary classification dataset for experimentation."""
    return make_classification(
        n_samples=1_200,
        n_features=12,
        n_informative=8,
        n_redundant=2,
        n_clusters_per_class=2,
        class_sep=1.1,
        weights=[0.52, 0.48],
        random_state=RANDOM_STATE,
    )


def train_model(X_train, y_train) -> RandomizedSearchCV:
    """Tune an XGBoost classifier using cross-validated ROC AUC."""
    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    parameter_distributions = {
        "n_estimators": [80, 120, 180, 240],
        "max_depth": [2, 3, 4, 5, 6],
        "learning_rate": [0.02, 0.05, 0.1, 0.15, 0.2],
        "subsample": [0.75, 0.85, 1.0],
        "colsample_bytree": [0.75, 0.85, 1.0],
        "min_child_weight": [1, 3, 5],
        "gamma": [0, 0.1, 0.25],
    }
    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=parameter_distributions,
        n_iter=20,
        scoring="roc_auc",
        cv=5,
        random_state=RANDOM_STATE,
        n_jobs=1,
        refit=True,
    )
    search.fit(X_train, y_train)
    return search


def save_report(y_test, predictions, probabilities, output_path: Path) -> tuple[float, float]:
    """Save accuracy, AUC, ROC, and confusion-matrix plots in one image."""
    accuracy = accuracy_score(y_test, predictions)
    auc = roc_auc_score(y_test, probabilities)
    conf_matrix = confusion_matrix(y_test, predictions)
    precision = conf_matrix[1, 1] / sum(conf_matrix[1, :])
    false_positive_rate, true_positive_rate, _ = roc_curve(y_test, probabilities)

    sns.set_theme(style="whitegrid")
    figure, axes = plt.subplots(2, 2, figsize=(12, 9))
    figure.suptitle("Tuned XGBoost Classification Evaluation", fontsize=16)

        # 1. Plot both Accuracy and Precision bars together
    metrics = ["Accuracy", "Precision"]
    scores = [accuracy, precision]
    colors = ["#2a9d8f", "#e76f51"]  # Teal for Accuracy, Coral for Precision
    
    axes[0, 0].bar(metrics, scores, color=colors)
    axes[0, 0].set_ylim(0, 1.1)  # Raised slightly to fit text labels without clipping
    axes[0, 0].set_ylabel("Score")
    axes[0, 0].set_title(f"Accuracy: {accuracy:.3f} | Precision: {precision:.3f}")
    
    # 2. Automatically loop and add text labels on top of each bar
    for i, score in enumerate(scores):
        axes[0, 0].text(i, score + 0.03, f"{score:.3f}", ha="center", va="bottom")


    axes[0, 1].plot(false_positive_rate, true_positive_rate, color="#e76f51", label=f"AUC = {auc:.3f}")
    axes[0, 1].plot([0, 1], [0, 1], "--", color="#666666", label="Chance")
    axes[0, 1].set_xlabel("False positive rate")
    axes[0, 1].set_ylabel("True positive rate")
    axes[0, 1].set_title("ROC curve")
    axes[0, 1].legend(loc="lower right")

    ConfusionMatrixDisplay(conf_matrix, display_labels=["Class 0", "Class 1"]
    ).plot(ax=axes[1, 0], cmap="magma", colorbar=True, values_format="d")
    axes[1, 0].set_title("Confusion matrix")
    axes[1, 1].axis("off")
    axes[1, 1].text( 0.05, 0.85,f"Test accuracy\n{accuracy:.3f}\n\nTest ROC AUC\n{auc:.3f}",
        fontsize=15,
        va="top",
    )
    figure.tight_layout()
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return float(accuracy), float(auc)


def save_metrics(
    output_path: Path,
    search: RandomizedSearchCV,
    accuracy: float,
    auc: float,
    y_test,
    predictions,
) -> None:
    """Persist the run's metrics and tuned configuration as JSON."""
    metrics = {
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_state": RANDOM_STATE,
        "best_cv_roc_auc": float(search.best_score_),
        "test_accuracy": accuracy,
        "test_roc_auc": auc,
        "best_parameters": search.best_params_,
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/xgboost_evaluation.png"),
        help="Path for the combined evaluation plot.",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=Path("artifacts/xgboost_metrics.json"),
        help="Path for the automatically saved metrics JSON file.",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    X, y = build_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    search = train_model(X_train, y_train)
    best_model = cast(XGBClassifier, search.best_estimator_)
    predictions = best_model.predict(X_test)
    probabilities = best_model.predict_proba(X_test)[:, 1]
    accuracy, auc = save_report(y_test, predictions, probabilities, args.output)
    save_metrics(args.metrics_output, search, accuracy, auc, y_test, predictions)

    print(f"Best CV ROC AUC: {search.best_score_:.4f}")
    print(f"Test accuracy: {accuracy:.4f}")
    print(f"Test ROC AUC: {auc:.4f}")
    print(f"Best parameters: {search.best_params_}")
    print(f"Plot saved to: {args.output}")
    print(f"Metrics saved to: {args.metrics_output}")


if __name__ == "__main__":
    main()