import asyncio,json,time,websockets
from .models import Trade,Book
class BinanceClient:
    name='binance'
    def __init__(self,symbol,depth=20): self.symbol=symbol; self.depth=depth
    async def run(self,on_trade,on_book):
        s=self.symbol.lower(); url=f'wss://fstream.binance.com/stream?streams={s}@aggTrade/{s}@depth20@100ms'
        while True:
            try:
                async with websockets.connect(url,ping_interval=20,ping_timeout=20) as ws:
                    async for raw in ws:
                        d=json.loads(raw).get('data',{}); typ=d.get('e')
                        if typ=='aggTrade':
                            side='sell' if d.get('m') else 'buy'
                            await on_trade(Trade(self.name,d['T']/1000,float(d['p']),float(d['q']),side))
                        elif typ=='depthUpdate':
                            b=[(float(p),float(q)) for p,q in d.get('b',[]) if float(q)>0]; a=[(float(p),float(q)) for p,q in d.get('a',[]) if float(q)>0]
                            await on_book(Book(self.name,time.time(),b,a))
            except Exception as e: print('Binance reconnect',repr(e)); await asyncio.sleep(2)
class BybitClient:
    name='bybit'
    def __init__(self,symbol,depth=20): self.symbol=symbol; self.depth=depth
    async def run(self,on_trade,on_book):
        url='wss://stream.bybit.com/v5/public/linear'
        while True:
            try:
                async with websockets.connect(url,ping_interval=20,ping_timeout=20) as ws:
                    await ws.send(json.dumps({'op':'subscribe','args':[f'publicTrade.{self.symbol}',f'orderbook.{self.depth}.{self.symbol}']}))
                    async for raw in ws:
                        m=json.loads(raw); topic=m.get('topic',''); d=m.get('data')
                        if topic.startswith('publicTrade.') and isinstance(d,list):
                            for x in d: await on_trade(Trade(self.name,int(x['T'])/1000,float(x['p']),float(x['v']),'buy' if x['S']=='Buy' else 'sell'))
                        elif topic.startswith('orderbook.') and isinstance(d,dict):
                            b=[(float(x[0]),float(x[1])) for x in d.get('b',[]) if float(x[1])>0]; a=[(float(x[0]),float(x[1])) for x in d.get('a',[]) if float(x[1])>0]
                            await on_book(Book(self.name,time.time(),b,a))
            except Exception as e: print('Bybit reconnect',repr(e)); await asyncio.sleep(2)
class OKXClient:
    name='okx'
    def __init__(self,symbol,depth=20): self.symbol=symbol
    async def run(self,on_trade,on_book):
        url='wss://ws.okx.com:8443/ws/v5/public'; inst=f'{self.symbol[:-4]}-USDT-SWAP' if self.symbol.endswith('USDT') else self.symbol
        while True:
            try:
                async with websockets.connect(url,ping_interval=20,ping_timeout=20) as ws:
                    await ws.send(json.dumps({'op':'subscribe','args':[{'channel':'trades','instId':inst},{'channel':'books','instId':inst}]}))
                    async for raw in ws:
                        m=json.loads(raw); ch=m.get('arg',{}).get('channel'); data=m.get('data',[])
                        if ch=='trades':
                            for x in data: await on_trade(Trade(self.name,int(x['ts'])/1000,float(x['px']),float(x['sz']),x['side']))
                        elif ch=='books':
                            for x in data:
                                b=[(float(v[0]),float(v[1])) for v in x.get('bids',[]) if float(v[1])>0]; a=[(float(v[0]),float(v[1])) for v in x.get('asks',[]) if float(v[1])>0]
                                await on_book(Book(self.name,time.time(),b,a))
            except Exception as e: print('OKX reconnect',repr(e)); await asyncio.sleep(2)
