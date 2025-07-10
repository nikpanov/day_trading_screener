import pandas as pd
import os
from utils.exporter import export_screener_results_to_excel
import pytest
from datetime import datetime

@pytest.fixture
def sample_results_df():
    return pd.DataFrame({
        "ticker": ["AAPL", "MSFT"],
        "bullish": [True, False],
        "score": [85, 60]
    })

def test_export_excel_structure(sample_results_df):
    now = datetime(2025, 7, 7, 12, 0)
    export_screener_results_to_excel(sample_results_df, now)
    expected_filename = f"output/screener_results/screener_results_{now.strftime('%Y-%m-%d_%H%M')}.xlsx"
    assert os.path.exists(expected_filename)