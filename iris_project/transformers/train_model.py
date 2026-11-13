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

from typing import Dict, Any
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


@transformer
def train(df: pd.DataFrame, *args, **kwargs) -> Dict[str, Any]:
    """
    Trains a DecisionTreeClassifier reading max_depth from runtime variables.
    """
    # Read max_depth from runtime variables or kwargs
    max_depth = kwargs.get('max_depth')
    if max_depth is None and 'runtime_vars' in kwargs and isinstance(kwargs['runtime_vars'], dict):
        max_depth = kwargs['runtime_vars'].get('max_depth')
    if max_depth is None:
        max_depth = 3
    max_depth = int(max_depth)

    feature_cols = [c for c in df.columns if c not in ['target', 'split']]
    
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    X_train = train_df[feature_cols]
    y_train = train_df['target']
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))

    print(f"[train_model] max_depth={max_depth} | Test Accuracy={acc:.4f}")

    predictions_df = X_test.copy()
    predictions_df['actual'] = y_test.values
    predictions_df['predicted'] = y_pred

    return {
        'model': clf,
        'model_name': 'DecisionTreeClassifier',
        'max_depth': max_depth,
        'accuracy': acc,
        'X_test': X_test,
        'y_test': y_test,
        'y_pred': y_pred,
        'predictions_df': predictions_df,
    }


@test
def test_accuracy(output, *args) -> None:
    """
    Quality gate: asserts accuracy meets the minimum 90% threshold.
    When max_depth=1 (accuracy ~67%), this test fails, blocking save_results.
    """
    assert output is not None, 'The output is undefined'
    acc = output.get('accuracy', 0.0)
    threshold = 0.90
    assert acc >= threshold, (
        f"Test accuracy {acc:.4f} is below required threshold {threshold}. "
        f"Blocking downstream export."
    )
