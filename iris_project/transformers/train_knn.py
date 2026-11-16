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
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


@transformer
def train_knn(df: pd.DataFrame, *args, **kwargs) -> Dict[str, Any]:
    """
    Parallel branch: Trains a KNeighborsClassifier on the prepared Iris dataset.
    """
    feature_cols = [c for c in df.columns if c not in ['target', 'split']]
    
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    X_train = train_df[feature_cols]
    y_train = train_df['target']
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)

    y_pred = knn.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))

    print(f"\n[train_knn (Parallel Branch)] KNeighborsClassifier(n_neighbors=5) | Test Accuracy = {acc:.4f}\n")

    return {
        'model_name': 'KNeighborsClassifier',
        'n_neighbors': 5,
        'accuracy': acc,
        'y_test': y_test.tolist(),
        'y_pred': y_pred.tolist(),
    }


@test
def test_knn_accuracy(output, *args) -> None:
    """
    Validates that the KNN parallel branch trained successfully with accuracy >= 90%.
    """
    assert output is not None, 'The output is undefined'
    acc = output.get('accuracy', 0.0)
    threshold = 0.90
    assert acc >= threshold, f"KNN accuracy {acc:.4f} fell below threshold {threshold}"
