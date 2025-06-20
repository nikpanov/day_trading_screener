import os
import pandas as pd
from openpyxl.styles import PatternFill, Font
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger()

def export_to_excel(results, run_timestamp):
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(results, columns=[
        "symbol", "signal_date", "buy_price", "sell_price", "sell_date", "gain_pct", "holding_days", "result"
    ])
    
    filename = f"output/backtest_results_{run_timestamp.strftime('%Y-%m-%d_%H%M')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Backtest Results"

    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        ws.append(row)

        if r_idx == 1:
            continue  # Skip header row

        result = row[-1]  # Last column is 'result'
        if result == 'win':
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Light green
        elif result == 'loss':
            fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Light red
        else:
            fill = None

        if fill:
            for cell in ws[r_idx]:
                cell.fill = fill

    wb.save(filename)
    print(f"📤 Exported backtest results to Excel: {filename}")
    logger.info(f"Exported backtest results to Excel: {filename}")