from collections import deque,defaultdict
from time import time
import asyncio
class Engine:
    def __init__(self,rolling_seconds=60,min_score=70): self.window=rolling_seconds; self.min_score=min_score; self.trades=deque(maxlen=50000); self.books={}; self.last_signal=None; self.signal_history=deque(maxlen=50); self.lock=asyncio.Lock()
    async def add_trade(self,t):
        async with self.lock: self.trades.append(t); self._trim()
    async def add_book(self,b):
        async with self.lock: self.books[b.exchange]=b
    def _trim(self):
        c=time()-self.window
        while self.trades and self.trades[0].ts<c: self.trades.popleft()
    def snapshot(self):
        self._trim(); trades=list(self.trades)
        if not trades: return {'status':'warming_up','signal':None}
        by=defaultdict(list)
        for t in trades: by[t.exchange].append(t)
        prices=[t.price for t in trades[-1000:]]; current=prices[-1]; hi=max(prices); lo=min(prices); span=max(hi-lo,current*.0001)
        metrics={}
        for ex in ['binance','bybit','okx']:
            ts=by[ex]; buy=sum(t.qty for t in ts if t.side=='buy'); sell=sum(t.qty for t in ts if t.side=='sell'); cvd=buy-sell; den=buy+sell; book=self.books.get(ex)
            metrics[ex]={'buy_volume':round(buy,4),'sell_volume':round(sell,4),'cvd_norm':round(cvd/den,4) if den else 0,'imbalance':round(book.imbalance,4) if book else 0}
        books=[b for b in self.books.values() if b.mid]; mid=sum(b.mid for b in books)/len(books) if books else current; avg_imb=sum(b.imbalance for b in books)/len(books) if books else 0; cvds=[m['cvd_norm'] for m in metrics.values() if m['buy_volume']+m['sell_volume']]; avg_cvd=sum(cvds)/len(cvds) if cvds else 0
        recent=trades[-300:]; rprice=recent[-1].price; rlo=min(t.price for t in recent); rhi=max(t.price for t in recent); sv=sum(t.qty for t in recent if t.side=='sell'); bv=sum(t.qty for t in recent if t.side=='buy'); total=sv+bv; sr=sv/total if total else .5
        near_low=(current-lo)/span<.18; near_high=(hi-current)/span<.18; ls=ss=0; lr=[]; rr=[]
        if near_low: ls+=20; lr.append('near recent low/liquidity')
        if near_high: ss+=20; rr.append('near recent high/liquidity')
        if avg_cvd<-.12: ls+=20; lr.append('aggressive selling')
        if avg_cvd>.12: ss+=20; rr.append('aggressive buying')
        if avg_imb>.12: ls+=20; lr.append('bid-side imbalance')
        if avg_imb<-.12: ss+=20; rr.append('ask-side imbalance')
        if near_low and sr>.58 and rprice>rlo*1.00015: ls+=25; lr.append('selling pressure without fresh low')
        if near_high and sr<.42 and rprice<rhi*.99985: ss+=25; rr.append('buying pressure without fresh high')
        lc=sum(1 for m in metrics.values() if m['cvd_norm']<-.05 and m['imbalance']>-.05); sc=sum(1 for m in metrics.values() if m['cvd_norm']>.05 and m['imbalance']<.05)
        if lc>=2: ls+=15; lr.append(f'{lc}/3 exchanges confirm')
        if sc>=2: ss+=15; rr.append(f'{sc}/3 exchanges confirm')
        score=max(ls,ss); side='LONG' if ls>ss else 'SHORT' if ss>ls else 'NONE'; sig=None
        if score>=self.min_score and side!='NONE':
            sig={'side':side,'score':score,'price':round(mid,2),'reasons':lr if side=='LONG' else rr,'timestamp':time(),'warning':'Heuristic signal — validate before trading.'}
            if not self.last_signal or self.last_signal['side']!=side or time()-self.last_signal['timestamp']>20: self.last_signal=sig; self.signal_history.appendleft(sig)
        return {'status':'live','price':round(mid,2),'range_low':round(lo,2),'range_high':round(hi,2),'avg_cvd':round(avg_cvd,4),'avg_imbalance':round(avg_imb,4),'signal':sig,'metrics':metrics,'history':list(self.signal_history)}
