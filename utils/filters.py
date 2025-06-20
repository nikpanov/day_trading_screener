from utils.logger import setup_logger

logger = setup_logger()

def apply_optional_filters(price, fundamentals, pre_market_change_pct, logger=None, symbol=None, reasons=None):
    try:
        if fundamentals.get("beta") is None:
            msg = f"{symbol}: missing beta"
            if logger: logger.info(msg)
            if reasons is not None: reasons.append(msg)
            return False
        if fundamentals.get("market_cap") is None:
            msg = f"{symbol}: missing market cap"
            if logger: logger.info(msg)
            if reasons is not None: reasons.append(msg)
            return False
        if pre_market_change_pct is None:
            msg = f"{symbol}: missing pre-market change %"
            if logger: logger.info(msg)
            if reasons is not None: reasons.append(msg)
            return False

        if fundamentals["beta"] <= 1:
            msg = f"{symbol}: beta too low ({fundamentals['beta']})"
            if logger: logger.info(msg)
            if reasons is not None: reasons.append(msg)
            return False
        if fundamentals["market_cap"] < 2_000_000_000:
            msg = f"{symbol}: market cap too small ({fundamentals['market_cap']})"
            if logger: logger.info(msg)
            if reasons is not None: reasons.append(msg)
            return False
        if pre_market_change_pct <= 1:
            msg = f"{symbol}: pre-market change too low ({pre_market_change_pct})"
            if logger: logger.info(msg)
            if reasons is not None: reasons.append(msg)
            return False

        return True
    except Exception as e:
        msg = f"Optional filter error for {symbol}: {e}"
        if logger: logger.error(msg)
        if reasons is not None: reasons.append(msg)
        return False
    
def is_bullish(price, indicators, fundamentals=None, pre_market_change_pct=None, use_optional_filters=False, logger=None, symbol=None, reasons=None):
    if use_optional_filters:
        if not apply_optional_filters(price, fundamentals or {}, pre_market_change_pct, logger, symbol, reasons):
            return False

    if indicators is None:
        msg = f"{symbol}: missing indicators"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False

    vwap = indicators.get("vwap")
    ema20 = indicators.get("ema20")
    ema50 = indicators.get("ema50")
    rsi = indicators.get("rsi14")

    if vwap is None:
        msg = f"{symbol}: missing VWAP"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False
    if ema20 is None:
        msg = f"{symbol}: missing EMA20"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False
    if ema50 is None:
        msg = f"{symbol}: missing EMA50"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False
    if rsi is None:
        msg = f"{symbol}: missing RSI"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False

    if not (price > vwap):
        msg = f"{symbol}: price not above VWAP"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False
    if not (ema20 > ema50):
        msg = f"{symbol}: EMA20 not above EMA50"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False
    if not (50 < rsi < 70):
        msg = f"{symbol}: RSI not in range (50,70), actual: {rsi}"
        if logger: logger.info(msg)
        if reasons is not None: reasons.append(msg)
        return False

    return True