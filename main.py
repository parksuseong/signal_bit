import DataModel
import TelegramModel

def get_rsi_message(periods,market):
    dm_instance = DataModel.DataModel(periods=periods, market=market)
    divergence = 0
    divergence = dm_instance.get_cur_divergence()
    periods = dm_instance.periods
    market = dm_instance.market
    dm_instance.cur_diver_experimental_datetime
    dm_instance.cur_diver_control_datetime
    dm_instance.cur_diver_experimental_rsi
    dm_instance.cur_diver_control_rsi
    dm_instance.cur_diver_experimental_price
    dm_instance.cur_diver_control_price
    
    rsi_message = "기준:" + dm_instance.cur_diver_experimental_datetime + "/price:" + dm_instance.cur_diver_experimental_price + "/rsi:" + dm_instance.cur_diver_experimental_rsi
    rsi_message = rsi_message + "\n"
    rsi_message = rsi_message + "비교:" + dm_instance.cur_diver_control_datetime + "/price:" + dm_instance.cur_diver_control_price + "/rsi:" + dm_instance.cur_diver_control_rsi

    if divergence == 1 :#upper
        return market + " " + periods + "봉 상승 다이버 포착 \n" + rsi_message
    elif divergence == -1:
        return market + " " + periods + "봉 하락 다이버 포착 \n" + rsi_message
    else:
        return ""
    

if __name__ == '__main__':
    bot = TelegramModel.TelegramModel()
    for period in ['5m','15m','30m','1h','4h']:
        for market in ['BTC/USDT','XRP/USDT','ETH/USDT','LINK/USDT']:
            text = get_rsi_message(period,market)
            if text != "":
                bot.send_message(text)


