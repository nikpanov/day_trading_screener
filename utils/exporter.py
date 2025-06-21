import os
import pandas as pd
from openpyxl.styles import PatternFill, Font
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger()

def export_screener_results_to_excel(rows, run_timestamp):
    os.makedirs("output/screener_results", exist_ok=True)
    df = pd.DataFrame(rows)

    expected_columns = [
        "symbol", "company_name", "price", "rsi14", "ema20", "ema50", "vwap",
        "is_bullish", "failure_reason", "timestamp"
    ]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None
    df = df[expected_columns]

    filename = f"output/screener_results/screener_results_{run_timestamp.strftime('%Y-%m-%d_%H%M')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Screener Results"

    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        ws.append(row)

        if r_idx == 1:
            for cell in ws[r_idx]:
                cell.font = Font(bold=True)
            continue

        is_bullish = df.loc[r_idx - 2, "is_bullish"]
        if is_bullish:
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        else:
            fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        for cell in ws[r_idx]:
            cell.fill = fill

    wb.save(filename)
    print(f"📤 Exported screener results to Excel: {filename}")
    logger.info(f"Exported screener results to Excel: {filename}")

def export_backtest_results_to_excel(results, run_timestamp):
    os.makedirs("output/backtest_results", exist_ok=True)
    df = pd.DataFrame(results, columns=[
        "symbol", "signal_date", "buy_price", "sell_price", "sell_date", "gain_pct", "holding_days", "result"
    ])

    filename = f"output/backtest_results/backtest_results_{run_timestamp.strftime('%Y-%m-%d_%H%M')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Backtest Results"

    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        ws.append(row)

        if r_idx == 1:
            for cell in ws[r_idx]:
                cell.font = Font(bold=True)
            continue

        result = row[-1]  # Last column is 'result'
        if result == 'win':
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        elif result == 'loss':
            fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        else:
            fill = None

        if fill:
            for cell in ws[r_idx]:
                cell.fill = fill

    wb.save(filename)
    print(f"\U0001f4e4 Exported backtest results to Excel: {filename}")
    logger.info(f"Exported backtest results to Excel: {filename}")
