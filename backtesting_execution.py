sum_profit =0
sum_trade_num = 0
cnt = 0
zero_num = 0
for stock in kosdaq_stocks:
  cnt += 1
  df = pd.read_csv('/content/drive/MyDrive/kosdaq/' + stock + '.csv')
  df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%Y%m%d')
  df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
  df['Adj Close']=df['close']
  df['Low']=df['low']
  df['High']=df['high']
  df['Open']=df['open']
  df['Close']=df['close']
  df['Volume']=df['volume']
  df=df.drop(['low','high','open','close','volume'],axis=1)
  a1 , a2 = backtesting(df)
  if a2 == 0:
    zero_num += 1
  if a2 != 0:
    sum_profit += a1-(a2/2)
    sum_trade_num += a2
    print(stock, a1-(a2/2), a2)
print(sum_profit/(cnt-zero_num), sum_trade_num/(cnt-zero_num) , zero_num)
