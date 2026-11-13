if 'data_loader' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_loader
    except ImportError:
        def data_loader(fn):
            return fn

if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(fn):
            return fn

import pandas as pd
from sklearn.datasets import load_iris


@data_loader
def load_data(*args, **kwargs) -> pd.DataFrame:
    """
    Loads the Iris dataset from scikit-learn as a pandas DataFrame.
    """
    iris = load_iris(as_frame=True)
    df = iris.frame.copy()
    return df


@test
def test_output(output, *args) -> None:
    """
    Validates that the iris dataset loaded successfully with expected shape.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, pd.DataFrame), 'Output must be a pandas DataFrame'
    assert len(output) == 150, f'Expected 150 rows, got {len(output)}'
    assert 'target' in output.columns, 'Target column missing from dataset'
