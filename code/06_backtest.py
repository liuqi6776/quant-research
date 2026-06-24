#!/usr/bin/env python3
"""
06_backtest.py - 回测框架
验证"偏离度均值回归"策略的有效性
注意：这里用的是价格偏离均线作为Max Pain偏离度的代理
真正的Max Pain回测需要历史Max Pain时间序列
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

COMMISSION = 0.001
SLIPPAGE = 0.0005


def backtest_daily(etf_df, thresh_long=-2.0, thresh_short=3.0, hold_days=5):
    """
    逐日回测框架（不重叠持仓版本）
    
    参数:
        etf_df: 包含close, ma_20, deviation的DataFrame
        thresh_long: 做多阈值（偏离度<%时做多）
        thresh_short: 做空阈值（偏离度>%时做空）
        hold_days: 持有天数
    
    返回:
        trades_df: 交易记录
        daily_df: 每日仓位和收益
    """
    df = etf_df.copy()
    n = len(df)
    
    position = 0
    entry_day = -1
    entry_price = 0
    
    trades = []
    daily_pnl = []
    
    for i in range(20, n - 1):
        # 当日P&L
        if position != 0:
            daily_ret = df.loc[i, 'returns']
            daily_pnl.append({
                'date': df.loc[i, 'time'],
                'position': position,
                'daily_ret': daily_ret * position,
                'close': df.loc[i, 'close'],
            })
        else:
            daily_pnl.append({
                'date': df.loc[i, 'time'],
                'position': 0,
                'daily_ret': 0,
                'close': df.loc[i, 'close'],
            })
        
        # 平仓检查
        if position != 0 and i - entry_day >= hold_days:
            exit_price = df.loc[i, 'close']
            gross_ret = (exit_price / entry_price - 1) * position
            net_ret = gross_ret - COMMISSION - SLIPPAGE
            trades.append({
                'entry_day': entry_day, 'exit_day': i,
                'direction': position,
                'entry_price': entry_price, 'exit_price': exit_price,
                'gross_ret': gross_ret, 'net_ret': net_ret,
            })
            position = 0
            entry_day = -1
        
        # 开新仓（空仓时）
        if position == 0:
            dev = df.loc[i, 'deviation']
            if dev < thresh_long:
                position, entry_day, entry_price = 1, i, df.loc[i, 'close']
            elif dev > thresh_short:
                position, entry_day, entry_price = -1, i, df.loc[i, 'close']
    
    # 强制平仓
    if position != 0:
        i = n - 1
        exit_price = df.loc[i, 'close']
        gross_ret = (exit_price / entry_price - 1) * position
        net_ret = gross_ret - COMMISSION - SLIPPAGE
        trades.append({
            'entry_day': entry_day, 'exit_day': i,
            'direction': position,
            'entry_price': entry_price, 'exit_price': exit_price,
            'gross_ret': gross_ret, 'net_ret': net_ret,
        })
        daily_pnl.append({
            'date': df.loc[i, 'time'], 'position': position,
            'daily_ret': df.loc[i, 'returns'] * position,
            'close': df.loc[i, 'close'],
        })
    
    return pd.DataFrame(trades), pd.DataFrame(daily_pnl)


def parameter_scan(etf_df):
    """参数扫描"""
    results = []
    for tl in [-3.0, -2.0, -1.5, -1.0]:
        for ts in [2.0, 3.0, 4.0, 5.0]:
            for hd in [3, 5, 10]:
                tdf, ddf = backtest_daily(etf_df, tl, ts, hd)
                if len(tdf) >= 5:
                    total = (ddf['daily_ret'] + 1).prod() - 1
                    ddf['cum'] = (1 + ddf['daily_ret']).cumprod()
                    ddf['cmax'] = ddf['cum'].cummax()
                    dd = (ddf['cum'] / ddf['cmax'] - 1).min()
                    ann = (1 + total) ** (252 / len(ddf)) - 1
                    results.append({
                        'tl': tl, 'ts': ts, 'hd': hd,
                        'trades': len(tdf), 'total': total * 100,
                        'ann': ann * 100, 'dd': dd * 100,
                        'win_rate': (tdf['net_ret'] > 0).mean() * 100,
                        'calmar': ann / abs(dd) if dd != 0 else 0,
                    })
    return pd.DataFrame(results)


if __name__ == "__main__":
    # 加载数据
    etf = pd.read_csv('../data/etf_50_price.csv')
    etf['time'] = pd.to_datetime(etf['time'])
    etf = etf.sort_values('time').reset_index(drop=True)
    etf['ma_20'] = etf['close'].rolling(20).mean()
    etf['deviation'] = (etf['close'] / etf['ma_20'] - 1) * 100
    etf['returns'] = etf['close'].pct_change()
    
    # 参数扫描
    print("Running parameter scan...")
    res_df = parameter_scan(etf)
    best = res_df.nlargest(1, 'calmar').iloc[0]
    
    print(f"\nBest params: long={best['tl']}, short={best['ts']}, hold={best['hd']}")
    print(f"Total return: {best['total']:+.2f}%")
    print(f"Max drawdown: {best['dd']:.2f}%")
    print(f"Win rate: {best['win_rate']:.1f}%")
    print(f"Trades: {best['trades']}")
    
    # ⚠️ 警告
    print("\n⚠️ WARNING: Only {} trades over ~18 months.".format(int(best['trades'])))
    print("This is likely overfitted. Use with extreme caution.")
