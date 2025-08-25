from fastapi import FastAPI, BackgroundTasks
from trading.strategy import MovingAverageCrossover, StrategyConfig
from trading.engine import TradingEngine
import pandas as pd
import asyncio
from typing import Optional

app = FastAPI()

strategy = MovingAverageCrossover(StrategyConfig())
engine = TradingEngine()

running_task: Optional[asyncio.Task] = None

async def run_strategy(symbol: str, interval_seconds: int = 60):
    global running_task
    print("Starting strategy loop")
    while True:
        # fetch recent market data - placeholder using Alpaca
        bars = engine.api.get_barset(symbol, 'minute', limit=engine.positions.get('lookback', 60))[symbol]
        data = pd.DataFrame({
            'close': [bar.c for bar in bars]
        }, index=[bar.t for bar in bars])
        signal_series = strategy.generate_signals(data)
        latest_signal = signal_series.iloc[-1]
        if latest_signal == 1:
            engine.submit_order(symbol, qty=1, side='buy')
        elif latest_signal == -1:
            engine.submit_order(symbol, qty=1, side='sell')
        await asyncio.sleep(interval_seconds)

@app.post('/start')
async def start(symbol: str = 'AAPL', interval: int = 60, background_tasks: BackgroundTasks = None):
    global running_task
    if running_task is None or running_task.done():
        running_task = asyncio.create_task(run_strategy(symbol=symbol, interval_seconds=interval))
        return {"status": "started"}
    return {"status": "already running"}

@app.post('/stop')
async def stop():
    global running_task
    if running_task and not running_task.done():
        running_task.cancel()
        return {"status": "stopping"}
    return {"status": "not running"}

@app.get('/status')
async def status():
    global running_task
    if running_task is None:
        return {"running": False}
    return {"running": not running_task.done()}