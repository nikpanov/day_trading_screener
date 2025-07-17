from db.reader import load_watchlist_symbols

tickers = load_watchlist_symbols()
print("Retrieved tickers:", tickers)
