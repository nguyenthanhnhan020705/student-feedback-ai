r"""Train three baseline algorithms, explain Validation Macro-F1, and plot it.

Run: .\.venv\Scripts\python.exe demo_validation_chart.py
Use --no-show to save the chart without opening a graphical window.
Only writes a fresh directory under outputs/; never modifies serving models.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
# Allow running this file directly from any working directory.
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    import matplotlib
    if args.no_show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from feedback_ai.data.loader import load_dataset
    from feedback_ai.evaluation.topic import verify_dataset_manifest
    from feedback_ai.evaluation import sentiment as sentiment_metrics, topic as topic_metrics
    from feedback_ai.training import sentiment, topic

    algorithms = ("nb", "logistic_regression", "linear_svm")
    names = ("Naïve Bayes", "Logistic Regression", "Linear SVM")
    output = ROOT / "outputs" / ("validation-demo-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    print("1. Verify dataset bytes against data/manifest.json", flush=True)
    manifest_hash = verify_dataset_manifest(ROOT / "data/raw", ROOT / "data/manifest.json")
    frames = load_dataset(ROOT / "data/raw")
    train, validation = frames["train"], frames["validation"]
    print(f"Train: {len(train)} | Validation: {len(validation)}")
    print("TF-IDF and classifiers fit TRAIN only; all scores below use VALIDATION.")
    print("Macro-F1 = mean of per-class F1; zero divisions use 0.")
    output.mkdir(parents=True, exist_ok=False)
    scores, summary = {}, []

    for task, trainer, evaluator in (
        ("sentiment", sentiment, sentiment_metrics),
        ("topic", topic, topic_metrics),
    ):
        print(f"\n2. Train 3 algorithms: {task}", flush=True)
        models = trainer.train_models(train)
        metrics = evaluator.evaluate_models(models, validation)
        selection = trainer.select_model(models, validation)
        predictions = {
            algorithm: [str(value) for value in models[algorithm].predict(validation.text.tolist())]
            for algorithm in algorithms
        }
        evidence = [
            {"id": row.id, "text": row.text, "true_label": getattr(row, task),
             **{algorithm: predictions[algorithm][i] for algorithm in algorithms}}
            for i, row in enumerate(validation.itertuples())
        ]
        payload = {
            "task": task, "dataset_manifest_sha256": manifest_hash,
            "train_rows": len(train), "validation_rows": len(validation),
            "validation": metrics, "selection": selection,
            "prediction_rows": evidence,
        }
        (output / f"{task}_validation.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        scores[task] = []
        for algorithm, name in zip(algorithms, names):
            result = metrics[algorithm]
            print(f"\n{task} / {name}")
            print(f"{'Class':<15} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>8}")
            for row in result["per_class"]:
                print(f"{row['label']:<15} {row['precision']:>10.6f} {row['recall']:>10.6f} "
                      f"{row['f1']:>10.6f} {row['support']:>8}")
            f1s = [row["f1"] for row in result["per_class"]]
            if not math.isclose(sum(f1s) / len(f1s), result["macro_f1"], abs_tol=1e-12):
                raise ValueError("Macro-F1 does not match per-class mean")
            expression = " + ".join(f"{value:.6f}" for value in f1s)
            print(f"Macro-F1 = ({expression}) / {len(f1s)} = {result['macro_f1']:.6f} "
                  f"= {result['macro_f1'] * 100:.2f}%")
            print("Confusion matrix (rows=true, columns=predicted):", result["label_order"])
            for row in result["confusion_matrix"]:
                print(" ", row)
            scores[task].append(result["macro_f1"] * 100)
            summary.append({"task": task, "algorithm": algorithm,
                            "validation_macro_f1": result["macro_f1"],
                            "validation_accuracy": result["accuracy"]})
        print(f"Selected by Validation: {selection['algorithm']}", flush=True)

    with (output / "summary.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(12, 6))
    for offset, task, label in (
        (-0.18, "sentiment", "Sentiment (cảm xúc)"),
        (0.18, "topic", "Topic (chủ đề)"),
    ):
        bars = ax.bar(x + offset, scores[task], 0.36, label=label)
        ax.bar_label(bars, fmt="%.2f%%", padding=4)
    ax.set_xticks(x, names)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Macro-F1 trên Validation (%)")
    ax.set_title("So sánh 3 thuật toán trên UIT-VSFC (Baseline)", pad=15)
    ax.legend()
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.15)
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(output / "validation_macro_f1.png", dpi=200, bbox_inches="tight")
    print(f"\n3. Evidence JSON, summary CSV and chart saved to: {output}", flush=True)
    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
