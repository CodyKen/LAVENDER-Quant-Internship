import polars as pl
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

class FactorAnalysis:
    # 定义不可使用的因子名称列表
    disallowed_names = [
        "symbol", "open_time", "sample_ref_return", "quantile_n", "quantile_1_minus_n", "factor_n",
        "factor_1_minus_n", "new_ret_long", "new_ret_short", "new_ret_LSA", "new_ret_SSA", "bench_return",
        "long_fee", "short_fee", "bench_fee", "long_short", "long_bench", "bench_long", "short_long",
        "short_bench", "bench_short", "long_cum", "short_cum", "bench_cum", "long_short_cum", "long_bench_cum",
        "bench_long_cum", "short_long_cum", "short_bench_cum", "bench_short_cum"
    ] + [f"quantile_{i}" for i in range(11)] + ["in_range", "range_return"] + [f"ret_sum_avg_{i+1}" for i in range(10)] + [f"group_diff_return_{i}" for i in range(10)]

    def __init__(self, factors, result_hour, commission=0.25 / 10000.0):
        """
        初始化因子分析类

        参数:
        factors (DataFrame): 因子数据
        result_hour (DataFrame): 每小时的结果数据
        commission (float): 交易佣金比例，默认为0.25个基点
        """
        self.factors = factors
        self.result_hour = result_hour
        self.commission = commission
        self.processed_factors = None
        self.ans_df = None
        self.result_df = None
        self.factor_name = [name for name in factors.columns if name not in ["symbol", "open_time"]][0]

        # 检查因子名称是否与禁止列表中的任何名称冲突
        if self.factor_name in self.disallowed_names:
            raise ValueError(f"因子名称 '{self.factor_name}' 不允许使用。因子名称不能与以下名称之一冲突：\n{self.disallowed_names}")


    def preprocess_data(self):
        """
        预处理数据
        将结果数据中的收盘价计算出收益率，并将其与因子数据合并
        """
        # 提取收盘价并按时间和符号排序
        close = self.result_hour.select(["symbol", "open_time", "close"]).sort("open_time").sort("symbol")
        # 计算每个符号的参考收益率
        f1 = (pl.col('close').shift(-1) / pl.col('close') - 1).over("symbol").alias("sample_ref_return")
        ret = close.select(pl.col(["symbol", 'open_time']), f1)
        
        # 将参考收益率与因子数据合并
        self.factors = self.factors.join(ret, on=["symbol", "open_time"], how="inner").sort("open_time")

    def calculate_quantiles(self):
        """
        计算因子的分位数并生成新列
        """
        n = 0.5 # 中位数
        self.factors_lazy = self.factors.lazy()

        # 按时间分组计算因子的中位数和1减中位数
        quantiles_lazy = self.factors_lazy.group_by("open_time").agg([
            pl.col(self.factor_name).quantile(n, 'linear').alias("quantile_n"),
            pl.col(self.factor_name).quantile(1 - n, 'linear').alias("quantile_1_minus_n")
        ]).sort("open_time")

        # 创建新列，标识因子值大于中位数和小于1减中位数的样本
        f1 = pl.when(pl.col(self.factor_name) > pl.col("quantile_n")).then(1).otherwise(0).alias("factor_n")
        f2 = pl.when(pl.col(self.factor_name) < pl.col("quantile_1_minus_n")).then(1).otherwise(0).alias("factor_1_minus_n")

        # 将新列添加到因子数据
        self.factors_lazy = self.factors_lazy.join(quantiles_lazy, on="open_time", how="inner")
        self.factors_lazy = self.factors_lazy.with_columns(f1, f2).sort("open_time")

        # 计算每个样本的长短期收益
        self.factors_lazy = self.factors_lazy.with_columns((pl.col("factor_n") * pl.col("sample_ref_return")).alias("new_ret_long")).fill_null(0)
        self.factors_lazy = self.factors_lazy.with_columns((pl.col("factor_1_minus_n") * pl.col("sample_ref_return")).alias("new_ret_short")).fill_null(0)

    def calculate_returns(self):
        """
        计算多种收益指标并生成结果数据框
        """
        # 按时间分组计算新 return
        f1 = pl.col("new_ret_long").sum()
        f2 = pl.col("factor_n").sum()
        f3 = pl.col("factor_1_minus_n").sum()
        f4 = pl.mean("sample_ref_return")
        f5 = pl.col("new_ret_short").sum()


        LSA_lazy = self.factors_lazy.group_by("open_time").agg((f1/f2).alias("new_ret_LSA")).sort("open_time").fill_nan(0).fill_null(0)
        SSA_lazy = self.factors_lazy.group_by("open_time").agg((f5/f3).alias("new_ret_SSA")).sort("open_time").fill_nan(0).fill_null(0)
        BR_lazy = self.factors_lazy.group_by("open_time").agg(f4.alias("bench_return")).sort("open_time").fill_nan(0).fill_null(0)

        # 将多种收益率合并
        ans_df_lazy = LSA_lazy.join(SSA_lazy, on="open_time", how="inner")
        ans_df_lazy = ans_df_lazy.join(BR_lazy, on="open_time", how="inner")

        # 考虑交易佣金，调整收益率
        ans_df_lazy = ans_df_lazy.with_columns((pl.col("new_ret_LSA") - 2 * self.commission).alias("long_fee"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col("new_ret_SSA") - 2 * self.commission).alias("short_fee"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col("bench_return") - 2 * self.commission).alias("bench_fee"))

        # 计算多种策略的组合收益
        ans_df_lazy = ans_df_lazy.with_columns((pl.col('new_ret_LSA') - pl.col('new_ret_SSA') - 2 * self.commission).alias("long_short"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col('new_ret_LSA') - pl.col('bench_return') - 2 * self.commission).alias("long_bench"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col('bench_return') - pl.col('new_ret_LSA') - 2 * self.commission).alias("bench_long"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col('new_ret_SSA') - pl.col('new_ret_LSA') - 2 * self.commission).alias("short_long"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col('new_ret_SSA') - pl.col('bench_return') - 2 * self.commission).alias("short_bench"))
        ans_df_lazy = ans_df_lazy.with_columns((pl.col('bench_return') - pl.col('new_ret_SSA') - 2 * self.commission).alias("bench_short"))

        self.ans_df = ans_df_lazy.collect()

        # 计算累积收益
        self.ans_df = self.ans_df.with_columns(pl.col('long_fee').cumsum().alias("long_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('short_fee').cumsum().alias("short_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('bench_fee').cumsum().alias("bench_cum"))

        self.ans_df = self.ans_df.with_columns(pl.col('long_short').cumsum().alias("long_short_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('long_bench').cumsum().alias("long_bench_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('bench_long').cumsum().alias("bench_long_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('short_long').cumsum().alias("short_long_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('short_bench').cumsum().alias("short_bench_cum"))
        self.ans_df = self.ans_df.with_columns(pl.col('bench_short').cumsum().alias("bench_short_cum"))

    def plot_cumulative_returns(self):
        """
        绘制累积收益曲线
        """
        # 绘制长策略、短策略和基准策略的累积收益
        plt.figure(figsize=(10, 6))
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["long_cum"].to_list(), label='long', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["short_cum"].to_list(), label='short', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["bench_cum"].to_list(), label='benchmark', linewidth=2, color="gray")

        plt.title("Accumulate Long")
        plt.xlabel("Open Time")
        plt.ylabel("Long Cumulative")
        plt.legend()
        plt.show()

        # 绘制六种策略的累积收益
        plt.figure(figsize=(10, 6))
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["long_short_cum"].to_list(), label='long_short', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["long_bench_cum"].to_list(), label='long_bench', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["bench_short_cum"].to_list(), label='bench_short', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["bench_long_cum"].to_list(), label='bench_long', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["short_long_cum"].to_list(), label='short_long', linewidth=1)
        plt.plot(self.ans_df["open_time"].to_list(), self.ans_df["short_bench_cum"].to_list(), label='short_bench', linewidth=1)

        plt.title("Accumulate Returns of Six Strategies")
        plt.legend()
        plt.show()

    def factor_stats(self, n, pnl):
        """
        计算并打印因子的统计指标

        参数:
        n (int): 每年的时间单位数
        S (Series): 收益率数据
        """
        net_value = pnl.cum_sum() + 1.0
        sharpe = n ** 0.5 * pnl.mean() / pnl.std()
        ann_return = n * pnl.mean()
        maxdd = (-(net_value / net_value.cum_max() - 1)).max()
        calmar_ratio = ann_return / maxdd

        print("ann_return =", round(ann_return, 4), end='  ')
        print("sharpe =", round(sharpe, 4), end='  ')
        print("maxdd =", round(maxdd, 4), end='  ')
        print("calmar_ratio =", round(calmar_ratio, 4), end='  ')

    def calculate_factor_stats(self):
        """
        计算并打印多种策略的统计数据
        """
        # 获取多种策略的收益率序列
        long_fee_series = pl.Series(self.ans_df['long_fee'])
        short_fee_series = pl.Series(self.ans_df['short_fee'])
        bench_fee_series = pl.Series(self.ans_df['bench_fee'])

        long_short_fee_series = pl.Series(self.ans_df['long_short'])
        long_bench_fee_series = pl.Series(self.ans_df['long_bench'])
        bench_long_fee_series = pl.Series(self.ans_df['bench_long'])
        short_long_fee_series = pl.Series(self.ans_df['short_long'])
        short_bench_fee_series = pl.Series(self.ans_df['short_bench'])
        bench_short_fee_series = pl.Series(self.ans_df['bench_short'])

        n = 365 * 24

        print("long: ")
        self.factor_stats(n, long_fee_series)
        print("\n")
        print("short: ")
        self.factor_stats(n, short_fee_series)
        print("\n")
        print("bench: ")
        self.factor_stats(n, bench_fee_series)
        print("\n")

        print("long_short: ")
        self.factor_stats(n, long_short_fee_series)
        print("\n")
        print("long_bench: ")
        self.factor_stats(n, long_bench_fee_series)
        print("\n")
        print("bench_long: ")
        self.factor_stats(n, bench_long_fee_series)
        print("\n")
        print("short_long: ")
        self.factor_stats(n, short_long_fee_series)
        print("\n")
        print("short_bench: ")
        self.factor_stats(n, short_bench_fee_series)
        print("\n")
        print("bench_short: ")
        self.factor_stats(n, bench_short_fee_series)
        print("\n")
        

    def calculate_10_group_returns(self):
        """
        计算因子的10组分位数收益
        """
        quantiles_10 = []
        for i in range(11):
            # 计算每组的分位数
            quantiles_10.append(self.factors.group_by("open_time").agg(
                pl.col(self.factor_name).quantile(i / 10, 'linear').alias(f"quantile_{i}")
            ).sort("open_time"))

        # 将各组分位数合并到
        quantiles_10_df = quantiles_10[0]
        for i in range(1, 11):
            quantiles_10_df = quantiles_10_df.join(quantiles_10[i], on="open_time", how="inner")

        for i in range(10):
            lower_quantile = f"quantile_{i}"
            upper_quantile = f"quantile_{i + 1}"

            # 筛选因子值在当前分位数范围内的数据
            factors_in_range = self.factors.join(quantiles_10_df, on="open_time", how='inner').with_columns(
                ((pl.col(self.factor_name) >= pl.col(lower_quantile)) & (pl.col(self.factor_name) <= pl.col(upper_quantile))).alias("in_range")
            ).with_columns(
                (pl.col("in_range") * pl.col("sample_ref_return")).alias("range_return")
            )

            # 计算当前分位数范围内的平均收益
            ret_sum_avg = factors_in_range.group_by("open_time").agg(
                (pl.sum("range_return") / pl.sum("in_range")).alias(f"ret_sum_avg_{i+1}")
            )

            # 调整收益率以考虑交易佣金
            ret_sum_avg = ret_sum_avg.with_columns(
                (pl.col(f"ret_sum_avg_{i+1}") - 2 * self.commission).alias(f"ret_sum_avg_{i+1}")
            )

            # 将当前分位数的收益合并到分位数数据框中
            quantiles_10_df = quantiles_10_df.join(ret_sum_avg, on="open_time", how="inner")

        # 填充缺失值和空值
        quantiles_10_df = quantiles_10_df.sort("open_time").fill_nan(0).fill_null(0)

        # 计算基准收益
        BR = self.factors_lazy.group_by("open_time").agg(pl.mean("sample_ref_return").alias("bench_return")).sort("open_time").fill_nan(0).fill_null(0).collect()

        # 将基准收益与分位数数据合并
        self.result_df = quantiles_10_df.join(BR, on="open_time", how="inner")

        # 计算每组分位数的超额收益
        for i in range(1, 11):
            self.result_df = self.result_df.with_columns(
                (
                    (pl.col(f"ret_sum_avg_{i}") - pl.col("bench_return"))
                ).alias(f"group_diff_return_{i}")
            )

        # 填充缺失值和空值
        self.result_df = self.result_df.fill_nan(0).fill_null(0)

    def plot_10_group_returns(self):
        """
        绘制10组分位数的累积收益和差异收益
        """
        open_time = self.result_df["open_time"]

        plt.figure(figsize=(10, 6))
        plt.title("10 Group Accumulate Return")

        # 绘制每组分位数的累积收益
        for i in range(1, 11):
            cumulative_return = self.result_df[f"ret_sum_avg_{i}"].cumsum()
            plt.plot(open_time, cumulative_return, label=f"group_{i}", linewidth=1)
        plt.plot(open_time, self.ans_df["bench_fee"].cumsum(), label=f"bench_return", linewidth=2, color="gray")

        plt.legend()
        plt.show()

        plt.figure(figsize=(10, 6))
        plt.title("10 Group Difference Return")

        # 绘制每组分位数的差异收益
        for i in range(1, 11):
            cumulative_return = self.result_df[f"group_diff_return_{i}"].cumsum()
            plt.plot(open_time, cumulative_return, label=f"group_{i}", linewidth=1)

        plt.legend()
        plt.show()

    def calculate_group_stats(self):
        """
        计算并打印10组分位数的统计数据
        """
        n = 365 * 24

        # 打印每组分位数的统计数据
        for i in range(1, 11):
            print(f"group_{i}: ")
            self.factor_stats(n, pl.Series(self.result_df[f"ret_sum_avg_{i}"]))
            print("\n")

        print('-----------------------------------------')

        # 打印每组分位数与基准收益差异的统计数据
        for i in range(1, 11):
            print(f"group_difference_{i}: ")
            self.factor_stats(n, pl.Series(self.result_df[f"group_diff_return_{i}"]))
            print("\n")

    def run_full_analysis(self):
        """
        运行完整的分析流程
        """
        self.preprocess_data() # 预处理数据
        self.calculate_quantiles() # 计算分位数
        self.calculate_returns() # 计算收益
        self.plot_cumulative_returns() # 绘制累积收益曲线
        self.calculate_factor_stats() # 计算因子统计数据
        self.calculate_10_group_returns() # 计算10组分位数收益
        self.plot_10_group_returns() # 绘制10组分位数收益曲线
        self.calculate_group_stats() # 计算10组分位数统计数据

