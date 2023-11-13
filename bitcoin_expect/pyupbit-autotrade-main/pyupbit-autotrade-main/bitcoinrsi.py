import pyupbit
import numpy as np
import datetime
import time

#개인키, 비밀번호
access = "7hBN0fUTdQrQZ6YS9b3cvpOGLILwgVoBAFaEsiGu"
secret = "5mZvAWuCt7gPldFnC718QM83sxMtmoUj8ICxoqF2"

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
try:
    balances = upbit.get_balances()
    if balances is not None:
        print("login success")
except Exception as e:
    print("login failed:", e)

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1) 
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# RSI 계산 함수
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_rsi(ohlcv, period=14):
    delta = ohlcv['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

#다이버전스 구하기
def find_divergences(df, lookback=14):
    """
    RSI와 가격 데이터에서 양 다이버전스와 음 다이버전스를 탐지합니다.
    양 다이버전스는 매수 신호, 음 다이버전스는 매도 신호로 간주할 수 있습니다.
    """
    price_highs = df['high'].rolling(window=lookback).max()
    price_lows = df['low'].rolling(window=lookback).min()
    rsi_highs = df['RSI'].rolling(window=lookback).max()
    rsi_lows = df['RSI'].rolling(window=lookback).min()

    bullish_divergence = (price_lows.iloc[-1] < price_lows.iloc[-lookback]) and (rsi_lows.iloc[-1] > rsi_lows.iloc[-lookback])
    bearish_divergence = (price_highs.iloc[-1] > price_highs.iloc[-lookback]) and (rsi_highs.iloc[-1] < rsi_highs.iloc[-lookback])
    return bullish_divergence, bearish_divergence



# 업비트에서 비트코인 가격 데이터 가져오기
df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=100)

# RSI 계산
df['RSI'] = calculate_rsi(df)

# 매매 신호 생성
buy_signal = (df['RSI'] < 30) & (df['RSI'].shift(1) >= 30)  # RSI가 30 이하로 떨어진 후 상승하는 경우
sell_signal = (df['RSI'] > 70) & (df['RSI'].shift(1) <= 70)  # RSI가 70 이상으로 상승한 후 하락하는 경우

while True:
    try:
        # 데이터 가져오기
        df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=100)
        df['RSI'] = calculate_rsi(df)
        current_rsi = get_rsi(df)
        bullish_divergence, bearish_divergence = find_divergences(df)

        # 매수 조건 검사
        if current_rsi < 30 or bullish_divergence:
            krw_balance = get_balance("KRW")
            if krw_balance > 5000:  # 최소 거래 금액
                upbit.buy_market_order("KRW-BTC", krw_balance * 0.9995)

        # 매도 조건 검사
        elif current_rsi > 70 or bearish_divergence:
            btc_balance = get_balance("BTC")
            if btc_balance > 0.00008:  # 최소 거래 수량
                upbit.sell_market_order("KRW-BTC", btc_balance)

        print(f"Current RSI: {current_rsi}")
        print(f"Bullish_divergence: {bullish_divergence}")
        print(f"Bearish_divergence: {bearish_divergence}")
        time.sleep(60)  # 60초마다 반복

        # 원화 잔고 및 비트코인 잔고 조회
        krw_balance = get_balance("KRW")
        btc_balance = get_balance("BTC")
        
        # 현재 비트코인 가격 조회
        current_btc_price = get_current_price("KRW-BTC")
        
        # 전체 자산 계산 (KRW + BTC 환산 금액)
        total_assets = krw_balance + (btc_balance * current_btc_price)
        
        print(f"current krw balance: {krw_balance} KRW")
        print(f"current btc balance: {btc_balance} BTC")
        print(f"total assets: {total_assets} KRW")

    except Exception as e:
        print(e)
        time.sleep(60)