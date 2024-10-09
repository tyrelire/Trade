#!/usr/bin/python3

import sys

class Trading:
    def __init__(bot):
        bot.state = TradingState()

    def read_input(bot):
        reading = input().strip()
        if reading:
            bot.parse_input(reading)

    def run(bot):
        while True:
            try:
                bot.read_input()
            except EOFError:
                break

    def parse_input(bot, info: str):
        parts = info.split()
        if not parts:
            return

        command = parts[0]
        if command == "settings":
            bot.state.configure_setting(parts[1], parts[2])
        elif command == "update":
            if parts[1] == "game":
                bot.state.update_game_state(parts[2], parts[3])
        elif command == "action":
            bot.handle_action()
        
    def is_order_valid(bot, action, amount):
    if action == "sell" and amount > bot.btc_balance:
        return False
    if action == "buy" and amount > bot.wallet.get("USDT", 0):
        return False
    return True

def handle_action(bot):
    affordable_amount = bot.state.calculate_affordable_amount()
    if bot.state.is_upward_trend():
        if is_order_valid(bot, "buy", affordable_amount):
            bot.buy_bitcoin(affordable_amount)
        else:
            print('pass', flush=True)
    else:
        if is_order_valid(bot, "sell", bot.btc_balance):
            bot.sell_bitcoin()
        else:
            print('pass', flush=True)

    # def handle_action(bot):
    #     affordable_amount = bot.state.calculate_affordable_amount()
    #     if bot.state.is_upward_trend():
    #         bot.state.buy_bitcoin(affordable_amount)
    #     else:
    #         bot.state.sell_bitcoin()

class TradingState:
    def __init__(bot):
        bot.initialize_time_related_attributes()
        bot.initialize_market_related_attributes()

    def initialize_time_related_attributes(bot):
        bot.time_bank_ms = 0
        bot.max_time_bank_ms = 0
        bot.time_per_move_ms = 1
        bot.current_date = 0

    def initialize_market_related_attributes(bot):
        bot.candle_interval_min = 1
        bot.candle_attributes = []
        bot.total_candles = 0
        bot.received_candles = 0
        bot.initial_balance = 0
        bot.transaction_fee_percentage = 0.1
        bot.btc_balance = 0
        bot.wallet = {}
        bot.market_data = {}

    def update_market_data(bot, trading_pair: str, candle_data: str):
        if trading_pair not in bot.market_data:
            bot.market_data[trading_pair] = TradingChart()
        candle = MarketCandle(bot.candle_attributes, candle_data)
        bot.market_data[trading_pair].add_candle(candle)

    def update_wallet_balance(bot, currency: str, amount: float):
        bot.wallet[currency] = amount

    def configure_setting(bot, setting_key: str, setting_value: str):
        settings_map = {
            "timebank": lambda val: setattr(bot, 'max_time_bank_ms', int(val)) or setattr(bot, 'time_bank_ms', int(val)),
            "time_per_move": lambda val: setattr(bot, 'time_per_move_ms', int(val)),
            "candle_interval": lambda val: setattr(bot, 'candle_interval_min', int(val)),
            "candle_format": lambda val: setattr(bot, 'candle_attributes', val.split(",")),
            "candles_total": lambda val: setattr(bot, 'total_candles', int(val)),
            "candles_given": lambda val: setattr(bot, 'received_candles', int(val)),
            "initial_stack": lambda val: setattr(bot, 'initial_balance', int(val)),
            "transaction_fee_percent": lambda val: setattr(bot, 'transaction_fee_percentage', float(val))
        }

        if setting_key in settings_map:
            settings_map[setting_key](setting_value)

    def update_game_state(bot, update_key: str, update_value: str):
        if update_key == "next_candles":
            new_candles_data = update_value.split(";")
            bot.current_date = int(new_candles_data[0].split(",")[1])
            for candle_data in new_candles_data:
                trading_pair = candle_data.split(",")[0]
                bot.update_market_data(trading_pair, candle_data)
        elif update_key == "stacks":
            stack_entries = update_value.split(",")
            for stack_entry in stack_entries:
                currency, amount = stack_entry.split(":")
                bot.update_wallet_balance(currency, float(amount))

    def calculate_affordable_amount(bot):
        usd_balance = bot.wallet.get("USDT", 0)
        current_price = bot.market_data["USDT_BTC"].closes[-1] if "USDT_BTC" in bot.market_data else 0
        return usd_balance / current_price if current_price > 0 else 0

    def buy_bitcoin(bot, affordable_amount):
        bot.btc_balance += affordable_amount * 0.199
        print(f'buy USDT_BTC {0.20 * affordable_amount}', flush=True)

    # def buy_bitcoin(bot, affordable_amount, conversion_rate):
    #     bot.btc_balance += affordable_amount * conversion_rate
    #     print(f'buy USDT_BTC {conversion_rate * affordable_amount}', flush=True)

    def sell_bitcoin(bot):
        if bot.btc_balance > 0:
            print(f'sell USDT_BTC {bot.btc_balance}', flush=True)
            bot.btc_balance = 0
        else:
            print('no_moves', flush=True)

    def is_upward_trend(bot):
        return all(
            bot.market_data["USDT_BTC"].opens[-i] > bot.market_data["USDT_BTC"].opens[-(i + 1)]
            for i in range(1, 6)
        )

