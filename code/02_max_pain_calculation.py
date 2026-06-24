#!/usr/bin/env python3
"""
02_max_pain_calculation.py - Max Pain计算模块
计算股指期权和ETF期权的Max Pain（最痛点）
"""

import pandas as pd
import numpy as np
import requests


def get_cffex_option_data():
    """
    从中金所获取股指期权数据
    返回DataFrame包含各合约的持仓量信息
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
                                })
                        except:
                            continue
                all_data[option_code] = pd.DataFrame(data)
        except Exception as e:
            print(f"[ERROR] {option_code}: {e}")
    return all_data


def calculate_max_pain(df, contract_month):
    """
    从期权链数据中计算Max Pain
    
    参数:
        df: 包含期权合约数据的DataFrame
        contract_month: 合约月份，如 '2606'
    
    返回:
        max_pain_strike: Max Pain对应的行权价
        pain_df: 各价格点的pain值明细
    """
    month_data = df[df['contract_month'] == contract_month]
    if len(month_data) == 0:
        return None, None
    
    calls = month_data[month_data['option_type'] == 'C'].set_index('strike')['position']
    puts = month_data[month_data['option_type'] == 'P'].set_index('strike')['position']
    all_strikes = sorted(set(calls.index) | set(puts.index))
    
    if len(all_strikes) == 0:
        return None, None
    
    min_pain = float('inf')
    max_pain_strike = None
    pain_details = []
    
    for expire_price in all_strikes:
        call_pain = 0
        put_pain = 0
        for strike in all_strikes:
            call_oi = calls.get(strike, 0)
            call_pain += max(0, expire_price - strike) * call_oi
            put_oi = puts.get(strike, 0)
            put_pain += max(0, strike - expire_price) * put_oi
        
        total_pain = call_pain + put_pain
        pain_details.append({
            'expire_price': expire_price,
            'call_pain': call_pain,
            'put_pain': put_pain,
            'total_pain': total_pain
        })
        
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = expire_price
    
    return max_pain_strike, pd.DataFrame(pain_details)


def calculate_max_pain_from_yahoo_options(calls_df, puts_df):
    """
    从Yahoo Finance期权数据计算Max Pain
    适用于美股期权
    """
    calls_df = calls_df.copy()
    puts_df = puts_df.copy()
    calls_df['option_type'] = 'C'
    puts_df['option_type'] = 'P'
    
    all_options = pd.concat([calls_df, puts_df], ignore_index=True)
    all_options['openInterest'] = all_options['openInterest'].fillna(0)
    all_options = all_options[all_options['openInterest'] > 0]
    
    calls_oi = all_options[all_options['option_type']=='C'].groupby('strike')['openInterest'].sum()
    puts_oi = all_options[all_options['option_type']=='P'].groupby('strike')['openInterest'].sum()
    
    all_strikes = sorted(set(calls_oi.index) & set(puts_oi.index))
    contract_multiplier = 100
    
    min_pain = float('inf')
    max_pain_strike = None
    
    for expire_price in all_strikes:
        call_pain = sum(max(0, expire_price - s) * calls_oi.get(s, 0) * contract_multiplier for s in all_strikes)
        put_pain = sum(max(0, s - expire_price) * puts_oi.get(s, 0) * contract_multiplier for s in all_strikes)
        total_pain = call_pain + put_pain
        
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = expire_price
    
    return max_pain_strike


def analyze_all_contracts(option_data_dict):
    """
    分析所有期权合约的Max Pain
    返回汇总DataFrame
    """
    results = []
    
    for code, name, price in [('IO', '沪深300', 4745.22), 
                               ('HO', '上证50', 2847.46), 
                               ('MO', '中证1000', 8158.73)]:
        df = option_data_dict.get(code)
        if df is None or len(df) == 0:
            continue
        
        for month in sorted(df['contract_month'].unique()):
            mp, pain_df = calculate_max_pain(df, month)
            if mp:
                month_data = df[df['contract_month'] == month]
                total_oi = month_data['position'].sum()
                call_oi = month_data[month_data['option_type'] == 'C']['position'].sum()
                put_oi = month_data[month_data['option_type'] == 'P']['position'].sum()
                
                results.append({
                    'contract': f'{code}{month}',
                    'index_name': name,
                    'max_pain': mp,
                    'current_price': price,
                    'diff': mp - price,
                    'diff_pct': (mp/price - 1) * 100,
                    'total_oi': total_oi,
                    'call_oi': call_oi,
                    'put_oi': put_oi,
                    'pcr': put_oi/call_oi if call_oi > 0 else 0,
                })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    print("=" * 60)
    print("Max Pain 计算模块")
    print("=" * 60)
    
    # 1. 获取数据
    print("\n[1/2] 获取中金所期权数据...")
    option_data = get_cffex_option_data()
    
    # 2. 计算Max Pain
    print("\n[2/2] 计算各合约Max Pain...")
    results_df = analyze_all_contracts(option_data)
    
    # 3. 保存结果
    output_path = '../data/a50_all_index_maxpain.csv'
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n[OK] 结果已保存: {output_path}")
    
    # 4. 打印汇总
    print("\n=== Max Pain 汇总 ===")
    for code in ['IO', 'HO', 'MO']:
        code_data = results_df[results_df['contract'].str.startswith(code)]
        if len(code_data) > 0:
            print(f"\n{code} ({code_data.iloc[0]['index_name']}):")
            for _, row in code_data.iterrows():
                print(f"  {row['contract']}: MaxPain={row['max_pain']} "
                      f"(偏离{row['diff_pct']:+.2f}%)")
