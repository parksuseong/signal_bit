import ccxt
from datetime import datetime, timedelta
import pandas as pd



class DataModel():

    def __init__(self, periods='1d', op_type='batch'):
        self.binance = ccxt.binance()
        self.periods = periods

        #init method call
        if op_type == 'batch':
            print('batch type model start')
            #data load
            self.get_origin_data()
            #add rsi
            self.calc_rsi()

            self.cal_divergence()
        else: #realtime use async 
            print('realtime type model start')

    def print_df(self):
        pd.set_option('display.max_row',1000)
        pd.set_option('display.max_columns',100)
        print(self.df)
    
    def save_df_csv(self):
        self.df.to_csv("result.csv",header=True, index=False)

    def get_origin_data(self, exchange='binance'):
        #현재는 exchange가 바낸만 구현
        ohlcvs = self.binance.fetch_ohlcv('BTC/USDT', self.periods)
        #일자, 시가, 고가, 저가, 종가, 거래량
        df = pd.DataFrame(ohlcvs, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df['datetime'] = pd.DatetimeIndex(df['datetime']) + timedelta(hours=9)
        df.set_index('datetime', inplace=True)
        df.reset_index(inplace=True)
        self.df = df

    #to do list    
    def get_tsi(self, s1=25, s2=13, s3=7):
        return self.df


    def get_cur_rsi(self):#현재 rsi 반환
        #self.cur_rsi = self.df['rsi'].iloc[-1]
        return self.df['rsi'].iloc[-1]

    def get_cur_date(self):
        #self.cur_date = self.df.index[-1]
        return self.df.index[-1]

    def get_cur_close(self):
        #self.cur_close = self.df['close'].iloc[-1]
        return self.df['close'].iloc[-1]
    
    def get_cur_high(self):
        return self.df['high'].iloc[-1]

    def get_cur_low(self):
        return self.df['low'].iloc[-1]


    #calculate rsi
    def calc_rsi(self, periods=14, ema=True):
        close_delta=self.df['close'].diff()
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
        rsi = rsi.to_frame()
        rsi.columns = ['rsi']
        
        self.df = pd.concat([self.df,rsi], axis=1, join='inner')
        
        #result = pd.DataFrame(result, columns=['datetime', 'open','high','low','close','vol','rsi'])
        self.df.columns = ['datetime','open','high','low','close','vol','rsi']
    
    #마감봉은 현재 기준 60개 보는것으로 set.
    #현재 다이버전스 상태 여부 리턴 (히든다이버전스 등은 미판단. 그냥 내맘대로 함.)
    #상승다이버전스는 저점은 하락하는데 rsi는 상승하는 상태
    #하락다이버전스는 고점은 상승하는데 rsi는 하락하는 상태
    def cal_divergence(self, lower_barrier=30, upper_barrier=70, width=30):
        latest_rsi=self.df['rsi'].iloc[-2]
        latest_high=self.df['high'].iloc[-2]
        latest_rsi_low=self.df['low'].iloc[-2]
        self.df['diver_up'] = 0
        self.df['diver_down'] = 0

        #bullish
        for i in range(0,len(self.df.index)):        
            try: 
                if self.df['rsi'][i] < lower_barrier:
                    for a in range(i + 1, i + width):
                        if self.df['rsi'][a] > lower_barrier:
                            for r in range(a + 1, a + width):
                                if self.df['rsi'][r] < lower_barrier and self.df['rsi'][r] > self.df['rsi'][i] and self.df['low'][r] < self.df['low'][i]:
                                    for s in range(r + 1, r + width):
                                        if self.df['rsi'][s] > lower_barrier:
                                            print(str(self.df['datetime'][i]) + " " + str(self.df['rsi'][i]) + " " +  str(self.df['high'][i]))
                                            print(str(self.df['datetime'][a]) + " " + str(self.df['rsi'][a]) + " " + str(self.df['high'][a]))
                                            print(str(self.df['datetime'][r]) + " " + str(self.df['rsi'][r]) + " " + str(self.df['high'][r]))
                                            print(str(self.df['datetime'][s]) + " " + str(self.df['rsi'][s]) + " " + str(self.df['high'][s]))
                                            self.df['diver_up'][s + 1] = 1
                                            break
                                        else:
                                            continue
                                else:
                                    continue
                        else:
                            continue
                else:
                    continue
            except IndexError:
                pass
        
        for i in range(0,len(self.df.index)):               
            try:
                if self.df['rsi'][i] > upper_barrier:
                    for a in range(i + 1, i + width):
                        if self.df['rsi'][a] < upper_barrier:
                            for r in range(a + 1, a + width):
                                if self.df['rsi'][r] > upper_barrier and self.df['rsi'][r] < self.df['rsi'][i] and self.df['high'][r] > self.df['high'][i]:
                                    for s in range(r + 1, r + width):
                                        if self.df['rsi'][s] < upper_barrier:
                                            self.df['diver_down'][s + 1] = -1
                                            break
                                        else:
                                            continue
                                else:
                                    continue
                        else:
                            continue
                else:
                    continue
            except IndexError:
                pass
        
        


    def get_over_trade(self, df):
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


    def judge_rsi(self):
        df_rsi= self.calc_rsi(self.get_origin_data())
        over_trade_val = self.get_over_trade(df_rsi.iloc[-1])
        cur_rsi = self.get_cur_rsi(df_rsi[:-1])
        cur_date = self.get_cur_date(df_rsi[:-1])
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



#test
dm = DataModel(periods='1d', op_type='batch')
#dm.print_df()
dm.save_df_csv()
#print(dm.df)
#print(dm.get_cur_low())
#print(dm.get_cur_high())
#print(dm.get_cur_date())
