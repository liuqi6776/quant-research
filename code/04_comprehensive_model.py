#!/usr/bin/env python3
"""
04_comprehensive_model.py - 综合评分模型
基于PCR、MaxPain偏离度、OI构建ETF期权综合评分
"""

import pandas as pd
import numpy as np


def score_pcr(pcr):
    """
    PCR评分函数
    PCR偏低=看涨情绪重，PCR偏高=看跌情绪重（逆向指标）
    """
    if pcr < 0.7:
        return 2, "PCR<0.7，看涨过热，逆向看多"
    elif pcr < 0.85:
        return 1, "PCR偏低，轻度看涨"
    elif pcr < 1.0:
        return 0, "PCR中性"
    elif pcr < 1.2:
        return -1, "PCR偏高，轻度看跌"
    else:
        return -2, "PCR>1.2，看跌过重，逆向看空"


def score_max_pain(deviation):
    """
    Max Pain偏离度评分
    正偏离=高估（看空），负偏离=低估（看多）
    """
    if deviation > 5:
        return -2, f"高估{deviation:.1f}%，回调压力大"
    elif deviation > 2:
        return -1, f"高估{deviation:.1f}%，轻度压力"
    elif deviation > -2:
        return 0, "接近平价，平衡"
    elif deviation > -5:
        return 1, f"低估{abs(deviation):.1f}%，轻度支撑"
    else:
        return 2, f"低估{abs(deviation):.1f}%，反弹潜力大"


def score_oi(oi, threshold=1000000):
    """
    持仓量评分
    OI越大，流动性越好，指标越有效
    """
    if oi >= 1500000:
        return 1, f"OI{oi/10000:.0f}万，流动性极好"
    elif oi >= threshold:
        return 1, f"OI{oi/10000:.0f}万，流动性好"
    elif oi >= 500000:
        return 0, f"OI{oi/10000:.0f}万，流动性一般"
    else:
        return -1, f"OI{oi/10000:.0f}万，流动性差"


def calculate_composite_score(etf_data):
    """
    计算单个ETF的综合评分
    
    参数:
        etf_data: dict，包含PCR、MaxPain偏离、OI等指标
    
    返回:
        dict: 各维度评分和综合评分
    """
    pcr_score, pcr_comment = score_pcr(etf_data['PCR'])
    mp_score, mp_comment = score_max_pain(etf_data['MaxPain偏离'])
    oi_score, oi_comment = score_oi(etf_data['OI'])
    
    total_score = pcr_score + mp_score + oi_score
    
    # 信号判断
    if total_score >= 3:
        signal = "强烈看多"
    elif total_score >= 1:
        signal = "轻度看多"
    elif total_score == 0:
        signal = "中性"
    elif total_score >= -2:
        signal = "轻度看空"
    else:
        signal = "强烈看空"
    
    return {
        'ETF': etf_data['ETF名称'],
        '代码': etf_data['代码'],
        'PCR评分': pcr_score,
        'PCR解读': pcr_comment,
        'MaxPain评分': mp_score,
        'MaxPain解读': mp_comment,
        'OI评分': oi_score,
        'OI解读': oi_comment,
        '总分': total_score,
        '信号': signal,
    }


def batch_score(etf_list):
    """
    批量计算多个ETF的评分
    
    参数:
        etf_list: list of dict，每个dict包含一只ETF的指标
    
    返回:
        DataFrame: 评分结果
    """
    results = []
    for etf in etf_list:
        results.append(calculate_composite_score(etf))
    
    return pd.DataFrame(results)


# ========== 2025-06-11 数据快照 ==========

ETF_SNAPSHOT_20250611 = [
    {'ETF名称': '上证50ETF', '代码': '510050', '最新价': 2.735, '20日涨跌': 2.15, '波动率': 9.35, 'OI': 1383607, 'PCR': 0.866, 'MaxPain': 2.90, 'MaxPain偏离': 6.03},
    {'ETF名称': '沪深300ETF', '代码': '510300', '最新价': 3.881, '20日涨跌': 2.91, '波动率': 9.57, 'OI': 1186747, 'PCR': 0.799, 'MaxPain': 3.85, 'MaxPain偏离': -0.80},
    {'ETF名称': '中证500ETF', '代码': '510500', '最新价': 5.919, '20日涨跌': 4.56, '波动率': 12.35, 'OI': 1232457, 'PCR': 0.794, 'MaxPain': 5.80, 'MaxPain偏离': -2.01},
    {'ETF名称': '科创50ETF', '代码': '588000', '最新价': 1.056, '20日涨跌': 2.13, '波动率': 15.02, 'OI': 1511938, 'PCR': 0.666, 'MaxPain': 1.10, 'MaxPain偏离': 4.17},
    {'ETF名称': '创业板ETF', '代码': '159915', '最新价': 2.133, '20日涨跌': 7.89, '波动率': 18.75, 'OI': 1262960, 'PCR': 0.942, 'MaxPain': 2.15, 'MaxPain偏离': 0.80},
    {'ETF名称': '深证100ETF', '代码': '159901', '最新价': 2.850, '20日涨跌': 3.20, '波动率': 11.20, 'OI': 104850, 'PCR': 0.895, 'MaxPain': 2.90, 'MaxPain偏离': 1.75},
    {'ETF名称': '沪深300ETF(深)', '代码': '159919', '最新价': 3.920, '20日涨跌': 2.80, '波动率': 9.80, 'OI': 212902, 'PCR': 0.982, 'MaxPain': 3.90, 'MaxPain偏离': -0.51},
    {'ETF名称': '中证500ETF(深)', '代码': '159922', '最新价': 5.750, '20日涨跌': 4.30, '波动率': 12.80, 'OI': 295057, 'PCR': 1.070, 'MaxPain': 5.65, 'MaxPain偏离': -1.74},
]


if __name__ == "__main__":
    print("=" * 60)
    print("ETF期权综合评分模型")
    print("=" * 60)
    
    # 计算评分
    scores_df = batch_score(ETF_SNAPSHOT_20250611)
    
    # 排序
    scores_df = scores_df.sort_values('总分', ascending=False)
    
    # 打印摘要
    print("\n=== 评分排名 ===")
    print(scores_df[['ETF', '代码', 'PCR评分', 'MaxPain评分', 'OI评分', '总分', '信号']].to_string(index=False))
    
    # 保存
    output_path = '../data/etf_option_score_model.csv'
    scores_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n[OK] 评分结果已保存: {output_path}")
