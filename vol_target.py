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

class Ewm_Beta_Target:
    def __init__(self, leverage_upper, leverage_lower,mkt,factor_long_side,factor_short_side, target_beta, lagging_days):
        self.leverage_upper = leverage_upper
        self.leverage_lower = leverage_lower
        self.mkt = mkt
        self.factor_long_side = factor_long_side
        self.factor_short_side = factor_short_side
        self.target_beta = target_beta
        self.lagging_days = lagging_days

    def leverage_scaler(self, x):
        if x > self.leverage_upper:
            return self.leverage_upper
        elif x < self.leverage_lower:
            return self.leverage_lower
        else:
            return x

    def beta_target_ewma_maker(self, com = 10.65):
        self.com = com
        factor_long_side = self.factor_long_side
        factor_short_side = self.factor_short_side

        factor_panel = pd.merge(pd.DataFrame(self.factor_long_side, columns = ['long']), pd.DataFrame(self.factor_short_side, columns = ['short']), on = 'Date', how = 'inner')
        factor_panel['mkt'] = self.mkt

        predicted_beta_long = (factor_panel.ewm(com=10.65).cov()['long'][:,'mkt'] / factor_panel.ewm(com=10.65).cov()['mkt'][:,'mkt'])
        predicted_beta_short = (factor_panel.ewm(com=10.65).cov()['short'][:,'mkt'] / factor_panel.ewm(com=10.65).cov()['mkt'][:,'mkt'])

        leverage_constant_long = (self.target_beta / predicted_beta_long.shift(self.lagging_days))
        leverage_constant_long = leverage_constant_long.map(self.leverage_scaler)

        leverage_constant_short = (self.target_beta / predicted_beta_short.shift(self.lagging_days))
        leverage_constant_short = leverage_constant_short.map(self.leverage_scaler)

        beta_target_long = factor_long_side.iloc[self.lagging_days+1:] * leverage_constant_long.iloc[self.lagging_days+1:]
        beta_target_short = factor_short_side.iloc[self.lagging_days+1:] * leverage_constant_short.iloc[self.lagging_days+1:]

        beta_hedged_factor = beta_target_long - beta_target_short

        self.beta_target_long = beta_target_long
        self.beta_target_short = beta_target_short

        return beta_hedged_factor


def vol_of_vol(univariate_series, rolling_periods):
  return ( univariate_series.rolling(window=rolling_periods).std() * np.sqrt(252) ).iloc[rolling_periods-1:]