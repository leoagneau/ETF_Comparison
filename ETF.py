import numpy as np
import pandas as pd
from datetime import date
import time
import re

###### Part 1 ######
# Find all the ETFs available for trading in HKEX, using the `read_html` function in Pandas
####################
def get_ETF_list(lang='en'):
    lang = lang  # 'tc' or 'en'
    url = 'http://www.aastocks.com/' + lang + '/stocks/etf/search.aspx?t=1&s=0&o=1&sl=1'
    dfs = pd.read_html(url, encoding='utf8')
    df = max(dfs, key=len)  # table includes all ETF information
    ETF_Name = df.iloc[1:len(df), 0]
    non_etf_idx = ETF_Name[~ETF_Name.str.contains('.HK')].index
    ETF_Name = ETF_Name.drop(non_etf_idx)
    ETF_Name = ETF_Name.apply(str.rsplit, args=(' ', 1))
    ETF_Name.reset_index(inplace=True, drop=True)
    ETF_Index = df.iloc[1:len(df), 1]
    ETF_Index = ETF_Index.drop(non_etf_idx)
    ETF_Index.reset_index(inplace=True, drop=True)
    return (ETF_Name, ETF_Index)


def show_ETF_info():
    return (pd.concat([ETF_Name, ETF_Index], axis=1))


def get_historical(date_start, date_end, ticker):
    # date_start = date(2017, 1, 1)
    # date_end = date.today()
    # ticker = ETF_Name[1][1].strip('0')
    start_tstmp = int(time.mktime(date_start.timetuple()))
    end_tstmp = int(time.mktime(date_end.timetuple()))
    # Ref URL(TC): https://hk.finance.yahoo.com/quote/2800.HK/history?period1=1483200000&period2=1560960000&interval=1mo&filter=history&frequency=1mo
    # Ref URL(EN): https://finance.yahoo.com/quote/2800.HK/history?period1=1483200000&period2=1561046400&interval=1mo&filter=history&frequency=1mo
    his_url = 'https://finance.yahoo.com/quote/' + ticker + '/history?period1=' + str(start_tstmp) + '&period2=' + str(
        end_tstmp) + '&interval=1mo&filter=history&frequency=1mo'
    print("Getting data of", ticker, "...")
    his_tbl = pd.read_html(his_url, header=0)
    df = his_tbl[0]
    if (df.columns[0] == 'Date'):
        df = df.iloc[0:len(df) - 1, [0, 5]]  # Only retrieve 'Date' and 'Adj Close'
        non_price_idx = df[df.iloc[:, 1].str.contains('Dividend')].index
        # non_price_idx = df[df.iloc[:, 1].isna()].index
        df = df.drop(non_price_idx)  # Remove 'dividend' information row
        # datetime.strptime(df.iloc[0,0], '%b %d, %Y').date()
        df.Date = pd.to_datetime(df.Date)  # Convert to datetime
        df.iloc[:, 1:df.shape[1]] = df.iloc[:, 1:df.shape[1]].apply(pd.to_numeric, errors='coerce')  # Convert to numeric
        col_name = ticker + '_Adj_Close'
        df.columns = ['Date', col_name]
        df[ticker + '_pct_diff'] = df[col_name].pct_change(periods=-1) * 100
        # return(df.drop(columns=['Adj_Close']).set_index('Date'))
        return (df.set_index('Date'))
    else:
        return (None)


def exclude_outliers(corr_df):
    q1s, q3s = np.nanpercentile(corr_df, [25, 75])
    iqrs = q3s - q1s
    lbs = q1s - 1.5 * iqrs
    ubs = q3s + 1.5 * iqrs
    corr_df[np.logical_or(corr_df < lbs, corr_df > ubs)] = np.nan
    return(corr_df)


def can_add(etf, min_len):
    if etf is not None:
        if len(etf) > min_len:
            if etf.iloc[-min_len:,0].isna().sum() == 0:
                return True
    return False


def find_nsmallest(corr_mat, n):
    corr_arr = corr_mat.to_numpy()
    corrs = corr_arr[np.triu_indices(len(corr_arr), 1)]  # extract the upper triangle
    abs = np.abs(corrs)
    abs_sorted = np.sort(abs)
    pos = [np.argwhere(abs == abs_sorted[i]).item() for i in range(n)]
    return corrs[pos]

