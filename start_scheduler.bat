@echo off
cd /d "F:\Nick\My Code\trading\day_trading_screener"
set PYTHONPATH=.
python scheduler.py --interval 15 --limit 2500 --tighten --debug --cooldown 30

