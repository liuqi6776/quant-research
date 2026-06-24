#!/usr/bin/env python3
"""
03_correlation_analysis.py - 相关性分析模块
分析Max Pain、PCR、OI与ETF价格的相关性
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def analyze_max_pain_price_correlation(mp_df, price_col='etf_price', mp_col='max_pain'):
    """
    分析Max Pain与ETF价格的相关性
    
    参数:
        mp_df: 包含max_pain和价格的DataFrame
        price_col: 价格列名
        mp_col: MaxPain列名
    
    返回:
        dict: 各项统计指标
    """
    # 基础统计
    diff = mp_df[mp_col] - mp_df[price_col]
    diff_pct = (mp_df[mp_col] / mp_df[price_col] - 1) * 100
    
    # Pearson相关系数
    pearson_r, pearson_p = stats.pearsonr(mp_df[price_col], mp_df[mp_col])
    
    # Spearman秩相关
    spearman_r, spearman_p = stats.spearmanr(mp_df[price_col], mp_df[mp_col])
    
    # T检验：Max Pain是否显著高于价格
    t_stat, p_value = stats.ttest_1samp(diff, 0)
    
    return {
        'data_points': len(mp_df),
        'mp_above_price': (diff > 0).sum(),
        'mp_above_pct': (diff > 0).mean() * 100,
        'avg_diff': diff.mean(),
        'avg_diff_pct': diff_pct.mean(),
        'median_diff_pct': diff_pct.median(),
        'std_diff_pct': diff_pct.std(),
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        't_stat': t_stat,
        't_test_p': p_value,
    }


def analyze_pcr_effectiveness(etf_stats_df):
    """
    分析PCR指标的有效性
    PCR作为逆向指标：PCR越高，后续反而可能上涨
    """
    pcr = etf_stats_df['PCR'].values
    returns_20d = etf_stats_df['20日涨跌'].values
    
    corr, p_val = stats.pearsonr(pcr, returns_20d)
    
    # 极端值分析
    low_pcr = etf_stats_df[etf_stats_df['PCR'] < 0.7]
    high_pcr = etf_stats_df[etf_stats_df['PCR'] > 1.0]
    
    return {
        'pcr_return_corr': corr,
        'pcr_return_p': p_val,
        'low_pcr_count': len(low_pcr),
        'high_pcr_count': len(high_pcr),
        'low_pcr_avg_return': low_pcr['20日涨跌'].mean() if len(low_pcr) > 0 else None,
        'high_pcr_avg_return': high_pcr['20日涨跌'].mean() if len(high_pcr) > 0 else None,
    }


def analyze_maxpain_deviation_effectiveness(etf_stats_df):
    """
    分析Max Pain偏离度的有效性
    偏离度作为均值回归指标
    """
    deviation = etf_stats_df['MaxPain偏离'].values
    returns_20d = etf_stats_df['20日涨跌'].values
    
    corr, p_val = stats.pearsonr(deviation, returns_20d)
    
    # 极端偏离分析
    high_dev = etf_stats_df[etf_stats_df['MaxPain偏离'] > 5]
    low_dev = etf_stats_df[etf_stats_df['MaxPain偏离'] < -2]
    
    return {
        'deviation_return_corr': corr,
        'deviation_return_p': p_val,
        'high_deviation_count': len(high_dev),
        'low_deviation_count': len(low_dev),
        'high_dev_avg_return': high_dev['20日涨跌'].mean() if len(high_dev) > 0 else None,
        'low_dev_avg_return': low_dev['20日涨跌'].mean() if len(low_dev) > 0 else None,
    }


def print_correlation_report(results):
    """打印相关性分析报告"""
    print("=" * 60)
    print("相关性分析报告")
    print("=" * 60)
    
    print("\n【1】Max Pain vs 价格相关性")
    print(f"  数据点: {results['data_points']}")
    print(f"  MaxPain>价格: {results['mp_above_pct']:.1f}%")
    print(f"  平均偏离: {results['avg_diff_pct']:.2f}%")
    print(f"  Pearson: {results['pearson_r']:.4f} (p={results['pearson_p']:.4f})")
    print(f"  Spearman: {results['spearman_r']:.4f} (p={results['spearman_p']:.4f})")
    print(f"  T检验: t={results['t_stat']:.4f}, p={results['t_test_p']:.6f}")
    
    print("\n【2】PCR有效性")
    pcr_res = results.get('pcr_analysis', {})
    if pcr_res:
        print(f"  PCR与收益相关性: {pcr_res['pcr_return_corr']:.4f}")
        print(f"  PCR<0.7的ETF平均收益: {pcr_res['low_pcr_avg_return']:.2f}%")
        print(f"  PCR>1.0的ETF平均收益: {pcr_res['high_pcr_avg_return']:.2f}%")
    
    print("\n【3】MaxPain偏离度有效性")
    dev_res = results.get('deviation_analysis', {})
    if dev_res:
        print(f"  偏离度与收益相关性: {dev_res['deviation_return_corr']:.4f}")
        print(f"  偏离>5%的ETF平均收益: {dev_res['high_dev_avg_return']:.2f}%")
        print(f"  偏离<-2%的ETF平均收益: {dev_res['low_dev_avg_return']:.2f}%")


if __name__ == "__main__":
    print("=" * 60)
    print("相关性分析模块")
    print("=" * 60)
    
    # 读取50ETF MaxPain历史数据（需提前准备）
    try:
        df = pd.read_csv('../data/sz50_max_pain_etf_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        print(f"\n[OK] 加载数据: {len(df)} 条")
        
        results = analyze_max_pain_price_correlation(df)
        print_correlation_report(results)
    except FileNotFoundError:
        print("\n[WARNING] 50ETF MaxPain数据不存在，请先运行数据收集模块")
