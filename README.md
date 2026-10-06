# Tri-Exchange Order Flow Scalper

MVP de scalping BTCUSDT perp qui agrège Binance Futures, Bybit Linear et OKX Swap. Il produit des signaux heuristiques à partir des trades agressifs, CVD normalisé, imbalance du carnet, extrêmes récents et confirmation multi-exchange.

Aucune clé API n'est nécessaire. Le système ne passe aucun ordre réel.

## Render
1. Push les fichiers sur GitHub.
2. Render -> New -> Blueprint.
3. Sélectionne le repo.
4. Render utilise `render.yaml`.
5. Ouvre l'URL fournie.

Variables: `SYMBOL=BTCUSDT`, `BOOK_DEPTH=20`, `ROLLING_SECONDS=60`, `MIN_SCORE=70`.

## Important
Ce n'est pas encore une stratégie prouvée rentable. L'absorption est inférée par le comportement prix/flux, pas observée comme une donnée native parfaite. La prochaine version devrait ajouter replay tick, backtest, liquidation/OI, détection de sweep plus robuste, persistance et Telegram.
