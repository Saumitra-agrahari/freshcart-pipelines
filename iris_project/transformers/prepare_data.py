if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ImportError:
        def transformer(fn):
            return fn

if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(fn):
            return fn

import pandas as pd
from sklearn.model_selection import train_test_split


@transformer
def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
    Splits Iris data into 80% train and 20% test partitions.
    """
    df = df.copy()
    test_size = kwargs.get('test_size', 0.2)
    train_idx, test_idx = train_test_split(
        df.index,
        test_size=test_size,
        random_state=42,
        stratify=df['target'] if 'target' in df.columns else None
    )
    df['split'] = 'train'
    df.loc[test_idx, 'split'] = 'test'
    return df


@test
def test_output(output, *args) -> None:
    """
    Validates that the split column was added with an 80/20 train/test distribution.
    """
    assert output is not None, 'The output is undefined'
    assert 'split' in output.columns, 'Missing split column'
    assert (output['split'] == 'train').sum() == 120, 'Train split must contain 120 rows'
    assert (output['split'] == 'test').sum() == 30, 'Test split must contain 30 rows'
