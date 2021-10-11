import DataModel
import TelegramModel

def get_rsi_message(periods):
    dm_instance = DataModel.DataModel(periods=periods)
    rsi_message = dm_instance.judge_rsi()
    return rsi_message

if __name__ == '__main__':
    bot = TelegramModel.TelegramModel()
    for period in ['1m','5m','15m','30m','1h','4h','1d']:
        text = get_rsi_message(period)
        if text != "":
            bot.send_message(text)

