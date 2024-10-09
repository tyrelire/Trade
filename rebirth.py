#!/usr/bin/python3
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

import sys

class Bot:
    def __init__(self):
        self.botState = BotState()
        self.transaction_fee_rate = 0.2 / 100  # 0.2%

    def putTheNumber(self, TheNumber):
        Number = TheNumber
        return Number

    def run(self):
        nbBougie = 0
        range_limit = 20
        moyenne = 0
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)
            moyenne = 0
            if nbBougie > range_limit:
                for pair, chart in self.botState.charts.items():
                    if len(chart.closes) >= range_limit and len(chart.opens) >= range_limit:
                        tabCloses = chart.closes[-range_limit:]
                        tabOpens = chart.opens[-range_limit:]
                        for i in range(range_limit):
                            moyenne += ((tabCloses[i] + tabOpens[i]) / 2)
                        moyenne = moyenne / range_limit
                        print(f'Calculated moyenne: {moyenne}', file=sys.stderr)
                self.botState.moyenne[1] = self.botState.moyenne[0]
                self.botState.moyenne[0] = moyenne
                print(f'Updated moyenne[0]: {self.botState.moyenne[0]}', file=sys.stderr)
                print(f'Updated moyenne[1]: {self.botState.moyenne[1]}', file=sys.stderr)
                # Appeler la méthode act après la mise à jour des moyennes
                self.act()
            
            nbBougie += 1
            print(f'nbBougie: {nbBougie}', file=sys.stderr)

    def parse(self, info: str):
        print(f'Parsing info: {info}', file=sys.stderr)
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        elif tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        elif tmp[0] == "action":
            print("Calling act method", file=sys.stderr)
            self.act()

    def sell(self, maxSell):
        percentage_to_sell = 0.50
        amount_to_sell = percentage_to_sell * self.botState.stacks.get("BTC", 0)
        current_closing_price = self.botState.charts["USDT_BTC"].closes[-1]
        if amount_to_sell < maxSell:
            print('no_moves', flush=True)
            return
        actual_amount_sold = amount_to_sell * (1 - self.transaction_fee_rate)
        self.botState.update_stack("BTC", self.botState.stacks.get("BTC", 0) - amount_to_sell)
        self.botState.update_stack("USDT", self.botState.stacks.get("USDT", 0) + actual_amount_sold * current_closing_price)
        print(f'sell USDT_BTC {amount_to_sell}', flush=True)

    def buy(self, minLost):
        dollars = self.botState.stacks.get("USDT", 0)
        current_closing_price = self.botState.charts["USDT_BTC"].closes[-1]
        affordable = dollars / current_closing_price
        if dollars < minLost:
            print('no_moves', flush=True)
            return
        percentage_to_use = 0.50
        amount_to_buy = percentage_to_use * affordable
        actual_amount_bought = amount_to_buy * (1 - self.transaction_fee_rate)
        self.botState.update_stack("BTC", self.botState.stacks.get("BTC", 0) + actual_amount_bought)
        self.botState.update_stack("USDT", dollars - amount_to_buy * current_closing_price)
        print(f'buy USDT_BTC {amount_to_buy}', flush=True)

    def act(self):
        # Imprimer les valeurs des moyennes avant de prendre des décisions
        print(f'Current moyenne: {self.botState.moyenne[0]}', file=sys.stderr)
        print(f'Previous moyenne: {self.botState.moyenne[1]}', file=sys.stderr)
    
        if self.botState.moyenne[0] > self.botState.moyenne[1]:
            print("Decision: Sell", file=sys.stderr)
            self.sell(150)
        elif self.botState.moyenne[0] < self.botState.moyenne[1]:
            print("Decision: Buy", file=sys.stderr)
            self.buy(150)
        else:
            print('no_moves', flush=True)

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            elif key == "date":
                self.date = int(value)
            elif key == "high":
                self.high = float(value)
            elif key == "low":
                self.low = float(value)
            elif key == "open":
                self.open = float(value)
            elif key == "close":
                self.close = float(value)
            elif key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)

class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)

class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.moyenne = [0, 0]
        self.stacks = dict()
        self.charts = dict()

    def update_chart(self, pair: str, new_candle_str: str):
        if pair not in self.charts:
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        elif key == "time_per_move":
            self.timePerMove = int(value)
        elif key == "candle_interval":
            self.candleInterval = int(value)
        elif key == "candle_format":
            self.candleFormat = value.split(",")
        elif key == "candles_total":
            self.candlesTotal = int(value)
        elif key == "candles_given":
            self.candlesGiven = int(value)
        elif key == "initial_stack":
            self.initialStack = int(value)
        elif key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        elif key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
