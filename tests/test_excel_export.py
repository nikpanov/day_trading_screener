import pandas as pd
from output.export import export_screener_results_to_excel
import pytest

@pytest.fixture
def sample_results_df():
    return pd.DataFrame({
        "ticker": ["AAPL", "MSFT"],
        "bullish": [True, False],
        "score": [85, 60]
    })

def test_export_excel_structure(tmp_path, sample_results_df):
    output_path = tmp_path / "results.xlsx"
    export_screener_results_to_excel(sample_results_df, output_path)
    assert output_path.exists()
