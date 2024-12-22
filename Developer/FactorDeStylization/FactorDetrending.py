import polars as pl
import statsmodels.api as sm

class FactorDetrending:
    def __init__(self, column_to_clean, reference_column):
        """
        Initialize the FactorDetrending class.

        :param column_to_clean: Name of the column to perform de-stylization on (e.g., the factor column).
        :param reference_column: Name of the column to use as the reference (e.g., close prices).
        """
        self.column_to_clean = column_to_clean
        self.reference_column = reference_column

    def remove_outliers(self, group):
        """
        Remove outliers in the specified column using Median Absolute Deviation (MAD).

        :param group: A DataFrame group for a single time slice.
        :return: A cleaned DataFrame with outliers replaced.
        """
        column = self.column_to_clean
        median = group[column].median()
        mad = (group[column] - median).abs().median()

        lower_bound = median - 5 * mad
        upper_bound = median + 5 * mad

        new_column = group[column].clone()

        for i in range(len(new_column)):
            if new_column[i] < lower_bound:
                new_column[i] = lower_bound
            elif new_column[i] > upper_bound:
                new_column[i] = upper_bound

        group = group.with_columns(pl.Series(column, new_column))
        return group

    def orthogonalize(self, group):
        """
        Perform orthogonalization by regressing the factor column on the reference column.

        :param group: A DataFrame group for a single time slice.
        :return: A DataFrame with residuals from the regression.
        """
        X = group[self.reference_column].to_numpy()
        Y = group[self.column_to_clean].to_numpy()

        X = sm.add_constant(X)
        model = sm.OLS(Y, X).fit()
        residuals = model.resid

        return pl.DataFrame({
            'open_time': group['open_time'],
            'symbol': group['symbol'],
            f'{self.column_to_clean}_residuals': residuals
        })

    def process(self, all_data):
        """
        Execute outlier removal and orthogonalization sequentially.

        :param all_data: Input DataFrame containing the data to process.
        :return: A DataFrame with the processed residuals.
        """
        all_data_clean = all_data.groupby('open_time').apply(self.remove_outliers)
        residuals_df = all_data_clean.groupby('open_time').apply(self.orthogonalize)
        return residuals_df