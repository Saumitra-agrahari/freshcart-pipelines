# FreshCart Data Engineering Pipelines ("From Git to Gold")

Comprehensive data engineering repository containing end-to-end implementations of:
1. **Part A:** Git version control, pytest validation, and GitHub Actions CI/CD.
2. **Part B:** FreshCart ELT pipeline on Snowflake (Bronze, Silver, Dim SCD-2, Gold, Quality Gates).
3. **Part C:** Orchestrated ML pipeline with Mage (Iris Classifier, test gates, evaluation and KNN branches).
4. **Part D:** Real-time event streaming with RabbitMQ topic exchanges, dynamic binding, and ACK/NACK handling.
5. **Part E:** System integration architecture, report templates, and reflection.

---

## Repository Structure

```text
freshcart-pipelines/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow (Python 3.12 + Pytest)
├── elt/
│   ├── README.md                # Snowflake ELT instructions and walkthrough
│   └── snowflake_edits.sql      # SQL diffs, 6th quality check, mock orders, and SCD2 events
├── iris_project/
│   ├── data_loaders/load_iris.py
│   ├── transformers/
│   │   ├── prepare_data.py      # 80/20 train/test split (importable by pytest)
│   │   ├── train_model.py       # DecisionTreeClassifier with runtime max_depth & @test gate
│   │   ├── evaluate_model.py    # Confusion matrix and classification metrics branch
│   │   └── train_knn.py         # KNeighborsClassifier parallel branch
│   ├── data_exporters/save_results.py
│   ├── pipelines/iris_classifier/metadata.yaml
│   ├── iris_pipeline.ipynb      # Interactive notebook representation
│   └── run_experiment.py        # Automated runner for C2 max_depth experiment table
├── stream/
│   ├── README.md                # Streaming broker guide and command reference
│   ├── dispatcher.py            # Event generator publishing to 'rapido-dispatch' topic exchange
│   └── driver.py                # Consumer declaring exclusive queues with ACK/NACK validation
├── tests/
│   └── test_prepare_data.py     # Unit test asserting 80/20 train-test split
├── report/
│   ├── report_template.md       # Complete assignment template (sections A1-D3, E)
│   └── integration_diagram.mmd  # Editable Mermaid system integration diagram
├── .env.example                 # Template for required environment variables
├── .gitignore                   # Ignores .env, *.pkl, *.csv, mage.log, __pycache__/
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## Quickstart & Execution Guide

### Prerequisites
- Python 3.12
- Docker (for RabbitMQ local broker) or an active AMQP cloud instance
- Snowflake trial account
- Git and GitHub CLI / web account

Setup local environment:
```bash
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

---

### Part A: Git & CI/CD Workflow

1. **Run Unit Tests Locally:**
   ```bash
   pytest tests/test_prepare_data.py -v
   ```

2. **Push to Remote Repository:**
   ```bash
   git branch -M main
   git remote add origin https://github.com/Saumitra-agrahari/DE-Assignment
   git push -u origin main
   ```

3. **Capture Green & Red CI Screenshots:**
   - **Green CI:** Pushing the valid code triggers GitHub Actions and passes `pytest`.
   - **Red CI:** Temporarily change `test_size=0.3` in `iris_project/transformers/prepare_data.py`.
     ```bash
     git commit -am "test(ci): trigger red CI with test_size=0.3"
     git push
     ```
     Take a screenshot of the failed GitHub Actions job.
   - **Restore Green CI:** Revert `test_size=0.2`.
     ```bash
     git commit -am "fix(ci): restore test_size=0.2 for green CI"
     git push
     ```

---

### Part B: FreshCart ELT on Snowflake

1. Review and apply the SQL changes provided in `elt/snowflake_edits.sql`:
   - **Validation Rule:** Added `IFF(currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL)` into `ARRAY_CONSTRUCT_COMPACT(...)` in `silver.orders_checked`.
   - **Sixth Quality Check:** Verifies `COUNT(*) = 0` for `gold.orders` where `loyalty_points < 0`.
   - **Mock Order Failure:** Run the injection script to trigger quality check failure, observe the alert, and execute the cleanup DELETE.
   - **SCD2 Customer Tier:** Insert Arjun's new Gold tier event effective `2026-08-15` into `ref.mock_crm_tier_events`.
2. Refer to `elt/README.md` for detailed step-by-step SQL worksheet execution.

---

### Part C: Mage ML Pipeline (Iris Classifier)

1. **Run the Full Pipeline via Mage CLI:**
   ```bash
   mage run iris_project iris_classifier --test
   ```

2. **Run Part C2 Experiment Loop (`max_depth = 1..5`):**
   Execute the automated experiment runner to observe how failing accuracy at `max_depth=1` blocks downstream export:
   ```bash
   python iris_project/run_experiment.py
   ```
   Or via shell loop:
   ```bash
   # Bash
   for d in 1 2 3 4 5; do
     rm -f iris_predictions.csv
     echo "=== Testing max_depth = $d ==="
     mage run iris_project iris_classifier --runtime-vars "{\"max_depth\": $d}" --test
     ls -l iris_predictions.csv 2>/dev/null || echo "iris_predictions.csv: NOT CREATED (Test Blocked)"
   done
   ```

3. **Verify Evaluation & KNN Parallel Branches:**
   - Decision Tree branches into `save_results` and `evaluate_model` (confusion matrix and classification report).
   - `prepare_data` branches in parallel into `train_knn` (KNeighborsClassifier with accuracy evaluation).

---

### Part D: Food-Order Stream with RabbitMQ

1. **Start RabbitMQ Broker:**
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

2. **Launch Driver Consumers (Separate Terminals):**
   ```bash
   # Terminal 1: Ravi (Koramangala orders)
   python stream/driver.py Ravi "bangalore.koramangala.*"

   # Terminal 2: Arjun (Bangalore rides)
   python stream/driver.py Arjun "bangalore.*.ride"

   # Terminal 3: Control (All Bangalore events)
   python stream/driver.py Control "bangalore.#"
   ```

3. **Launch Dispatcher:**
   ```bash
   # Terminal 4
   python stream/dispatcher.py
   ```

4. **Observe ACK/NACK Validation:**
   - Every 10th message generated by `dispatcher.py` omits the `"zone"` field.
   - Drivers receiving this message call `basic_nack(requeue=False)` and print `REJECTED`.
   - Valid messages are processed and acknowledged via `basic_ack`.

---

### Part E: Student Report & Integration Architecture

- Report template with empty student response blocks is ready at `report/report_template.md`.
- System architecture diagram is located at `report/integration_diagram.mmd`.
