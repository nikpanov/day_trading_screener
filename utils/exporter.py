import pandas as pd
import os
from utils.logger import setup_logger
logger = setup_logger()

def export_to_excel(rows, run_timestamp):
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(rows)
    filename = f"output/{run_timestamp.strftime('%Y-%m-%d_%H%M')}_screener_results.xlsx"
    df.to_excel(filename, index=False)
    print(f"📤 Exported to Excel: {filename}")
    logger.info(f"Exported to Excel: {filename}")
