import numpy as np
import pandas as pd

class VolTarget:
    def __init__(self, leverage_upper, leverage_lower, univariate_series, target_vol, lagging_days):
        self.leverage_upper = leverage_upper
        self.leverage_lower = leverage_lower
        self.univariate_series = univariate_series
        self.target_vol = target_vol
        self.lagging_days = lagging_days

    def leverage_scaler(self, x):
        if x > self.leverage_upper:
            return self.leverage_upper
        elif x < self.leverage_lower:
            return self.leverage_lower
        else:
            return x
    
    def vol_target_mm_maker(self, rolling_periods):
        self.rolling_periods = rolling_periods
        univariate_series = self.univariate_series
        realized_vol = univariate_series.rolling(window=self.rolling_periods, min_periods = 0).std()*np.sqrt(252)
        leverage_constant = pd.DataFrame()
        vol_target_mm = pd.DataFrame()

        leverage_constant = (self.target_vol / realized_vol.shift(self.lagging_days))

        leverage_constant = leverage_constant.applymap(self.leverage_scaler)

        vol_target_mm = univariate_series.iloc[self.lagging_days+1:] * leverage_constant.iloc[self.lagging_days+1:]

        vol_target_mm.index.name = 'Date'

        self.vol_target_mm_scaler = leverage_constant.iloc[self.lagging_days+1:]
        return vol_target_mm

    def vol_target_ewma_maker(self, com=10.65):
        self.com = com
        univariate_series = self.univariate_series
        predicted_vol = (univariate_series.ewm(com = self.com).std() * np.sqrt(252))
        leverage_constant = pd.DataFrame()
        vol_target_ewma = pd.DataFrame()

        leverage_constant = (self.target_vol / predicted_vol.shift(self.lagging_days))

        leverage_constant = leverage_constant.applymap(self.leverage_scaler)

        vol_target_ewma = univariate_series.iloc[self.lagging_days+1:] * leverage_constant.iloc[self.lagging_days+1:]

        vol_target_ewma.index.name = 'Date'

        self.vol_target_ewma_scaler = leverage_constant.iloc[self.lagging_days+1:]
        return vol_target_ewma


def vol_of_vol(univariate_series, rolling_periods):
  return ( univariate_series.rolling(window=rolling_periods).std() * np.sqrt(252) ).iloc[rolling_periods-1:]