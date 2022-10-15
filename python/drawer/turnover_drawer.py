from .utils import render_color_bar

class TurnoverRateDrawer:
    """
    绘制换手率
    """
    def __init__(self, data) -> None:
        '''
        data = {times, turnover_rate, candles, ...}
        candles = [[start, end, low, high]]
        '''   
        self.times = data["times"]
        self.candles = data["candles"]
        self.bar_datas = data["turnover_rate"]

    def render(self):
        # 涨跌分别绘制
        datas = []
        for i in range(len(self.bar_datas)):
            if self.candles[i][0] > self.candles[i][1]:
                datas.append(["green", self.bar_datas[i]])
            else:
                datas.append(["red", self.bar_datas[i]])
        self.chart = render_color_bar(datas, self.times, name="turnover_rate")


class TurnoverCountDrawer:
    """
    绘制换手数量
    """
    def __init__(self, data) -> None:
        '''
        data = {times, turnover_count, candles, ...}
        candles = [[start, end, low, high]]
        '''   
        self.times = data["times"]
        self.candles = data["candles"]
        self.bar_datas = data["turnover_count"]

    def render(self):
        # 涨跌分别绘制
        datas = []
        for i in range(len(self.bar_datas)):
            item = self.bar_datas[i]
            if self.candles[i][0] > self.candles[i][1]:
                datas.append(["green", item])
            else:
                datas.append(["red", item])
        self.chart = render_color_bar(datas, self.times, name="turnover_count")