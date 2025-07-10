import os
import pandas as pd
from openpyxl.styles import PatternFill, Font
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
from utils.logger import setup_logger
# from datetime import datetime, timedelta
from emailer.notify import send_email_with_attachment

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

    # Remove tzinfo from all timestamps
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)

    try:
        run_timestamp_naive = run_timestamp.replace(tzinfo=None)
    except Exception:
        run_timestamp_naive = run_timestamp

    filename = f"output/screener_results/screener_results_{run_timestamp_naive.strftime('%Y-%m-%d_%H%M')}.xlsx"

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
        fill = (
            PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # green
            if is_bullish
            else PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # red
        )

        for cell in ws[r_idx]:
            cell.fill = fill

    try:
        wb.save(filename)
        print(f"📤 Exported screener results to Excel: {filename}")
        logger.info(f"Exported screener results to Excel: {filename}")
    except Exception as e:
        logger.error(f"Failed to save Excel file: {e}")
        print(f"Failed to save Excel file: {e}")
        return

    # ✅ Email Summary Section
    try:
        total_scanned = len(df)
        bullish_count = df["is_bullish"].sum()

        failure_summary = df["failure_reason"].value_counts(dropna=True)
        failure_lines = "\n".join(f"  - {reason}: {count}" for reason, count in failure_summary.items())
        failure_text = f"\n⚠️ Failure reasons:\n{failure_lines}" if not failure_summary.empty else ""

        body = (
            f"📊 Screener run completed.\n\n"
            f"✅ Bullish tickers found: {bullish_count}\n"
            f"🔍 Total tickers scanned: {total_scanned}\n"
            f"{failure_text}"
        )

        send_email_with_attachment(
            subject="📈 Screener Results Available",
            body=body,
            attachment_path=filename
        )
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        print(f"Failed to send email notification: {e}")

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

    # Remove tzinfo from all timestamps
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)

    try:
        run_timestamp_naive = run_timestamp.replace(tzinfo=None)
    except Exception:
        run_timestamp_naive = run_timestamp

    filename = f"output/screener_results/screener_results_{run_timestamp_naive.strftime('%Y-%m-%d_%H%M')}.xlsx"

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
        fill = (
            PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # green
            if is_bullish
            else PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # red
        )

        for cell in ws[r_idx]:
            cell.fill = fill

    try:
        wb.save(filename)
        print(f"📤 Exported screener results to Excel: {filename}")
        logger.info(f"Exported screener results to Excel: {filename}")
    except Exception as e:
        logger.error(f"Failed to save Excel file: {e}")
        print(f"Failed to save Excel file: {e}")

def export_backtest_results_to_excel(results, run_timestamp):
    os.makedirs("output/backtest_results", exist_ok=True)

    df = pd.DataFrame(results, columns=[
        "symbol", "signal_date", "buy_price", "sell_price",
        "sell_date", "gain_pct", "holding_days", "result"
    ])

    # Ensure timestamp is naive (Excel can't handle tz-aware datetimes)
    try:
        run_timestamp_naive = run_timestamp.replace(tzinfo=None)
    except Exception:
        run_timestamp_naive = run_timestamp

    filename = f"output/backtest_results/backtest_results_{run_timestamp_naive.strftime('%Y-%m-%d_%H%M')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Backtest Results"

    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        ws.append(row)

        if r_idx == 1:
            for cell in ws[r_idx]:
                cell.font = Font(bold=True)
            continue

        result = df.loc[r_idx - 2, "result"]
        if result == 'win':
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        elif result == 'loss':
            fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        else:
            fill = None

        if fill:
            for cell in ws[r_idx]:
                cell.fill = fill

    try:
        wb.save(filename)
        print(f"📤 Exported backtest results to Excel: {filename}")
        logger.info(f"Exported backtest results to Excel: {filename}")
    except Exception as e:
        logger.error(f"Failed to save backtest Excel file: {e}")
        print(f"Failed to save backtest Excel file: {e}")
