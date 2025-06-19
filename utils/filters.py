from utils.logger import setup_logger

logger = setup_logger()


def is_bullish(stock_price: float, indicators: dict) -> bool:
    """
    Apply bullish filter:
    - RSI between 50 and 70
    - EMA20 > EMA50
    - price > VWAP
    """
    try:
        rsi = indicators["rsi14"]
        ema20 = indicators["ema20"]
        ema50 = indicators["ema50"]
        vwap = indicators["vwap"]

        if None in (rsi, ema20, ema50, vwap):
            return False

        return (
            50 <= rsi <= 70 and
            ema20 > ema50 and
            stock_price > vwap
        )
    except Exception as e:
        print(f"⚠️ Error applying bullish filter: {e}")
        logger.error(f"Error applying bullish filter: {e}")
        return False
