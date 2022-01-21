library(quantmod)
library(rugarch)
library(rmgarch)
library(nonnest2)
library(dplyr)

mkt <- read.csv('/cloud/project/mkt.csv', header = T)
size <- read.csv('/cloud/project/size.csv', header = T)
value <- read.csv('/cloud/project/value.csv', header = T)
mom <- read.csv('/cloud/project/momentum.csv', header = T)
profit <- read.csv('/cloud/project/profit.csv', header = T)
investment <- read.csv('/cloud/project/investment.csv', header = T)

size$mkt <- mkt$Mkt.RF
value$mkt <- mkt$Mkt.RF
mom <- inner_join(mom, mkt)
names(mom)[5] <- 'mkt'
profit <- inner_join(profit, mkt)
names(profit)[5] <- 'mkt'
investment <- inner_join(investment, mkt)
names(investment)[5] <- 'mkt'

dcb_generator <- function(factor_table){
  uspec.n = multispec(replicate(4, ugarchspec(mean.model = list(armaOrder = c(1,0)))))
  multf = multifit(uspec.n, factor_table[c('long','short','longshort','mkt')])
  spec1 = dccspec(uspec = uspec.n, dccOrder = c(1, 1), distribution = 'mvt')
  fit1 = dccfit(spec1, data = factor_table[c('long','short','longshort','mkt')], fit.control = list(eval.se = TRUE), fit = multf)
  factor_dcc_cov <- rcov(fit1)
  
  factor_dcb <- as.data.frame(x=factor_table$Date)
  names(factor_dcb) <- 'Date'
  
  factor_dcb$long <- (factor_dcc_cov[1,4,] / factor_dcc_cov[4,4,])
  factor_dcb$short <- (factor_dcc_cov[2,4,] / factor_dcc_cov[4,4,])
  factor_dcb$longshort <- (factor_dcc_cov[3,4,] / factor_dcc_cov[4,4,])
  
  return (factor_dcb)
  
}
size_dcb <- dcb_generator(size)
write.csv(size_dcb, 'size_dcb.csv')
value_dcb <- dcb_generator(value)
write.csv(value_dcb, 'value_dcb.csv')
momentum_dcb <- dcb_generator(mom)
write.csv(momentum_dcb, 'momentum_dcb.csv')
profit_dcb <- dcb_generator(profit)
write.csv(profit_dcb, 'profit_dcb.csv')
investment_dcb <- dcb_generator(investment)
write.csv(investment_dcb,'investment_dcb.csv')