class MarketCandle:
    def __init__(bot, attributes, data):
        tmp = data.split(",")
        attribute_mapping = {
            "pair": lambda val: setattr(bot, 'pair', val),
            "date": lambda val: setattr(bot, 'date', int(val)),
            "high": lambda val: setattr(bot, 'high', float(val)),
            "low": lambda val: setattr(bot, 'low', float(val)),
            "open": lambda val: setattr(bot, 'open', float(val)),
            "close": lambda val: setattr(bot, 'close', float(val)),
            "volume": lambda val: setattr(bot, 'volume', float(val))
        }
        for i, key in enumerate(attributes):
            if key in attribute_mapping:
                attribute_mapping[key](tmp[i])

    def __repr__(bot):
        return f"{bot.pair} {bot.date} {bot.close} {bot.volume}"

class TradingChart:
    def __init__(bot):
        bot.dates = []
        bot.opens = []
        bot.highs = []
        bot.lows = []
        bot.closes = []
        bot.volumes = []

    def add_candle(bot, candle: MarketCandle):
        bot.dates.append(candle.date)
        bot.opens.append(candle.open)
        bot.highs.append(candle.high)
        bot.lows.append(candle.low)
        bot.closes.append(candle.close)
        bot.volumes.append(candle.volume)

class TradingSettings:
    def __init__(bot):
        bot.max_time_bank_ms = 0
        bot.time_bank_ms = 0
        bot.time_per_move_ms = 1
        bot.candle_interval_min = 1
        bot.candle_attributes = []
        bot.total_candles = 0
        bot.received_candles = 0
        bot.initial_balance = 0
        bot.transaction_fee_percentage = 0.1

class Wallet:
    def __init__(bot):
        bot.wallet = {}

    def update_wallet_balance(bot, currency: str, amount: float):
        bot.wallet[currency] = amount

class GameState:
    def __init__(bot):
        bot.current_date = 0
        bot.market_data = {}

    def update_market_data(bot, trading_pair: str, candle_data: str):
        if trading_pair not in bot.market_data:
            bot.market_data[trading_pair] = TradingChart()
        candle = MarketCandle(bot.candle_attributes, candle_data)
        bot.market_data[trading_pair].add_candle(candle)

class Settings:
    def __init__(bot):
        bot.max_time_bank_ms = 0
        bot.time_bank_ms = 0
        bot.time_per_move_ms = 1
        bot.candle_interval_min = 1
        bot.candle_attributes = []
        bot.total_candles = 0
        bot.received_candles = 0
        bot.initial_balance = 0
        bot.transaction_fee_percentage = 0.1

    def configure_setting(bot, setting_key: str, setting_value: str):
        settings_map = {
            "timebank": lambda val: setattr(bot, 'max_time_bank_ms', int(val)) or setattr(bot, 'time_bank_ms', int(val)),
            "time_per_move": lambda val: setattr(bot, 'time_per_move_ms', int(val)),
            "candle_interval": lambda val: setattr(bot, 'candle_interval_min', int(val)),
            "candle_format": lambda val: setattr(bot, 'candle_attributes', val.split(",")),
            "candles_total": lambda val: setattr(bot, 'total_candles', int(val)),
            "candles_given": lambda val: setattr(bot, 'received_candles', int(val)),
            "initial_stack": lambda val: setattr(bot, 'initial_balance', int(val)),
            "transaction_fee_percent": lambda val: setattr(bot, 'transaction_fee_percentage', float(val))
        }

        if setting_key in settings_map:
            settings_map[setting_key](setting_value)

if __name__ == "__main__":
    bot = Trading()
    bot.run()
