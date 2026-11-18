"""Dip-buy mean-reversion bot for cbBTC, revision 2 (make.fun btc-race-24h).

Long only, one position at a time, whole-cash entries. The bot watches the
close of each one-minute bar against the mean of the last 120 closes and
buys the dip when the close sits 70 basis points or more below that mean.
It exits the whole position when the close recovers 95 basis points above
its cost basis, or cuts it when the close falls 200 basis points below it.
After any exit it rests ten bars before looking for the next dip, and it
opens nothing in the final hour of the window, so no position is left to be
flattened at a loss by the end-of-window close.

Everything is integer arithmetic on the protocol's own units (prices at
price_scale 5, quantities at qty_scale 8, cash at quote_scale 6), so two
runs on the same bars produce the same orders. No clock, no environment,
no files, no randomness.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# Revision-2 tuning, chosen on the kit dev window plus held-out sub-windows:
# the take-profit moved 80 -> 95 bps (both dev recoveries ran past +95 bps
# while the +105 bps level was never reached on a close, so 95 sits
# mid-plateau instead of at the cliff edge), and the stop widened 150 ->
# 200 bps (it never fired on the dev window, so the wider stop only cuts
# whipsaw exits on a noisier fresh window). Entry, mean length, rest and
# the final-hour rule are unchanged from variant 1.
MEAN_BARS = 120
DIP_BPS = 70
TAKE_BPS = 95
STOP_BPS = 200
REST_BARS = 10
NO_BUY_TAIL_BARS = 60
MAX_SLIPPAGE_BPS = 500
BPS = 10000


class DipBuyer:
    """Rolling-mean dip buyer. One instance lives for the whole replay."""

    def __init__(self):
        self.closes = []
        self.running_total = 0
        self.rest_left = 0
        self.scales = None

    def note_close(self, close):
        self.closes.append(close)
        self.running_total += close
        if len(self.closes) > MEAN_BARS:
            self.running_total -= self.closes[len(self.closes) - MEAN_BARS - 1]

    def mean(self):
        if len(self.closes) < MEAN_BARS:
            return None
        return self.running_total // MEAN_BARS

    def cost_basis_price(self, holding):
        """Price at which the held quantity is worth exactly its cash cost.

        Scales come from hello, never hard-coded: the basis is the inverse of
        value(qty, price) = qty * price * 10^quote_scale /
        10^(qty_scale + price_scale).
        """
        qty_scale, price_scale, quote_scale = self.scales
        return (holding.cost * 10 ** (qty_scale + price_scale)
                // (holding.qty * 10 ** quote_scale))

    def decide(self, state):
        if self.scales is None:
            symbol = next(s for s in state.hello["symbols"]
                          if s["symbol"] == SYMBOL)
            self.scales = (symbol["qty_scale"], symbol["price_scale"],
                           state.hello["capital"]["quote_scale"])
        close = state.close(SYMBOL)
        if close is None:
            return []
        self.note_close(close)
        holding = state.positions.get(SYMBOL)
        if holding is not None:
            basis = self.cost_basis_price(holding)
            if close * BPS >= basis * (BPS + TAKE_BPS):
                self.rest_left = REST_BARS
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            if close * BPS <= basis * (BPS - STOP_BPS):
                self.rest_left = REST_BARS
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []
        if self.rest_left > 0:
            self.rest_left -= 1
            return []
        mean = self.mean()
        if mean is None:
            return []
        if state.seq >= 1440 - NO_BUY_TAIL_BARS:
            return []
        if close * BPS <= mean * (BPS - DIP_BPS):
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []


BOT = DipBuyer()


def on_batch(state, batch):
    return BOT.decide(state)


makefun_bars.run(on_batch)
