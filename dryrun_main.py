import argparse
from runner.screener_runner import run_screener
import logging

def main():
    parser = argparse.ArgumentParser(description="Dry Run Screener")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--limit", type=int, default=50, help="Number of tickers to screen")
    parser.add_argument("--tighten", action="store_true", help="Apply optional filters: beta > 1, market cap >= 2B, pre-market change > 1%")
    parser.add_argument("--cooldown", type=int, default=3, help="Seconds to wait between batches")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO

    print(f"🧪 Dry Run Screener — Limit: {args.limit}, Optional Filters: {args.tighten}, Log Level: {'DEBUG' if args.debug else 'INFO'}")

    run_screener(
        limit=args.limit,
        use_optional_filters=args.tighten,
        log_level=log_level,
        cooldown=args.cooldown
    )

if __name__ == "__main__":
    main()
