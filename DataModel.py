import ccxt
from datetime import datetime, timedelta
import pandas as pd



class DataModel():

    def __init__(self, periods='1d', op_type='batch'):
        self.binance = ccxt.binance()
        self.periods = periods
        
        #current divergence variable
        self.divergence=0 #zero not, plus upper, minus down
        self.cur_diver_experimental_datetime=''
        self.cur_diver_control_datetime=''
        self.cur_diver_experimental_rsi=''
        self.cur_diver_control_rsi=''
        self.cur_diver_experimental_price=''
        self.cur_diver_control_price=''
        
        #latest divergence variable
        self.lastest_upper_diver_experimental_datetime=''
        self.lastest_upper_diver_control_datetime=''
        self.lastest_upper_diver_experimental_rsi=''
        self.lastest_upper_diver_control_rsi=''
        self.lastest_upper_diver_experimental_price=''
        self.lastest_upper_diver_control_price=''
        self.lastest_down_diver_experimental_datetime=''
        self.lastest_down_diver_control_datetime=''
        self.lastest_down_diver_experimental_rsi=''
        self.lastest_down_diver_control_rsi=''
        self.lastest_down_diver_experimental_price=''
        self.lastest_down_diver_control_price=''
        

        #init method call
        if op_type == 'batch':
            print(self.periods + ' batch type model start')
            #data load
            self.get_origin_data()
            #add rsi
            self.calc_rsi()

            self.cal_ma(7)
            self.cal_rsi_ma(7)

            #self.cal_lastest_upper_divergence()
            #self.cal_lastest_down_divergence()
            #self.print_lastest_divergence()
            
        else: #realtime use async 
            print('realtime type model start')

    def print_lastest_divergence(self):
        print("가장 최근의 {}봉 상승 다이버".format(self.periods))
        print("기준:"+ self.lastest_upper_diver_experimental_datetime + '/rsi:' + self.lastest_upper_diver_experimental_rsi + '/low:' + self.lastest_upper_diver_experimental_price)
        print("비교:"+ self.lastest_upper_diver_control_datetime + '/rsi:' + self.lastest_upper_diver_control_rsi + '/low:' + self.lastest_upper_diver_control_price)

        print("가장 최근의 {}봉 하락 다이버".format(self.periods))
        print("기준:"+ self.lastest_down_diver_experimental_datetime + '/rsi:' + self.lastest_down_diver_experimental_rsi + '/high:' + self.lastest_down_diver_experimental_price)
        print("비교:"+ self.lastest_down_diver_control_datetime + '/rsi:' + self.lastest_down_diver_control_rsi + '/high:' + self.lastest_down_diver_control_price)

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
    
    
    def get_cur_divergence(self, lower_barrier=30, upper_barrier=70, width=14, hop=7):
        #bullish judge
        for i in reversed(range(len(self.df.index)-2,len(self.df.index)-1)): #one time
            if self.df['rsi'][i] > lower_barrier and \
                self.df['rsi'][i] < self.df['rsi'][i+1] and self.df['rsi'][i] < self.df['rsi'][i-1] and \
                    self.df['low'][i] < self.df['low'][i-1]:
                for j in reversed(range(i-width,i-hop)):
                    Verification=True
                    for k in range(j,i):#must be the highest during the period. Verification!
                        if self.df['low'][i] > self.df['low'][k]:
                            Verification=False
                            break
                    if Verification == True and self.df['rsi'][j] < lower_barrier and \
                        self.df['rsi'][j] < self.df['rsi'][j+1] and self.df['rsi'][j] < self.df['rsi'][j-1] and \
                            self.df['low'][j] < self.df['low'][j-1] and \
                                self.df['low'][i] < self.df['low'][j]:
                                self.divergence=1
                                self.cur_diver_experimental_datetime=str(self.df['datetime'][i])
                                self.cur_diver_experimental_rsi=str(self.df['rsi'][i])
                                self.cur_diver_experimental_price=str(self.df['low'][i])  
                                self.cur_diver_control_datetime=str(self.df['datetime'][j])
                                self.cur_diver_control_rsi=str(self.df['rsi'][j])
                                self.cur_diver_control_price=str(self.df['low'][j])
                                return



        #bearish judge
        for i in reversed(range(len(self.df.index)-2,len(self.df.index)-1)): #one time
            if self.df['rsi'][i] < upper_barrier and \
                self.df['rsi'][i] > self.df['rsi'][i+1] and self.df['rsi'][i] > self.df['rsi'][i-1] and \
                    self.df['high'][i] > self.df['high'][i-1]:
                for j in reversed(range(i-width,i-hop)):
                    Verification=True
                    for k in range(j,i):#must be the highest during the period. Verification!
                        if self.df['high'][i] <= self.df['high'][k]:
                            Verification=False
                            break
                    if Verification == True and self.df['rsi'][j] > upper_barrier and \
                        self.df['rsi'][j] > self.df['rsi'][j+1] and self.df['rsi'][j] > self.df['rsi'][j-1] and \
                            self.df['high'][j] > self.df['high'][j-1] and \
                                self.df['high'][i] > self.df['high'][j]:
                                self.divergence=-1
                                self.cur_diver_experimental_datetime=str(self.df['datetime'][i])
                                self.cur_diver_experimental_rsi=str(self.df['rsi'][i])
                                self.cur_diver_experimental_price=str(self.df['low'][i])  
                                self.cur_diver_control_datetime=str(self.df['datetime'][j])
                                self.cur_diver_control_rsi=str(self.df['rsi'][j])
                                self.cur_diver_control_price=str(self.df['low'][j])
                                return 

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

    #calculate ma_%
    def cal_ma(self,periods):
        col_nm="ma_{}".format(periods)
        col_df = self.df['close'].rolling(window=periods).mean()
        self.df.insert(len(self.df.columns), col_nm, col_df)

    def cal_rsi_ma(self,periods):
        col_nm="rsi_ma_{}".format(periods)
        col_df = self.df['rsi'].rolling(window=periods).mean()
        self.df.insert(len(self.df.columns), col_nm, col_df)
    
    #마감봉은 현재 기준 60개 보는것으로 set.
    #현재 다이버전스 상태 여부 리턴 (히든다이버전스 등은 미판단. 그냥 내맘대로 함.)
    #상승다이버전스는 저점은 하락하는데 rsi는 상승하는 상태
    #하락다이버전스는 고점은 상승하는데 rsi는 하락하는 상태
    def cal_lastest_upper_divergence(self, lower_barrier=30, upper_barrier=70, width=14, hop=7):
        latest_rsi=self.df['rsi'].iloc[-2]
        latest_high=self.df['high'].iloc[-2]
        latest_rsi_low=self.df['low'].iloc[-2]

        #bullish judge
        for i in reversed(range(0,len(self.df.index)-1)):
            if self.df['rsi'][i] > lower_barrier and \
                self.df['rsi'][i] < self.df['rsi'][i+1] and self.df['rsi'][i] < self.df['rsi'][i-1] and \
                    self.df['low'][i] < self.df['low'][i-1]:
                for j in reversed(range(i-width,i-hop)):
                    Verification=True
                    for k in range(j,i):#must be the highest during the period. Verification!
                        if self.df['low'][i] > self.df['low'][k]:
                            Verification=False
                            break
                    if Verification == True and self.df['rsi'][j] < lower_barrier and \
                        self.df['rsi'][j] < self.df['rsi'][j+1] and self.df['rsi'][j] < self.df['rsi'][j-1] and \
                            self.df['low'][j] < self.df['low'][j-1] and \
                                self.df['low'][i] < self.df['low'][j]:
                                self.lastest_upper_diver_experimental_datetime=str(self.df['datetime'][i])
                                self.lastest_upper_diver_experimental_rsi=str(self.df['rsi'][i])
                                self.lastest_upper_diver_experimental_price=str(self.df['low'][i])  
                                self.lastest_upper_diver_control_datetime=str(self.df['datetime'][j])
                                self.lastest_upper_diver_control_rsi=str(self.df['rsi'][j])
                                self.lastest_upper_diver_control_price=str(self.df['low'][j])
                                return

    def cal_lastest_down_divergence(self, lower_barrier=30, upper_barrier=70, width=14, hop=7):
            latest_rsi=self.df['rsi'].iloc[-2]
            latest_high=self.df['high'].iloc[-2]
            latest_rsi_low=self.df['low'].iloc[-2]

            #bearish judge
            for i in reversed(range(0,len(self.df.index)-1)):
                if self.df['rsi'][i] < upper_barrier and \
                    self.df['rsi'][i] > self.df['rsi'][i+1] and self.df['rsi'][i] > self.df['rsi'][i-1] and \
                        self.df['high'][i] > self.df['high'][i-1]:
                    for j in reversed(range(i-width,i-hop)):
                        Verification=True
                        for k in range(j,i):#must be the highest during the period. Verification!
                            if self.df['high'][i] <= self.df['high'][k]:
                                Verification=False
                                break
                        if Verification == True and self.df['rsi'][j] > upper_barrier and \
                            self.df['rsi'][j] > self.df['rsi'][j+1] and self.df['rsi'][j] > self.df['rsi'][j-1] and \
                                self.df['high'][j] > self.df['high'][j-1] and \
                                    self.df['high'][i] > self.df['high'][j]:
                                    self.lastest_down_diver_experimental_datetime=str(self.df['datetime'][i])
                                    self.lastest_down_diver_experimental_rsi=str(self.df['rsi'][i])
                                    self.lastest_down_diver_experimental_price=str(self.df['high'][i])  
                                    self.lastest_down_diver_control_datetime=str(self.df['datetime'][j])
                                    self.lastest_down_diver_control_rsi=str(self.df['rsi'][j])
                                    self.lastest_down_diver_control_price=str(self.df['high'][j])
                                    return 


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
#dm = DataModel(periods='1d', op_type='batch')

#dm.print_df()
#dm.save_df_csv()
#print(dm.df)
#print(dm.get_cur_low())
#print(dm.get_cur_high())
#print(dm.get_cur_date())
