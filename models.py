from dataclasses import dataclass
@dataclass
class Trade:
    exchange:str; ts:float; price:float; qty:float; side:str
@dataclass
class Book:
    exchange:str; ts:float; bids:list; asks:list
    @property
    def best_bid(self): return self.bids[0][0] if self.bids else 0.0
    @property
    def best_ask(self): return self.asks[0][0] if self.asks else 0.0
    @property
    def mid(self): return (self.best_bid+self.best_ask)/2 if self.best_bid and self.best_ask else 0.0
    @property
    def imbalance(self):
        b=sum(q for _,q in self.bids); a=sum(q for _,q in self.asks); t=b+a
        return (b-a)/t if t else 0.0
