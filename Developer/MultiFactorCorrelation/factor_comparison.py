import polars as pl
import numpy as np
from scipy.stats import spearmanr, kendalltau
from minepy import MINE

class FactorCorrelation:
    def __init__(self, factors_dict):
        """
        初始化方法
        :param factors_dict: 包含所有因子的字典，键为因子名称，值为因子数据的DataFrame
        """
        self.factors_dict = factors_dict
        self.factor_names = list(factors_dict.keys())
        self.aligned_factors = self.align_factors()
    
    def align_factors(self):
        """
        对齐所有因子数据
        :return: 对齐后的因子数据
        """
        aligned_factors = None
        for i, (name, df) in enumerate(self.factors_dict.items()):
            value_col = [col for col in df.columns if col not in ["open_time", "symbol"]][0]
            df = df.rename({value_col: f"factor{i + 1}"})
            if aligned_factors is None:
                aligned_factors = df
            else:
                aligned_factors = aligned_factors.join(df, on=["open_time", "symbol"], how="inner")
        return aligned_factors
    
    def compute_correlation_per_time(self, correlation_func):
        """
        按时间截面计算相关性并返回所有时间截面上的均值
        :param correlation_func: 相关性计算函数（Spearman, Kendall, etc.）
        :return: 所有时间截面相关性的均值
        """
        time_points = self.aligned_factors["open_time"].unique().to_list()  # 获取所有时间点
        correlations = []

        for time in time_points:
            # 获取当前时间点的所有数据
            time_data = self.aligned_factors.filter(pl.col("open_time") == time)
            
            # 计算当前时间点的相关性矩阵
            correlation_matrix = correlation_func(time_data)
            correlations.append(correlation_matrix)

        # 计算所有时间截面上相关性的均值
        mean_correlations = np.nanmean(correlations, axis=0)
        return mean_correlations

    def compute_spearman(self, time_data=None):
        """
        计算Spearman相关性矩阵，支持按时间截面计算
        :param time_data: 可选，指定特定时间的数据，默认为None
        :return: Spearman相关性矩阵
        """
        if time_data is None:
            time_data = self.aligned_factors
        
        n = len(self.factor_names)
        spearman_matrix = np.full((n, n), np.nan)

        for i in range(1, n):
            factor_i = f"factor{i + 1}"
            for j in range(i):
                factor_j = f"factor{j + 1}"
                valid_data = time_data.select([factor_i, factor_j]).drop_nulls()
                factor_i_values = valid_data[factor_i].to_numpy()
                factor_j_values = valid_data[factor_j].to_numpy()
                spearman_corr, _ = spearmanr(factor_i_values, factor_j_values)
                spearman_matrix[i, j] = spearman_corr

        return spearman_matrix
    
    def compute_kendall(self, time_data=None):
        """
        计算Kendall Tau相关性矩阵，支持按时间截面计算
        :param time_data: 可选，指定特定时间的数据，默认为None
        :return: Kendall Tau相关性矩阵
        """
        if time_data is None:
            time_data = self.aligned_factors

        n = len(self.factor_names)
        kendall_matrix = np.full((n, n), np.nan)

        for i in range(1, n):
            factor_i = f"factor{i + 1}"
            for j in range(i):
                factor_j = f"factor{j + 1}"
                valid_data = time_data.select([factor_i, factor_j]).drop_nulls()
                factor_i_values = valid_data[factor_i].to_numpy()
                factor_j_values = valid_data[factor_j].to_numpy()
                kendall_corr, _ = kendalltau(factor_i_values, factor_j_values)
                kendall_matrix[i, j] = kendall_corr

        return kendall_matrix
    
    def compute_mine(self, time_data=None):
        """
        计算MINE相关性矩阵，支持按时间截面计算
        :param time_data: 可选，指定特定时间的数据，默认为None
        :return: MINE相关性矩阵
        """
        if time_data is None:
            time_data = self.aligned_factors
        
        n = len(self.factor_names)
        mine_matrix = np.full((n, n), np.nan)
        mine = MINE()

        for i in range(1, n):
            factor_i = f"factor{i + 1}"
            for j in range(i):
                factor_j = f"factor{j + 1}"
                valid_data = time_data.select([factor_i, factor_j]).drop_nulls()
                factor_i_values = valid_data[factor_i].to_numpy()
                factor_j_values = valid_data[factor_j].to_numpy()
                mine.compute_score(factor_i_values, factor_j_values)
                mine_corr = mine.mic()
                mine_matrix[i, j] = mine_corr

        return mine_matrix

    def compute_all(self, correlations=["spearman", "kendall", "mine"]):
        """
        计算所有相关性并打印结果，按时间截面计算后取均值
        :param correlations: 选择需要计算和打印的相关系数，可以为("spearman", "kendall", "mine")的任意组合
        """
        correlation_mapping = {
            "spearman": self.compute_spearman,
            "kendall": self.compute_kendall,
            "mine": self.compute_mine
        }

        for corr in correlations:
            if corr in correlation_mapping:
                mean_corr = self.compute_correlation_per_time(correlation_mapping[corr])
                print(f"\n{corr.capitalize()}相关性均值：")
                print(mean_corr)
    
    def split(self, date_time):
        """
        以时间 time_list 为界限将 aligned_factors 分为两部分并返回
        :param time_list: [年, 月, 日, 时, 分, 秒] 的时间格式列表
        :return: 全部表格、时间 time_list 之前的表格、时间 time_list 之后的表格
        """
        ans = self.aligned_factors.sort("open_time")
        before_date_df = ans.filter(pl.col('open_time') <= date_time)
        after_date_df = ans.filter(pl.col('open_time') > date_time)

        return ans, before_date_df, after_date_df



