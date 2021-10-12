import ccxt
from datetime import datetime, timedelta
import pandas as pd

pd.set_option('display.max_row',1000)
pd.set_option('display.max_columns',10)


#실시간
#ticker = binance.fetch_ticker('BTC/USDT') #비트코인 가격
#print(ticker['open'], ticker['high'], ticker['low'], ticker['close'])

class DataModel():

    def __init__(self, periods='1d'):
        self.binance = ccxt.binance()
        self.periods = periods
        self.cur_rsi = 0

    #바낸 데이터 긁어오기
    def get_data(self, exchange):
        #현재는 exchange가 바낸만 구현
        ohlcvs = self.binance.fetch_ohlcv('BTC/USDT', self.periods)
        #일자, 시가, 고가, 저가, 종가, 거래량
        df = pd.DataFrame(ohlcvs, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df['datetime'] = pd.DatetimeIndex(df['datetime']) + timedelta(hours=9)
        df.set_index('datetime', inplace=True)
        return df

    #rsi 계산
    def get_rsi(self, df, periods=14, ema=True):
        close_delta=df['close'].diff()
        up=close_delta.clip(lower=0)
        down=-1*close_delta.clip(upper=0)

        if ema: #exponentail moving avg
            ma_up=up.ewm(com=periods-1, adjust=True, min_periods=periods).mean()
            ma_down=down.ewm(com=periods-1, adjust=True, min_periods=periods).mean()
        else: #simple moving avg
            ma_up=up.rolling(window.periods).mean()
            ma_down=up.rolling(window.periods).mean()

        rsi=ma_up/ma_down
        rsi=100-(100/(1+rsi))
        rsi.fillna(0,inplace=True)

        result = pd.concat([df,rsi],axis=1,join='inner')
        #result = pd.DataFrame(result, columns=['datetime', 'open','high','low','close','vol','rsi'])
        result.columns = ['open','high','low','close','vol','rsi']
        return result #마감 전은 제외


    def get_over_trade(self, df, periods):
        if df['rsi'] > 90: #초초과매수
            return 3
        elif df['rsi'] > 80: #초과매수
            return 2 
        elif df['rsi'] > 70: #과매수
            return 1 
        elif df['rsi'] < 30: #과매도
            return -1
        elif df['rsi'] < 20: #초과매도
            return -2
        elif df['rsi'] < 10: #초초과매도
            return -3
        else:
            return 0 #보통

    def get_cur_rsi(self, df, periods):#현재 rsi 반환
        self.cur_rsi = df['rsi'].iloc[-1]
        return self.cur_rsi

    def get_cur_date(self, df, periods):
        self.cur_date = df.index[-1]
        return self.cur_date


    def judge_rsi(self):
        df_rsi= self.get_rsi(self.get_data(self.periods))
        over_trade_val = self.get_over_trade(df_rsi.iloc[-1], self.periods)
        cur_rsi = self.get_cur_rsi(df_rsi[:-1],self.periods)
        cur_date = self.get_cur_date(df_rsi[:-1],self.periods)
        result=self.periods + " / " + str(cur_date) + " / rsi : " + str(cur_rsi) + " / 상태 : "
        if over_trade_val == 3:
            result += "초초과매수 진입"
        elif over_trade_val == 2:
            result += "초과매수 진입"
        elif over_trade_val == 1:
            result += "과매수 진입"
        elif over_trade_val == -3:
            result += "초초과매도 진입"
        elif over_trade_val == -2:
            result += "초과매도 진입"
        elif over_trade_val == -1:
            result += "과매도 진입"
        else:
            result = "평상시"
        return result



#df_rsi= get_rsi(get_data('1h'))
#over_trade_val = get_over_trade(df_rsi.iloc[-1], periods='1d')
#send_over_trade(over_trade_val)


#instance = DataModel('1h')
#instance.send_over_trade(3)
