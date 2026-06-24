#!/usr/bin/env python3
"""
05_visualization.py - 可视化模块
生成研究所需的各类图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


def plot_price_vs_maxpain(price_df, mp_df, title, output_path, 
                          price_col='close', date_col='time',
                          figsize=(18, 10)):
    """
    绘制ETF价格与Max Pain对比图
    
    参数:
        price_df: ETF价格DataFrame
        mp_df: Max Pain数据DataFrame
        title: 图表标题
        output_path: 输出路径
    """
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # 价格线
    ax1.fill_between(price_df[date_col], price_df[price_col], alpha=0.08, color='#2E86C1')
    ax1.plot(price_df[date_col], price_df[price_col], color='#2E86C1', 
             linewidth=1.8, label='ETF Price')
    ax1.set_ylabel('ETF Price', color='#2E86C1', fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#2E86C1')
    
    # Max Pain散点
    ax2 = ax1.twinx()
    ax2.scatter(mp_df['date'], mp_df['max_pain'], color='#E74C3C', s=100, 
                zorder=5, label='Max Pain', edgecolors='white', linewidths=1.5)
    ax2.plot(mp_df['date'], mp_df['max_pain'], color='#E74C3C', 
             linewidth=1.5, linestyle='--', alpha=0.6)
    ax2.set_ylabel('Max Pain', color='#E74C3C', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#E74C3C')
    
    # 标注
    for _, row in mp_df.iterrows():
        ax2.annotate(f'{row["max_pain"]:.0f}', 
                    xy=(row['date'], row['max_pain']),
                    xytext=(0, 12), textcoords='offset points',
                    ha='center', fontsize=9, color='#C0392B', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FADBD8', 
                             edgecolor='#E74C3C', alpha=0.8))
    
    ax1.set_title(title, fontsize=15, fontweight='bold', pad=20)
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45, ha='right')
    ax1.grid(True, alpha=0.15, linestyle='--')
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', 
               fontsize=11, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] 图表已保存: {output_path}")


def plot_dashboard(analysis_df, score_df, output_path, figsize=(20, 16)):
    """
    绘制ETF期权综合分析仪表盘
    
    参数:
        analysis_df: 综合分析数据
        score_df: 评分结果
        output_path: 输出路径
    """
    fig = plt.figure(figsize=figsize)
    
    # 1. PCR vs 收益气泡图
    ax1 = plt.subplot(2, 2, 1)
    scatter = ax1.scatter(analysis_df['PCR'], analysis_df['20日涨跌'],
                          s=analysis_df['持仓量(OI)']/5000,
                          c=analysis_df['MaxPain偏离'], cmap='RdYlGn',
                          alpha=0.7, edgecolors='black', linewidth=1)
    ax1.axvline(x=0.85, color='gray', linestyle='--', alpha=0.5)
    ax1.axvline(x=1.0, color='red', linestyle='--', alpha=0.5)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    for _, row in analysis_df.iterrows():
        ax1.annotate(row['ETF名称'], (row['PCR'], row['20日涨跌']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    ax1.set_xlabel('PCR', fontsize=12)
    ax1.set_ylabel('20-Day Return (%)', fontsize=12)
    ax1.set_title('PCR vs Return (Bubble=OI)', fontsize=13, fontweight='bold')
    plt.colorbar(scatter, ax=ax1, label='MaxPain Dev (%)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Max Pain偏离度
    ax2 = plt.subplot(2, 2, 2)
    colors = ['#27AE60' if x < 0 else '#E74C3C' for x in analysis_df['MaxPain偏离']]
    ax2.barh(analysis_df['ETF名称'], analysis_df['MaxPain偏离'], 
             color=colors, alpha=0.8, edgecolor='white')
    ax2.axvline(x=0, color='black', linewidth=0.8)
    ax2.set_xlabel('MaxPain Deviation (%)', fontsize=12)
    ax2.set_title('MaxPain Deviation by ETF', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 3. 综合评分排名
    ax3 = plt.subplot(2, 2, 3)
    sorted_scores = score_df.sort_values('总分', ascending=True)
    colors_bar = ['#27AE60' if x > 0 else '#E74C3C' if x < 0 else '#F39C12' 
                  for x in sorted_scores['总分']]
    ax3.barh(sorted_scores['ETF'], sorted_scores['总分'], 
             color=colors_bar, alpha=0.8, edgecolor='white')
    ax3.axvline(x=0, color='black', linewidth=0.8)
    ax3.set_xlabel('Score', fontsize=12)
    ax3.set_title('Composite Score Ranking', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 4. 关键结论文本
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    conclusions = (
        "Key Findings\n"
        "=" * 35 + "\n\n"
        "1. MaxPain > Price: 100% of time\n"
        f"2. Avg deviation: +5.31%\n"
        f"3. Spearman corr: 0.944\n"
        f"4. PCR contrarian: +0.37 corr\n\n"
        "Best Signals:\n"
        "  PCR < 0.7 or > 1.2\n"
        "  MaxPain dev > 5%\n"
        "  High OI (>1M)"
    )
    ax4.text(0.1, 0.95, conclusions, transform=ax4.transAxes, fontsize=12,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#f8f9fa', 
                     edgecolor='#dee2e6', alpha=0.95))
    
    plt.suptitle('ETF Option Indicator Dashboard', fontsize=16, 
                fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] 仪表盘已保存: {output_path}")


def plot_mu_analysis(mu_price_df, mp_data, output_path, figsize=(20, 14)):
    """
    绘制MU（美光科技）Max Pain分析图
    
    参数:
        mu_price_df: MU历史价格
        mp_data: Max Pain期限结构数据
        output_path: 输出路径
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize, 
                            gridspec_kw={'height_ratios': [3, 1]})
    
    ax1 = axes[0]
    ax1_twin = ax1.twinx()
    
    ax1.fill_between(mu_price_df['Date'], mu_price_df['Close'], 
                     alpha=0.08, color='#2E86C1')
    ax1.plot(mu_price_df['Date'], mu_price_df['Close'], 
             color='#2E86C1', linewidth=1.8, label='MU Price')
    ax1.set_ylabel('MU Price (USD)', color='#2E86C1', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#2E86C1')
    
    mp_df = pd.DataFrame(mp_data)
    mp_df['expiry_date'] = pd.to_datetime(mp_df['expiry'])
    
    ax1_twin.scatter(mp_df['expiry_date'], mp_df['max_pain'],
                     color='#E74C3C', s=100, zorder=5, label='Max Pain')
    ax1_twin.plot(mp_df['expiry_date'], mp_df['max_pain'],
                  color='#E74C3C', linewidth=1.5, linestyle='--', alpha=0.6)
    ax1_twin.set_ylabel('Max Pain (USD)', color='#E74C3C', fontsize=12)
    ax1_twin.tick_params(axis='y', labelcolor='#E74C3C')
    
    ax1.set_title('MU Price vs Max Pain Term Structure', 
                  fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.15, linestyle='--')
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
    
    # 偏离度图
    ax2 = axes[1]
    mu_current = 891.88
    mp_df['deviation'] = (mp_df['max_pain'] / mu_current - 1) * 100
    colors = ['#27AE60' if x > 0 else '#E74C3C' for x in mp_df['deviation']]
    ax2.bar(range(len(mp_df)), mp_df['deviation'], color=colors, 
            alpha=0.7, edgecolor='white')
    ax2.set_ylabel('Deviation (%)', fontsize=11)
    ax2.set_title('Max Pain Deviation from Current Price', fontsize=13)
    ax2.axhline(y=0, color='black', linewidth=0.8)
    ax2.grid(True, alpha=0.15, linestyle='--', axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] MU分析图已保存: {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("可视化模块")
    print("=" * 60)
    
    # 示例：生成仪表盘
    try:
        analysis_df = pd.read_csv('../data/etf_option_comprehensive_analysis.csv')
        score_df = pd.read_csv('../data/etf_option_score_model.csv')
        plot_dashboard(analysis_df, score_df, '../output/etf_option_dashboard.png')
        print("\n[COMPLETE] 所有图表生成完成!")
    except FileNotFoundError as e:
        print(f"\n[WARNING] 数据文件不存在: {e}")
