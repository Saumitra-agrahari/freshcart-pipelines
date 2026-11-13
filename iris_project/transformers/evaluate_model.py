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
from sklearn.metrics import confusion_matrix, classification_report


@transformer
def evaluate(data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
    """
    Evaluates the trained model, generating a confusion matrix and metrics table.
    """
    y_test = data.get('y_test')
    y_pred = data.get('y_pred')
    model_name = data.get('model_name', 'DecisionTreeClassifier')
    max_depth = data.get('max_depth', 'N/A')

    if y_test is None or y_pred is None:
        raise ValueError("Missing 'y_test' or 'y_pred' in upstream data.")

    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(
        cm,
        index=[f"Actual Class {i}" for i in range(len(cm))],
        columns=[f"Pred Class {i}" for i in range(len(cm))]
    )

    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report_dict).transpose()

    print(f"\n================ Model Evaluation: {model_name} (max_depth={max_depth}) ================")
    print("\n--- Confusion Matrix ---")
    print(cm_df)
    print("\n--- Classification Metrics Table ---")
    print(report_df)
    print("========================================================================================\n")

    return {
        'confusion_matrix': cm.tolist(),
        'confusion_matrix_df': cm_df,
        'metrics_report': report_dict,
        'metrics_df': report_df
    }


@test
def test_evaluation_metrics(output, *args) -> None:
    """
    Validates evaluation output structure and metrics generation.
    """
    assert output is not None, 'The output is undefined'
    assert 'confusion_matrix' in output, 'Missing confusion_matrix in output'
    assert 'metrics_report' in output, 'Missing metrics_report in output'
    cm = output['confusion_matrix']
    assert len(cm) == 3, f'Expected 3 classes in confusion matrix, got {len(cm)}'
