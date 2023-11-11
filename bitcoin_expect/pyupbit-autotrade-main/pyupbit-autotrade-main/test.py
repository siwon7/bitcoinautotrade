import pyupbit

access = "7hBN0fUTdQrQZ6YS9b3cvpOGLILwgVoBAFaEsiGu"
secret = "5mZvAWuCt7gPldFnC718QM83sxMtmoUj8ICxoqF2"
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-BTC"))     # KRW-BTC 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회