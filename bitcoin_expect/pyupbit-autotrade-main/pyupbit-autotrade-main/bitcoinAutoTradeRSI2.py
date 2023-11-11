import time
import pyupbit
import datetime
import os

access = "7hBN0fUTdQrQZ6YS9b3cvpOGLILwgVoBAFaEsiGu"
secret = "5mZvAWuCt7gPldFnC718QM83sxMtmoUj8ICxoqF2"

ticker = "KRW_BTC"
btc_day = pyupbit.get_ohlcv(ticker, interval="day")

# rsi 가져오기
def get_rsi(df, period=14):

    """ 전일 대비 변동 평균 """
    df['change'] = df['close'].diff()

    """ 상승한 가격과 하락한 가격 """
    df['up'] = df['change'].apply(lambda x: x if x > 0 else 0)
    df['down'] = df['change'].apply(lambda x: -x if x < 0 else 0)

    """ 상승 평균과 하락 평균 """
    df['avg_up'] = df['up'].ewm(alpha=1/period).mean()
    df['avg_down'] = df['down'].ewm(alpha=1/period).mean()

    """ 상대강도지수(RSI) 계산 """
    df['rs'] = df['avg_up'] / df['avg_down']
    df['rsi'] = 100 - (100 / (1 + df['rs']))
    rsi = df['rsi']
    print(rsi)

    return rsi


# 이미 매수한 코인인지 확인
def has_coin(ticker, balances):
    result = False
    
    for coin in balances:
        coin_ticker = coin['unit_currency'] + "-" + coin['currency']
        
        if ticker == coin_ticker:
            result = True
            
    return result



# 거래량 추적
def get_transaction_amount(date, num):
    tickers = pyupbit.get_tickers("KRW")	# KRW를 통해 거래되는 코인만 불러오기
    dic_ticker = {}

    for ticker in tickers:
        df = pyupbit.get_ohlcv(ticker, date)	# date 기간의 거래대금을 구해준다
        volume_money = 0.0  
        
        # 순위가 바뀔 수 있으니 당일은 포함 x
        for i in range(2, 9):
            volume_money += df['close'][-i] * df['volume'][-i]  

        dic_ticker[ticker] = volume_money
    # 거래대금 큰 순으로 ticker를 정렬
    sorted_ticker = sorted(dic_ticker.items(), key= lambda x : x[1], reverse= True)

    coin_list = []
    count = 0

    for coin in sorted_ticker:
        count += 1

        # 거래대금이 높은 num 개의 코인만 구한다
        if count <= num:
            coin_list.append(coin[0])
        else:
            break

    return coin_list
tickers = get_transaction_amount("day", 5)	# 거래대금 상위 5개 코인 선정

#수익률 계산
def get_revenue_rate(balances, ticker):
    revenue_rate = 0.0

    for coin in balances:
        # 티커 형태로 전환
        coin_ticker = coin['unit_currency'] + "-" + coin['currency']

        if ticker == coin_ticker:
            # 현재 시세
            now_price = pyupbit.get_current_price(coin_ticker)
             
            # 수익률 계산을 위한 형 변환
            revenue_rate = (now_price - float(coin['avg_buy_price'])) / float(coin['avg_buy_price']) * 100.0

    return revenue_rate
balances = upbit.get_balances()
ticker_rate = get_revenue_rate(balances, target_ticker)

have_coin = 0.0
for coin in balances:
    coin_ticker = coin['unit_currency'] + "-" + coin['currency']

    if target_ticker == coin_ticker:
        have_coin = float(coin_ticker['avg_buy_price']) * float(coin_ticker['balance'])
        ticker_rate = get_revenue_rate(balances, target_ticker)
        
	# 실제 매수된 금액의 오차 감안
        if (money * 0.99) < have_coin:
            if ticker_rate <= -7.0:
                amount = upbit.get_balance(target_ticker)       # 현재 코인 보유 수량	  
                upbit.buy_market_order(target_ticker, amount)   # 시장가에 매도
		
        # 실제 매수된 금액의 오차 감안
        elif (money * 0.49) < have_coin and (money * 0.51) > have_coin:
            if ticker_rate <= -5.0:
                upbit.buy_market_order(target_ticker, money * first_buy)   # 시장가에 코인 매수


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
try:
    balances = upbit.get_balances()
    if balances is not None:
        print("login success")
except Exception as e:
    print("login failed:", e)
balances = upbit.get_balances()

my_money = float(balances[0]['balance'])    # 내 원화
money_rate = 1.0                            # 투자 비중
money = my_money * money_rate               # 비트코인에 할당할 비용
money = math.floor(money)		    # 소수점 버림
count_coin = len(coin_list)	# 목표 코인 개수
money /= count_coin		# 각각의 코인에 공평하게 자본 분배
first_buy = 0.5             	# 첫 매수 비중
water_buy = 1.0 - first_buy 	# 물 탈 비중
target_revenue = 1.0        # 목표 수익률 (1.0 %)
division_amount = 0.3       # 분할 매도 비중

for target_ticker in tickers:
    df_day = pyupbit.get_ohlcv(target_ticker, interval="day")     # 일봉 정보
    rsi14 = get_rsi(df_day, 14).iloc[-1]                          # 당일 RSI
    before_rsi14 = get_rsi(df_day, 14).iloc[-2]                   # 작일 RSI

    if has_coin(ticker, balances):
        # 매도 조건 충족
        if rsi14 < 70 and before_rsi14 > 70:
            amount = upbit.get_balance(target_ticker)       # 현재 코인 보유 수량	  
            upbit.sell_market_order(target_ticker, amount)  # 시장가에 매도 
            balances = upbit.get_balances()                 # 매도했으니 잔고를 최신화!

    else:
        # 매수 조건 충족
        if rsi14 > 30 and before_rsi14 < 30:
            upbit.buy_market_order(target_ticker, money)    # 시장가에 코인 매수
            balances = upbit.get_balances()         	    # 매수했으니 잔고를 최신화!

# 분할매도
if rsi14 < 70 and before_rsi14 > 70:
        amount = upbit.get_balance(target_ticker)       # 현재 코인 보유 수량
        upbit.buy_market_order(target_ticker, amount)   # 시장가에 매도 
        balances = upbit.get_balances()                 # 매도했으니 잔고를 최신화!

# 매도 조건 충족 (과매수 구간일 때)
elif rsi14 > 70:
    ticker_rate = get_revenue_rate(balances, target_ticker)     # 수익률 확인

    # 목표 수익률을 만족한다면
    if ticker_rate >= target_revenue:
        amount = upbit.get_balance(target_ticker)           # 현재 코인 보유 수량
        sell_amount = amount * division_amount              # 분할 매도 비중
        upbit.buy_market_order(target_ticker, sell_amount)  # 시장가에 매도 
        balances = upbit.get_balances()                     # 매도했으니 잔고를 최신화!


max_rsi_data = dict()
max_rsi_path = r"C:\Users\c1203\Desktop\bitcoin_expect\pyupbit-autotrade-main\pyupbit-autotrade-main"

# 파일을 불러온다
try:
    # 파일을 읽어서 딕셔너리에 적용 
    with open(max_rsi_path, 'r') as json_file:
        max_rsi_data = json.load(json_file)

except Exception as e:
    print("Init...")
	
    # 0으로 초기화
    max_rsi_data["max_rsi14"] = 0.0
    max_rsi_data["sell_signal"] = False
    
    # 파일에 저장
    with open(max_rsi_path, 'w') as outfile:
        json.dump(max_rsi_data, outfile)


