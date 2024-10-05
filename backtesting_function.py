def backtesting(df):
  df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

  df.replace([np.inf], 1000000, inplace=True)
  df.replace([-np.inf], -100000, inplace=True)

  filtered_df = df[
    (df['Low'] <= df['Open']) &   # Low가 Open보다 크면 안 됨
    (df['Low'] <= df['Close']) &  # Low가 Close보다 크면 안 됨
    (df['Low'] <= df['High']) &   # Low가 High보다 크면 안 됨
    (df['High'] >= df['Open']) &  # High는 Open보다 작으면 안 됨
    (df['High'] >= df['Close']) & # High는 Close보다 작으면 안 됨
    (df['Volume'] > 0)           # 거래량은 음수일 수 없음
  ]

  #  변환된 DataFrame을 다시 CSV 파일로 저장
  filtered_df.to_csv('AAPL_fixed.csv', index=False)

  # Yahoo 피드 준비
  feed = yahoofeed.Feed()
  feed.addBarsFromCSV("aapl", "AAPL_fixed.csv")

  # 전략 실행 (딥러닝 모델을 통합)
  start = DeepLearningStrategy(feed, "aapl", main)

  # 수익률 분석기 추가
  returnsAnalyzer = returns.Returns()
  start.attachAnalyzer(returnsAnalyzer)

  # 트레이드 분석기 추가 (거래 내역 및 수익 확인)
  tradesAnalyzer = trades.Trades()
  start.attachAnalyzer(tradesAnalyzer)

  # 백테스트 실행
  initial_cash = start.getBroker().getCash()
  logging.getLogger("broker.backtesting").setLevel(logging.CRITICAL)
  start.run()
  profit = ((tradesAnalyzer.getProfits().sum() + tradesAnalyzer.getLosses().sum())/ initial_cash) * 100

  return profit,tradesAnalyzer.getCount()
