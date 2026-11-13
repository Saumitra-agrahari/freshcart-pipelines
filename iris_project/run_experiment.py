"""
Runner script for Part C2: Tests as a Gate experiment.
Runs pipeline iterations for max_depth = 1, 2, 3, 4, 5.
Before each run, removes iris_predictions.csv, trains model, executes @test gate,
and checks if downstream save_results created iris_predictions.csv.
"""
import os
import sys
import pandas as pd

from iris_project.data_loaders.load_iris import load_data
from iris_project.transformers.prepare_data import transform
from iris_project.transformers.train_model import train, test_accuracy
from iris_project.data_exporters.save_results import export_data
from iris_project.transformers.evaluate_model import evaluate
from iris_project.transformers.train_knn import train_knn


def run_experiment():
    print(f"\n{'max_depth':<10} | {'Test accuracy':<15} | {'test_accuracy passed?':<22} | {'iris_predictions.csv created?'}")
    print("-" * 80)

    raw_df = load_data()
    prepared_df = transform(raw_df)

    for depth in range(1, 6):
        # Delete iris_predictions.csv before each run
        if os.path.exists('iris_predictions.csv'):
            os.remove('iris_predictions.csv')

        test_passed = False
        accuracy_str = "N/A"

        try:
            # Train decision tree with specified max_depth
            model_out = train(prepared_df, max_depth=depth)
            acc = model_out.get('accuracy', 0.0)
            accuracy_str = f"{acc:.4f}"

            # Quality gate @test: fails if acc < 0.90
            test_accuracy(model_out)
            test_passed = True

            # Downstream execution (only reached if test passes)
            export_data(model_out)
            evaluate(model_out)
        except AssertionError:
            test_passed = False
        except Exception as e:
            test_passed = False

        csv_created = "YES" if os.path.exists('iris_predictions.csv') else "NO"
        status_str = "PASSED" if test_passed else "FAILED"
        print(f"{depth:<10} | {accuracy_str:<15} | {status_str:<22} | {csv_created}")

    print("-" * 80 + "\n")


if __name__ == '__main__':
    run_experiment()
