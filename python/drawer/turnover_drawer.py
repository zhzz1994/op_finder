from .utils import render_color_bar

class TurnoverRateDrawer:
    """
    绘制换手率
    """
    def __init__(self, stock) -> None: 
        self.times = stock.times
        self.opens = stock.opens
        self.closes = stock.closes
        self.bar_datas = stock.turnover_rate

    def render(self):
        # 涨跌分别绘制
        datas = []
        for i in range(len(self.bar_datas)):
            if self.closes[i] > self.opens[i]:
                datas.append(["green", self.bar_datas[i]])
            else:
                datas.append(["red", self.bar_datas[i]])
        self.chart = render_color_bar(datas, self.times, name="turnover_rate")


class TurnoverCountDrawer:
    """
    绘制换手数量
    """
    def __init__(self, stock) -> None:
        self.times = stock.times
        self.opens = stock.opens
        self.closes = stock.closes
        self.bar_datas = stock.turnover_count

    def render(self):
        # 涨跌分别绘制
        datas = []
        for i in range(len(self.bar_datas)):
            if self.closes[i] > self.opens[i]:
                datas.append(["green", self.bar_datas[i]])
            else:
                datas.append(["red", self.bar_datas[i]])
        self.chart = render_color_bar(datas, self.times, name="turnover_count")