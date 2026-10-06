import asyncio,os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .engine import Engine
from .exchanges import BinanceClient,BybitClient,OKXClient
app=FastAPI(title='Tri-Exchange Order Flow Scalper')
engine=Engine(int(os.getenv('ROLLING_SECONDS','60')),int(os.getenv('MIN_SCORE','70')))
@app.on_event('startup')
async def startup():
    symbol=os.getenv('SYMBOL','BTCUSDT'); depth=int(os.getenv('BOOK_DEPTH','20'))
    async def t(x): await engine.add_trade(x)
    async def b(x): await engine.add_book(x)
    for c in [BinanceClient(symbol,depth),BybitClient(symbol,depth),OKXClient(symbol,depth)]: asyncio.create_task(c.run(t,b))
@app.get('/api/state')
async def state(): return engine.snapshot()
@app.get('/',response_class=HTMLResponse)
async def home(): return HTMLResponse(open('app/static/index.html',encoding='utf-8').read())
