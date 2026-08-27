import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold


def _make_multi_record_dataset(n_patients=50, max_records_per_patient=4, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for patient_id in range(1, n_patients + 1):
        n_records = rng.integers(1, max_records_per_patient + 1)
        for _ in range(n_records):
            rows.append({
                "patient_id": patient_id,
                "feature_a": rng.normal(),
                "target": rng.integers(0, 2),
            })
    return pd.DataFrame(rows)


class TestGroupKFoldLeakageControl:

    def test_groupkfold_has_zero_patient_overlap(self):
        df = _make_multi_record_dataset()
        assert df["patient_id"].duplicated().any(), \
            "Test setup error: this dataset must contain patients with multiple records"

        X = df[["feature_a"]]
        y = df["target"]
        groups = df["patient_id"]

        gkf = GroupKFold(n_splits=5)
        for train_idx, test_idx in gkf.split(X, y, groups):
            train_patients = set(groups.iloc[train_idx])
            test_patients = set(groups.iloc[test_idx])
            assert train_patients.isdisjoint(test_patients), \
                "GroupKFold must never split a single patient's records across train/test"

    def test_plain_kfold_WOULD_leak_on_this_data(self):
        """Negative control: proves plain KFold leaks on multi-record
        data, confirming the test above is meaningful, not trivial."""
        df = _make_multi_record_dataset()
        X = df[["feature_a"]]
        y = df["target"]
        groups = df["patient_id"]

        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        leaked = False
        for train_idx, test_idx in kf.split(X, y):
            train_patients = set(groups.iloc[train_idx])
            test_patients = set(groups.iloc[test_idx])
            if not train_patients.isdisjoint(test_patients):
                leaked = True
                break
        assert leaked, (
            "Expected plain KFold to leak on multi-record data - if this "
            "fails, the synthetic dataset isn't exercising the scenario "
            "GroupKFold is meant to prevent."
        )
