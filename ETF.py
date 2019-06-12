import pandas as pd
# import bs4 as bs
# import urllib.request
# import html5lib

###### Part 1 ######
# Find all the ETFs available for trading in HKEX, using the `read_html` function in Pandas
####################
dfs = pd.read_html('http://www.aastocks.com/tc/stocks/etf/search.aspx?t=1&s=0&o=1&sl=1', encoding='utf8')
tab_num = 25 # table includes all ETF information
df = dfs[tab_num]
ETF_Name = df.iloc[1:len(df),0]
ETF_Name = ETF_Name.apply(str.split)

###
# Not use: BeautifulSoup functions
###
# source = urllib.request.urlopen('http://www.aastocks.com/tc/stocks/etf/search.aspx?t=1&s=0&o=1&sl=1').read()
# source = urllib.request.urlopen('https://pythonprogramming.net/sitemap.xml').read()
# soup = bs.BeautifulSoup(source, 'lxml')


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
####################


###### Part 5 ######
# Recommendation
####################