def find_nsmallest_pairs(corr_mtx, num_pairs):
    smallest_corrs = find_nsmallest(corr_mtx, num_pairs)
    smallest_pos = [np.argwhere(np.triu(corr_mtx, 1) == v)[0] for v in smallest_corrs]
    corrs_info = [[corr_mtx.index[smallest_pos[i][0]], corr_mtx.columns[smallest_pos[i][1]], smallest_corrs[i]] for i
                  in range(len(smallest_corrs))]
    return corrs_info


def find_specific_nsmallest_pairs(ticker, corr_mtx, num_pairs):
    corrs = corr_mtx[corr_mtx.columns == ticker]
    return corrs[np.abs(corrs.T).nsmallest(num_pairs, ticker).index].T


def analyse_corr(corr_mtx, ticker, pair_num):
    ncorrs_nsmallest_pairs = find_nsmallest_pairs(corr_mtx, pair_num)
    ticker_nsmallest_pairs = find_specific_nsmallest_pairs(ticker, corr_mtx, pair_num)
    xlab = ticker
    for i in range(pair_num):
        ylab = ticker_nsmallest_pairs.index[i]
        corrplot = etfs_diff_aggr.loc[:, [xlab, ylab]].plot.scatter(x=xlab, y=ylab)
        corrplot.set(xlabel=xlab+", monthly, %", ylabel=ylab+", monthly, %")

if __name__ == '__main__':
    ETF_Name, ETF_Index = get_ETF_list('en')
    Names = ETF_Name.tolist()
    etf_tickers = list(zip(*Names))[1]   # https://stackoverflow.com/a/3308805/3243870
    d1 = date(2017,1,1)
    d2 = date.today().replace(day=1)
    etf_all = []
    etf_all = [get_historical(d1, d2, etf.strip('0')) for etf in etf_tickers]
    month_diff = (d2.year-d1.year)*12 + (d2.month-d1.month)
    min_len = round(month_diff / 1.5)  # at least the most recent 2/3 of the whole period contains data
    etfs = [x for x in etf_all if can_add(x, min_len)]
    # etfs_close = [df.filter(regex='Adj_Close') for df in etfs]
    # etfs_close_aggr = pd.concat(etfs_close[:], axis=1)
    etfs_diff = [df.filter(regex='pct_diff') for df in etfs]
    etfs_diff_aggr = pd.concat(etfs_diff[:], axis=1)
    etfs_diff_aggr = etfs_diff_aggr.rename(columns=lambda x: re.sub('_pct_diff', '', x))  # remove unnecessary string in column labels
    etfs_corr = etfs_diff_aggr.corr()
    analyse_corr(etfs_corr, '2800.HK', 5)

    ## Exclude outliers
    etfs_diff_aggr = exclude_outliers(etfs_diff_aggr)
    etfs_corr = etfs_diff_aggr.corr()

    ## Correlation analysis after excluding outliers
    ticker = '2800.HK'
    corr_mtx = etfs_corr
    pair_num = 6
    ticker_nsmallest_pairs = find_specific_nsmallest_pairs(ticker, corr_mtx, pair_num)
    xlab = ticker
    fig, axes = plt.subplots(pair_num//2,2)
    fig.subplots_adjust(hspace=0.5)
    for i in range(pair_num):
        ylab = ticker_nsmallest_pairs.index[i]
        corrplot = etfs_diff_aggr.loc[:, [xlab, ylab]].plot.scatter(x=xlab, y=ylab, ax=axes[i//2, i%2])
        corrplot.set(xlabel="", ylabel="", title=ylab)



###### Part 2 ######
# Retrieve all the necessary parameters for estimation:
# Indicators: P/E, E/P, P/B, dividend yield ratio
# Involved parameters: price, earnings, book value, dividend
# Timeframe: rollling 4 quarters, last whole year, last 10 years, max time period
####################


###### Part 3 ######
# Apply formulae
####################


###### Part 4 ######
# Calculate expenses
# 總開支比率(Total Expense Ratio): 管理費(Mgmt fee)、牌照費(License fee)、交易費(Tx fee)、托管費(Custodian fee) etc.
# 其餘(Other)︰ 買賣佣金(Commission)、印花稅(Stamp duty)、交易徵費(Transaction Levy)(0.0027%)、交易費(Trading fee)(0.005%)、CCASS費用(2<=0.002%<=100) etc.
####################


###### Part 5 ######
# Recommendation
####################

