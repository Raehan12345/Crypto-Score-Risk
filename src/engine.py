from collections import deque
import pandas as pd
import numpy as np

class BacktestEngine:
    def __init__(self, initial_capital=10000, fee=0.001):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.fee = fee
        self.inventory = deque()
        self.total_qty = 0
        self.equity_curve = []
        self.drawdown_curve = []
        self.peak_equity = initial_capital
        self.last_buy_price = 0 

    def execute_buy(self, price, amount):
        if self.cash >= amount and amount > 0:
            qty = (amount * (1 - self.fee)) / price
            self.inventory.append((qty, price))
            self.total_qty += qty
            self.cash -= amount

    def execute_sell_fifo(self, price, percent):
        if self.total_qty <= 0: return
        
        target_qty = self.total_qty * percent
        realized_qty = 0
        
        while target_qty > 0 and self.inventory:
            lot_qty, lot_price = self.inventory.popleft()
            if lot_qty <= target_qty:
                realized_qty += lot_qty
                target_qty -= lot_qty
            else:
                remainder = lot_qty - target_qty
                self.inventory.appendleft((remainder, lot_price))
                realized_qty += target_qty
                target_qty = 0
                
        proceeds = realized_qty * price * (1 - self.fee)
        self.cash += proceeds
        self.total_qty -= realized_qty

    def run(self, df):
        for index, row in df.iterrows():
            price = row['close']
            risk = row['risk_score']

            # laddered Scale-out
            if risk > 70:
                self.execute_sell_fifo(price, 0.20)
                if self.total_qty == 0:
                    self.last_buy_price = 0
            
            # tiered DCA 
            elif risk < 30:
                if self.total_qty == 0 or price < (self.last_buy_price * 0.995):
                    self.execute_buy(price, self.cash * 0.15) # Back to 15%
                    self.last_buy_price = price
                    
            elif risk < 50:
                if self.total_qty == 0 or price < (self.last_buy_price * 0.995):
                    self.execute_buy(price, self.cash * 0.08) # Up to 8%
                    self.last_buy_price = price

            # metrics
            current_equity = self.cash + (self.total_qty * price)
            self.equity_curve.append(current_equity)
            
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity
            
            drawdown = (self.peak_equity - current_equity) / self.peak_equity
            self.drawdown_curve.append(drawdown * 100)

        df['equity'] = self.equity_curve
        df['drawdown'] = self.drawdown_curve
        return df
    
    def get_metrics(self, risk_free_rate=0.0):
        final_equity = self.equity_curve[-1]
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        mdd = max(self.drawdown_curve) if self.drawdown_curve else 0
        
        # period-to-period returns
        equity_series = pd.Series(self.equity_curve)
        returns = equity_series.pct_change().dropna()
        
        if len(returns) > 0 and returns.std() != 0:
            # annualise factor for 15m candles
            annual_factor = np.sqrt(35040)
            
            # mean and stdev of returns
            mean_return = returns.mean()
            std_return = returns.std()
            
            # annualised sharpe
            sharpe_ratio = (mean_return / std_return) * annual_factor
        else:
            sharpe_ratio = 0.0
            
        return final_equity, total_return, mdd, sharpe_ratio