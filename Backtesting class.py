class DeepLearningStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, model):
        super(DeepLearningStrategy, self).__init__(feed)
        self.__instrument = instrument
        self.__position = None
        self.__model = model
        self.__prices = []  # 종가 데이터를 저장할 리스트
        self.__opens=[]
        self.__volumes = []  # 거래량 데이터를 저장할 리스트
        self.__buy_date = None  # 매수 날짜 저장 변수
        self.__target_price = None  # 목표가 저장 변수
        self.feed=feed

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.__prices.append(bar.getClose())   # 종가 데이터를 저장
        self.__opens.append(bar.getOpen())
        current_date = bar.getDateTime()

        # 데이터가 있는지 확인
        date_times = self.feed[self.__instrument].getDateTimes()
        if len(date_times) > 0:
            date_len = len(date_times)-1
            self.__last_date = date_times[date_len]  # 마지막 날짜 저장
        else:
            self.__last_date = None  # 데이터가 없을 경우 None으로 설정

        # 최소 50일치 데이터가 있어야 예측 가능
        if len(self.__prices) < 21:
            return

        # 마지막 20일의 거래량 데이터 가져오기
        price = []
        for i in range(-1, -21, -1):  # 마지막 20일간의 데이터
            price_t = self.__prices[i]
            price.append(price_t)
        open = []
        for i in range(-1, -21, -1):  # 마지막 20일간의 데이터
            open_t = self.__opens[i]
            open.append(open_t)

        price=torch.Tensor(price).unsqueeze(1)
        price=price.reshape(1,-1)
        open=torch.Tensor(open).unsqueeze(1)
        open=open.reshape(1,-1)

        x = ...

        main_input = x.float()

        # 딥러닝 모델로 다음 날 가격 예측
        self.__model.eval()
        prediction = self.__model(main_input)
        predicted_classes = torch.argmax(prediction, dim=1)

        # 간단한 매수/매도 로직
        if self.__position is None:
            if predicted_classes == 1:  # 예측된 가격이 현재 가격보다 크면 매수
                available_cash = self.getBroker().getCash()  # 현재 자산(현금)
                price_per_share = bar.getClose()  # 현재 주가
                current_date = bar.getDateTime()

                # 구매 가능한 최대 주식 수 계산 (수수료 및 추가 비용을 15%로 가정)
                max_shares = int(available_cash / (price_per_share * 1.01))

                if max_shares > 0:
                    self.__position = self.enterLong(self.__instrument, max_shares)
                    self.__buy_date = bar.getDateTime()  # 매수 날짜를 저장
                    self.info(f"매수 메시지: {bar.getDateTime()}에 {bar.getPrice()}에 매수함")
                    self.__target_price = bar.getClose() * 1.15  # 목표가를 설정 (4% 상승)
                    self.__current_price = bar.getClose()
        elif self.__position is not None and not self.__position.exitActive():
          high_price_today = bar.getHigh()  # 오늘의 최고가
          low_price_today = bar.getLow()
          current_date = bar.getDateTime()

          # 매수 후 5일이 지나면 강제 매도
          if (current_date - self.__buy_date).days > 5 and high_price_today >= self.__current_price * 1:
            self.info(f"5일 경과 후 강제 매도: {current_date}에 {bar.getPrice()}에 매도함")
            self.__position.exitMarket()
            self.__position = None  # 매도 후 포지션 초기화