# Below is the old version, which calculates the correlation directly without calculating it per time.


# import polars as pl
# import numpy as np
# from scipy.stats import spearmanr, kendalltau
# from minepy import MINE

# class FactorCorrelation:
#     def __init__(self, factors_dict):
#         """
#         初始化方法
#         :param factors_dict: 包含所有因子的字典，键为因子名称，值为因子数据的DataFrame
#         """
#         self.factors_dict = factors_dict
#         self.factor_names = list(factors_dict.keys())
#         self.aligned_factors = self.align_factors()
    
#     def align_factors(self):
#         """
#         对齐所有因子数据
#         :return: 对齐后的因子数据
#         """
#         aligned_factors = None
#         for i, (name, df) in enumerate(self.factors_dict.items()):
#             value_col = [col for col in df.columns if col not in ["open_time", "symbol"]][0]
#             df = df.rename({value_col: f"factor{i + 1}"})
#             if aligned_factors is None:
#                 aligned_factors = df
#             else:
#                 aligned_factors = aligned_factors.join(df, on=["open_time", "symbol"], how="inner")
#         return aligned_factors
    
#     def compute_spearman(self):
#         """
#         计算Spearman相关性矩阵
#         :return: Spearman相关性矩阵
#         """
#         n = len(self.factor_names)
#         spearman_matrix = np.full((n, n), np.nan)

#         for i in range(1, n):
#             factor_i = f"factor{i + 1}"
#             for j in range(i):
#                 factor_j = f"factor{j + 1}"
#                 valid_data = self.aligned_factors.select([factor_i, factor_j]).drop_nulls()
#                 factor_i_values = valid_data[factor_i].to_numpy()
#                 factor_j_values = valid_data[factor_j].to_numpy()
#                 spearman_corr, _ = spearmanr(factor_i_values, factor_j_values)
#                 spearman_matrix[i, j] = spearman_corr

#         spearman_df = pl.DataFrame(spearman_matrix)
#         spearman_df.columns = self.factor_names
#         spearman_df.insert_column(0, pl.Series('factor', self.factor_names))
#         return spearman_df
    
#     def compute_ic(self):
#         """
#         计算IC相关性矩阵（使用Spearman相关性）
#         :return: IC相关性矩阵
#         """
#         return self.compute_spearman()

#     def compute_mine(self):
#         """
#         计算MINE相关性矩阵
#         :return: MINE相关性矩阵
#         """
#         n = len(self.factor_names)
#         mine_matrix = np.full((n, n), np.nan)
#         mine = MINE()

