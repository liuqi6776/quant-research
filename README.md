# A股ETF期权Max Pain量化研究

## 项目简介

本项目系统研究了A股ETF期权Max Pain（最痛点）指标与ETF实际价格之间的相关性，综合分析了OI（持仓量）、PCR（Put/Call Ratio）和Max Pain三个核心期权指标，评估其作为ETF操作参考的有效性。

## 研究覆盖的ETF品种

| 交易所 | ETF名称 | 代码 |
|--------|---------|------|
| 上交所 | 上证50ETF | 510050 |
| 上交所 | 沪深300ETF | 510300 |
| 上交所 | 中证500ETF | 510500 |
| 上交所 | 科创50ETF | 588000 |
| 上交所 | 科创板50ETF | 588080 |
| 深交所 | 创业板ETF | 159915 |
| 深交所 | 深证100ETF | 159901 |
| 深交所 | 沪深300ETF | 159919 |
| 深交所 | 中证500ETF | 159922 |

## 核心研究结论

### 1. 指标相关性分析

| 指标组合 | 相关系数 | 解读 |
|----------|----------|------|
| PCR vs 20日涨跌 | +0.37 | 中度正相关，PCR作为逆向指标 |
| MaxPain偏离 vs 20日涨跌 | -0.40 | 中度负相关，均值回归特性 |
| 持仓量 vs 波动率 | +0.31 | 弱正相关 |

### 2. 各ETF当前综合评分（2025-06-11）

| ETF | 综合评分 | 信号 |
|-----|----------|------|
| 中证500ETF | +3 | 强烈看多 |
| 沪深300ETF | +2 | 轻度看多 |
| 科创50ETF | +2 | 轻度看多 |
| 创业板ETF | +1 | 轻度看多 |
| 深证100ETF | 0 | 中性 |
| 300ETF(深) | 0 | 中性 |
| 上证50ETF | -1 | 轻度看空 |
| 500ETF(深) | -1 | 轻度看空 |

### 3. 关键发现

- **PCR是有效的逆向指标**：PCR极低(<0.7)时警惕回调，PCR极高(>1.2)时关注反弹
- **MaxPain偏离>5%时有均值回归效应**：价格趋向MaxPain回归
- **需多指标综合**：单一指标胜率不足50%，多指标共振时胜率显著提升
- **只选流动性好的ETF**：OI>100万的品种价格发现更有效

## 项目文件结构

```
quant_research/
├── README.md                          # 本文件
├── code/
│   ├── 01_data_collection.py          # 数据获取
│   ├── 02_max_pain_calculation.py     # Max Pain计算
│   ├── 03_correlation_analysis.py     # 相关性分析
│   ├── 04_comprehensive_model.py      # 综合评分模型
│   └── 05_visualization.py            # 可视化
├── data/
│   ├── etf_50_price.csv               # 50ETF历史价格
│   ├── etf_300_price.csv              # 300ETF历史价格
│   ├── etf_500_price.csv              # 500ETF历史价格
│   ├── etf_kc50_price.csv             # 科创50ETF历史价格
│   ├── etf_cy_price.csv               # 创业板ETF历史价格
│   ├── hs300_price_2025.csv           # 沪深300指数价格
│   ├── hs300_max_pain_2025.csv        # 沪深300 MaxPain数据
│   ├── sz50_max_pain_etf_data.csv     # 上证50 MaxPain数据
│   ├── mu_price_2y.csv                # 美光科技股价
│   ├── mu_maxpain_analysis.csv        # MU MaxPain分析
│   ├── a50_all_index_maxpain.csv      # 三大股指期权MaxPain
│   ├── etf_option_comprehensive_analysis.csv  # ETF综合分析
│   └── etf_option_score_model.csv     # 评分模型结果
└── output/
    ├── hs300_max_pain_chart_hd.png    # 沪深300 MaxPain图表
    ├── sz50_max_pain_etf_chart.png    # 上证50 MaxPain图表
    ├── sz50_pct_change_chart.png      # 上证50百分比变化
    ├── a50_index_maxpain_structure.png # 三大股指期限结构
    ├── mu_final_analysis.png          # MU分析图表
    ├── etf50_maxpain_correlation.png  # 50ETF相关性分析
    ├── etf50_maxpain_final.png        # 50ETF最终分析
    ├── etf_option_dashboard.png       # ETF期权仪表盘
    └── xiaohongshu_cover.png          # 小红书封面图
```

## 环境依赖

```bash
pip install pandas numpy matplotlib scipy akshare requests
```

## 使用方法

1. 运行 `01_data_collection.py` 获取最新数据
2. 运行 `02_max_pain_calculation.py` 计算Max Pain
3. 运行 `03_correlation_analysis.py` 进行相关性分析
4. 运行 `04_comprehensive_model.py` 生成综合评分
5. 运行 `05_visualization.py` 生成可视化图表

## 免责声明

本研究仅供学习交流使用，不构成投资建议。期权交易风险极高，请根据自身情况独立判断。

## 作者

量化研究团队 | 2025年6月
