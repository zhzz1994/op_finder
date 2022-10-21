import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from .utils import render_color_bar, render_line
from indicator import MACD


class MACDDrawer:
    """绘制MACD chart
    """
    def __init__(self, data) -> None:
        '''
        data = {times, candles, ...}
        candles = [[start, end, low, high]]
        '''
        self.times = data["times"]
        self.candles = data["candles"]

    def __add_bar(self, macd_bar):
        datas = []
        for i in range(len(macd_bar)):
            if macd_bar[i] > 0:
                datas.append(["red", macd_bar[i]])
            else:
                datas.append(["green", macd_bar[i]])
        self.chart = render_color_bar(datas, self.times, name="macd")

    def __add_dea(self, macd_dea):
        line = render_line(macd_dea, self.times, "red", "dea")
        self.chart.overlap(line)

    def __add_diff(self, macd_diff):
        line = render_line(macd_diff, self.times, "orange", "diff")
        self.chart.overlap(line)

    def render(self):
        data_end = [candle[1] for candle in self.candles]
        macd = MACD()(data_end)
        self.__add_bar(macd["bar"])
        self.__add_dea(macd["dea"])
        self.__add_diff(macd["diff"])







