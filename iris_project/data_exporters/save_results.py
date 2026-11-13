if 'data_exporter' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_exporter
    except ImportError:
        def data_exporter(fn):
            return fn

if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(fn):
            return fn

import os
from typing import Dict, Any
import pandas as pd


@data_exporter
def export_data(data: Dict[str, Any], *args, **kwargs) -> pd.DataFrame:
    """
    Exports model predictions to iris_predictions.csv.
    """
    predictions_df = data.get('predictions_df')
    if predictions_df is None:
        raise ValueError("Missing 'predictions_df' in upstream data.")

    # Write to iris_predictions.csv
    file_path = 'iris_predictions.csv'
    predictions_df.to_csv(file_path, index=False)
    print(f"[save_results] Predictions exported successfully to {os.path.abspath(file_path)}")
    return predictions_df


@test
def test_export_file_created(output, *args) -> None:
    """
    Validates that iris_predictions.csv was created and has records.
    """
    assert output is not None, 'The output is undefined'
    assert os.path.exists('iris_predictions.csv'), 'iris_predictions.csv was not created'
    df = pd.read_csv('iris_predictions.csv')
    assert len(df) == 30, f'Expected 30 test prediction rows, got {len(df)}'
    assert 'actual' in df.columns and 'predicted' in df.columns, 'Missing prediction columns'
