import time
import pyupbit
import datetime

access = "7hBN0fUTdQrQZ6YS9b3cvpOGLILwgVoBAFaEsiGu"
secret = "5mZvAWuCt7gPldFnC718QM83sxMtmoUj8ICxoqF2"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

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

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
try:
    balances = upbit.get_balances()
    if balances is not None:
        print("login success")
except Exception as e:
    print("login failed:", e)


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        print(now)
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.4)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
        
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
        time.sleep(1)
