#!/usr/bin/env python3
"""
01_data_collection.py - 数据获取模块
获取A股ETF历史价格、股指期权数据、美股数据
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import akshare as ak

# ========== A股ETF价格数据获取 ==========

def get_etf_price_from_ifind(ticker, start_date, end_date, output_path):
    """
    从iFinD获取ETF历史价格数据
    注意：需要iFinD数据接口权限
    """
    # 使用akshare作为备选方案
    try:
        # 上交所ETF
        if ticker.endswith('.SH'):
            code = ticker.replace('.SH', '')
            df = ak.fund_etf_hist_em(symbol=code, period="daily", 
                                     start_date=start_date.replace('-', ''), 
                                     end_date=end_date.replace('-', ''), 
                                     adjust="qfq")
        # 深交所ETF
        elif ticker.endswith('.SZ'):
            code = ticker.replace('.SZ', '')
            df = ak.fund_etf_hist_em(symbol=code, period="daily",
                                     start_date=start_date.replace('-', ''),
                                     end_date=end_date.replace('-', ''),
                                     adjust="qfq")
        df.to_csv(output_path, index=False)
        print(f"[OK] {ticker} 数据已保存: {len(df)} 条")
        return df
    except Exception as e:
        print(f"[ERROR] {ticker} 获取失败: {e}")
        return None


def get_cffex_option_data():
    """
    从中金所获取股指期权数据
    返回: IO(沪深300), HO(上证50), MO(中证1000) 的持仓量数据
    """
    all_data = {}
    for option_code in ['IO', 'HO', 'MO']:
        url = f"http://www.cffex.com.cn/quote_{option_code}.txt"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                lines = resp.text.strip().split('\n')
                data = []
                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        instrument = parts[0]
                        try:
                            contract_parts = instrument.split('-')
                            if len(contract_parts) == 3:
                                data.append({
                                    'instrument': instrument,
                                    'contract_month': contract_parts[0][2:],
                                    'option_type': contract_parts[1],
                                    'strike': int(contract_parts[2]),
                                    'position': int(parts[1]) if parts[1] else 0,
                                    'volume': int(parts[2]) if parts[2] else 0,
                                })
                        except:
                            continue
                all_data[option_code] = pd.DataFrame(data)
                print(f"[OK] {option_code} 期权数据: {len(data)} 条")
        except Exception as e:
            print(f"[ERROR] {option_code} 获取失败: {e}")
    return all_data


def get_sse_etf_option_stats(date_str="20250611"):
    """获取上交所ETF期权日度统计"""
    try:
        df = ak.option_daily_stats_sse(date=date_str)
        print(f"[OK] 上交所ETF期权统计: {len(df)} 只ETF")
        return df
    except Exception as e:
        print(f"[ERROR] 上交所统计获取失败: {e}")
        return None


def get_szse_etf_option_stats(date_str="20250611"):
    """获取深交所ETF期权日度统计"""
    try:
        df = ak.option_daily_stats_szse(date=date_str)
        print(f"[OK] 深交所ETF期权统计: {len(df)} 只ETF")
        return df
    except Exception as e:
        print(f"[ERROR] 深交所统计获取失败: {e}")
        return None


# ========== 美股数据获取 ==========

def get_us_stock_price(ticker, start_date, end_date, output_path):
    """
    从Yahoo Finance获取美股历史数据
    注意：需要yfinance库
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        df.to_csv(output_path)
        print(f"[OK] {ticker} 数据已保存: {len(df)} 条")
        return df
    except Exception as e:
        print(f"[ERROR] {ticker} 获取失败: {e}")
        return None


# ========== 主程序 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("A股ETF期权研究 - 数据获取模块")
    print("=" * 60)
    
    # 1. 获取ETF历史价格
    etf_list = {
        '510050.SH': 'etf_50_price.csv',
        '510300.SH': 'etf_300_price.csv',
        '510500.SH': 'etf_500_price.csv',
        '588000.SH': 'etf_kc50_price.csv',
        '159915.SZ': 'etf_cy_price.csv',
    }
    
    print("\n[1/4] 获取ETF历史价格...")
    for ticker, filename in etf_list.items():
        get_etf_price_from_ifind(ticker, '2024-01-01', '2025-06-30', 
                                 f'../data/{filename}')
    
    # 2. 获取中金所股指期权数据
    print("\n[2/4] 获取中金所股指期权数据...")
    cffex_data = get_cffex_option_data()
    
    # 3. 获取ETF期权日度统计
    print("\n[3/4] 获取ETF期权日度统计...")
    sse_stats = get_sse_etf_option_stats()
    szse_stats = get_szse_etf_option_stats()
    
    # 4. 获取美股数据（如MU）
    print("\n[4/4] 获取美股数据...")
    get_us_stock_price('MU', '2024-06-01', '2026-06-10', '../data/mu_price_2y.csv')
    
    print("\n[COMPLETE] 数据获取完成!")
