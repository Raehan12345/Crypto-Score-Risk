from collections import deque
import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, initial_capital=10000, fee=0.001):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.fee = fee
        
        # separate queues for bi-directional inventory tracking
        self.long_inventory = deque()
        self.total_long_qty = 0
        self.last_long_price = 0
        self.highest_long_price = 0
        
        self.short_inventory = deque()
        self.total_short_qty = 0
        self.last_short_price = 0
        
        # track the previous regime for crossover detection
        self.previous_regime = 1

        self.equity_curve = []
        self.drawdown_curve = []
        self.peak_equity = initial_capital

    def execute_buy_long(self, price, amount):
        if self.cash >= amount and amount > 0:
            qty = (amount * (1 - self.fee)) / price
            self.long_inventory.append((qty, price))
            self.total_long_qty += qty
            self.cash -= amount

    def execute_sell_long_fifo(self, price, percent):
        if self.total_long_qty <= 0: return
        
        target_qty = self.total_long_qty * percent
        realized_qty = 0
        
        while target_qty > 0 and self.long_inventory:
            lot_qty, lot_price = self.long_inventory.popleft()
            if lot_qty <= target_qty:
                realized_qty += lot_qty
                target_qty -= lot_qty
            else:
                remainder = lot_qty - target_qty
                self.long_inventory.appendleft((remainder, lot_price))
                realized_qty += target_qty
                target_qty = 0
                
        proceeds = realized_qty * price * (1 - self.fee)
        self.cash += proceeds
        self.total_long_qty -= realized_qty

    def execute_short(self, price, amount, current_equity):
        # rudimentary margin check to prevent over-leveraging
        if current_equity >= amount and amount > 0:
            qty = amount / price
            proceeds = amount * (1 - self.fee)
            self.short_inventory.append((qty, price))
            self.total_short_qty += qty
            self.cash += proceeds

    def execute_cover_short_fifo(self, price, percent):
        if self.total_short_qty <= 0: return
        
        target_qty = self.total_short_qty * percent
        realized_qty = 0
        
        while target_qty > 0 and self.short_inventory:
            lot_qty, lot_price = self.short_inventory.popleft()
            if lot_qty <= target_qty:
                realized_qty += lot_qty
                target_qty -= lot_qty
            else:
                remainder = lot_qty - target_qty
                self.short_inventory.appendleft((remainder, lot_price))
                realized_qty += target_qty
                target_qty = 0
                
        cost = realized_qty * price * (1 + self.fee)
        self.cash -= cost
        self.total_short_qty -= realized_qty

    def run(self, df):
        # pre-calculate monthly volatility (2880 candles) for sizing
        vol_30d = df['atr'].rolling(window=2880).mean()
        
        for index, row in df.iterrows():
            price, risk, atr = row['close'], row['risk_score'], row['atr']
            regime = row['macro_regime']
            current_equity = self.cash + (self.total_long_qty * price) - (self.total_short_qty * price)

            # institutional vol-targeting: size positions relative to 30d risk
            # if the market is twice as volatile as its average, we trade half size
            vol_target_multiplier = min(1.0, max(0.2, vol_30d.loc[index] / atr)) if atr > 0 else 1.0

            # pillar 1: macro bull execution
            if regime == 1:
                if risk < 45:
                    # require 1.8x atr spacing to prevent bunching during bull wicks
                    if self.total_long_qty == 0 or price < (self.last_long_price - (atr * 1.8)):
                        # increase base size to 24% to recover growth profile
                        self.execute_buy_long(price, current_equity * 0.24 * vol_target_multiplier)
                        self.last_long_price = price
                
                # laddered profit taking at risk extremes
                elif risk > 85:
                    self.execute_sell_long_fifo(price, 0.35)
            
            # pillar 2: active bear hedging
            else:
                # only short if risk score is extremely high (exhaustion bounces)
                if risk > 75:
                    if self.total_short_qty == 0 or price > (self.last_short_price + (atr * 2.0)):
                        # capped at 4% to act as a rebate, not a primary driver
                        self.execute_short(price, current_equity * 0.04, current_equity)
                        self.last_short_price = price
                elif risk < 35:
                    self.execute_cover_short_fifo(price, 0.45)

            # metrics recording
            current_equity = self.cash + (self.total_long_qty * price) - (self.total_short_qty * price)
            self.equity_curve.append(current_equity)
            if current_equity > self.peak_equity: self.peak_equity = current_equity
            dd = (self.peak_equity - current_equity) / self.peak_equity if self.peak_equity > 0 else 0
            self.drawdown_curve.append(dd * 100)

        df['equity'], df['drawdown'] = self.equity_curve, self.drawdown_curve
        return df
    
    def get_metrics(self):
        final_equity = self.equity_curve[-1]
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        mdd = max(self.drawdown_curve) if self.drawdown_curve else 0
        
        equity_series = pd.Series(self.equity_curve)
        returns = equity_series.pct_change().dropna()
        
        if len(returns) > 0 and returns.std() != 0:
            annual_factor = np.sqrt(35040)
            mean_return = returns.mean()
            std_return = returns.std()
            sharpe_ratio = (mean_return / std_return) * annual_factor
        else:
            sharpe_ratio = 0.0
            
        return final_equity, total_return, mdd, sharpe_ratio