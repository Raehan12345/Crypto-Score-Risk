import matplotlib.pyplot as plt
from src.data_loader import get_project_data
from src.indicators import *
from src.engine import BacktestEngine

def run_project():
    print("Initializing Project: The Score Risk System")
    
    # load data
    df = get_project_data()
    print(f"Data loaded successfully. Total periods: {len(df)}")

    # indicators
    print("Calculating Synthetic Risk Metrics...")
    df['s_ath'] = calculate_ath_score(df['close'])
    df['s_trend'] = calculate_trend_score(df['close'])
    df['s_vol'] = calculate_vol_score(df['close'])
    df['s_ratio'] = calculate_ratio_score(df['eth_btc_ratio'])

    # weights
    w_ath, w_trend, w_vol, w_ratio = 0.30, 0.30, 0.20, 0.20
    df['risk_score'] = (
        (df['s_ath'] * w_ath) + 
        (df['s_trend'] * w_trend) + 
        (df['s_vol'] * w_vol) + 
        (df['s_ratio'] * w_ratio)
    )

    # backtest
    print("Simulating Event-Driven Execution...")
    engine = BacktestEngine(initial_capital=10000)
    results_df = engine.run(df)
    
    final_eq, total_ret, mdd, sharpe = engine.get_metrics()
    
    print("\n--- Backtest Results ---")
    print(f"Final Equity: ${final_eq:,.2f}")
    print(f"Total Return: {total_ret:.2f}%")
    print(f"Max Drawdown: {mdd:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")

    # plot
    print("Generating Performance Charts...")
    
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # equity curve
    ax1.plot(results_df.index, results_df['equity'], color='orange', linewidth=1.5)
    ax1.set_title(f"Strategy Performance | Total Return: {total_ret:.2f}% | MDD: {mdd:.2f}%")
    ax1.set_ylabel("Equity ($)")
    ax1.grid(True, alpha=0.3)
    
    # drawdown curve
    ax2.fill_between(results_df.index, results_df['drawdown'], 0, color='red', alpha=0.4)
    ax2.plot(results_df.index, results_df['drawdown'], color='red', linewidth=0.5)
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("Date")
    ax2.invert_yaxis()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_project()