#         for i in range(1, n):
#             factor_i = f"factor{i + 1}"
#             for j in range(i):
#                 factor_j = f"factor{j + 1}"
#                 valid_data = self.aligned_factors.select([factor_i, factor_j]).drop_nulls()
#                 factor_i_values = valid_data[factor_i].to_numpy()
#                 factor_j_values = valid_data[factor_j].to_numpy()
#                 mine.compute_score(factor_i_values, factor_j_values)
#                 mine_corr = mine.mic()
#                 mine_matrix[i, j] = mine_corr

#         mine_df = pl.DataFrame(mine_matrix)
#         mine_df.columns = self.factor_names
#         mine_df.insert_at_idx(0, pl.Series('factor', self.factor_names))
#         return mine_df
    
#     def compute_kendall(self):
#         """
#         计算Kendall Tau相关性矩阵
#         :return: Kendall Tau相关性矩阵
#         """
#         n = len(self.factor_names)
#         kendall_matrix = np.full((n, n), np.nan)

#         for i in range(1, n):
#             factor_i = f"factor{i + 1}"
#             for j in range(i):
#                 factor_j = f"factor{j + 1}"
#                 valid_data = self.aligned_factors.select([factor_i, factor_j]).drop_nulls()
#                 factor_i_values = valid_data[factor_i].to_numpy()
#                 factor_j_values = valid_data[factor_j].to_numpy()
#                 kendall_corr, _ = kendalltau(factor_i_values, factor_j_values)
#                 kendall_matrix[i, j] = kendall_corr

#         kendall_df = pl.DataFrame(kendall_matrix)
#         kendall_df.columns = self.factor_names
#         kendall_df.insert_at_idx(0, pl.Series('factor', self.factor_names))
#         return kendall_df
    
#     def get_max_value_and_column(self, dataframe):
#         """
#         获取每一行的最大值及其列名，忽略None值
#         :param dataframe: 输入的DataFrame
#         :return: 每一行的最大值及其列名
#         """
#         max_values = []
#         row_factors = []
#         col_factors = []
        
#         factor_columns = dataframe.columns[1:]  # Exclude the 'factor' column
        
#         for idx, row in enumerate(dataframe.rows()):
#             factor_name = row[0]  # First column is the row factor name
#             row_values = row[1:]  # Remaining columns are the values
            
#             # 过滤掉None值
#             filtered_row = [(val, factor_columns[col_idx]) for col_idx, val in enumerate(row_values) if val is not None]
#             if filtered_row:
#                 max_value, max_col = max(filtered_row, key=lambda x: x[0])
#                 row_factors.append(factor_name)
#                 col_factors.append(max_col)
#             else:
#                 max_value = None
#                 row_factors.append(None)
#                 col_factors.append(None)
            
#             max_values.append(max_value)

#         # 创建结果DataFrame
#         result = pl.DataFrame({
#             "row_factor": row_factors,
#             "max_value": max_values,
#             "col_factor": col_factors
#         })

#         return result

#     def compute_all(self, correlations=["spearman", "ic", "mine", "kendall"]):
#         """
#         计算所有相关性并打印结果
#         :param correlations: 选择需要计算和打印的相关系数，可以为("spearman", "ic", "mine", "kendall")的任意组合
#         """
#         correlation_mapping = {
#             "spearman": self.compute_spearman,
#             "ic": self.compute_ic,
#             "mine": self.compute_mine,
#             "kendall": self.compute_kendall
#         }

#         for corr in correlations:
#             if corr in correlation_mapping:
#                 matrix = correlation_mapping[corr]()
#                 print(f"\n{corr.capitalize()}相关性矩阵：")
#                 print(matrix)

#                 highest_corr = self.get_max_value_and_column(matrix)
#                 print(f"\n每个因子与其他因子之间的最高{corr.capitalize()}相关性：")
#                 print(highest_corr)
    
#     def split(self, date_time):
#         """
#         以时间 time_list 为界限将 aligned_factors 分为两部分并返回
#         :param time_list: [年, 月, 日, 时, 分, 秒] 的时间格式列表
#         :return: 全部表格、时间 time_list 之前的表格、时间 time_list 之后的表格
#         """
#         # date_datetime = pl.datetime(*time_list)
#         ans = self.aligned_factors.sort("open_time")
#         before_date_df = ans.filter(pl.col('open_time') <= date_time)
#         after_date_df = ans.filter(pl.col('open_time') > date_time)

#         return ans, before_date_df, after_date_df
