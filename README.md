# makefun-btc-race-24h-20261118-1444-v2

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/deva1999/makefun-btc-race-24h-20261118-1444-v2/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/deva1999/makefun-btc-race-24h-20261118-1444-v2/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

A long-only dip-buy mean-reversion bot for Coinbase Wrapped BTC (cbBTC), revision 2: it buys the moment price closes 70 bps below its 120-minute rolling mean, at full size, then sells into recovery at 95 bps above its cost basis or cuts the trade at 200 bps below it. Revision 2 re-tunes variant 1 on the dev grade (net PnL +$12.84, 4 trades, max drawdown 0.675%): the take-profit moves 80 to 95 bps, because both dev recoveries ran past +95 bps while +105 bps was never reached on a close, and the stop widens 150 to 200 bps, because it never fired on the dev window. It trades one-minute bars of cbBTC against USDC, starting from $1,000 of paper money, in make.fun's 24-hour BTC trading-bot race.

## Run it

```sh
python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=gx4yrk51&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
