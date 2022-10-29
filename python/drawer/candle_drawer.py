import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from pyecharts import options as opts
from pyecharts.charts import Kline, Line

from .utils import color_table, render_line

from indicator import MA, EMA

class CandleDrawer:
    """
    绘制蜡烛图
    """
    def __init__(self, stock, y_axis_type="log", title = "") -> None:
        '''
        y_axis = y轴类型["log", "value"]
        '''
        self.chart = Kline()
        self.stock = stock
        self.y_axis_type = y_axis_type
        self.title = title

        self.colors = ["red", "yellow"]
        self.color_id = 0

    def __next_color(self):
        #颜色轮换
        self.color_id += 1
        return color_table(self.color_id)

    def render_base_candle(self, min="dataMin", max="dataMax"):
        '''
        渲染基础的蜡烛图
        '''
        candles = [item for item in zip(self.stock.opens, self.stock.closes, self.stock.lows, self.stock.highs)]
        # for open, close, low, high in zip(self.stock.opens, self.stock.closes, self.stock.lows, self.stock.highs):
        #     # if open == 0.0 and close == 0.0 and low == 0.0 and high == 0.0:
        #     #     candles.append(["-", "-", "-", "-"])
        #     # else:
        #     #     candles.append([open, close, low, high])
        #     candles.append([open, close, low, high])
        self.chart.add_xaxis(xaxis_data = self.stock.times)
        self.chart.add_yaxis(
            series_name='',
            y_axis=candles,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            ),
            # markpoint_opts=opts.MarkPointOpts(
            #     data=[
            #         opts.MarkPointItem(type_="max", name="最大值"),
            #         opts.MarkPointItem(type_="min", name="最小值"),
            #     ]
            # ),
            markline_opts=opts.MarkLineOpts(
                label_opts=opts.LabelOpts(
                    position="middle", color="blue", font_size=15
                ),
                symbol=["circle", "none"],
            ),
        )
        self.chart.set_global_opts(
            title_opts=opts.TitleOpts(title=self.title, pos_left="0"),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts = opts.AxisOpts(
                type_ = self.y_axis_type, 
                is_scale=True,               
                min_=min, 
                max_=max, 
                min_interval=1,
                split_number=10,
                minor_split_line_opts = opts.MinorSplitLineOpts(
                    is_show=True, # 是否显示次分隔线。默认不显示。
                    width = 1,       # 次分隔线线宽。
                    linestyle_opts = opts.LineStyleOpts(color = "#33C7FF", type_= "dotted", opacity=0.8)
                )
            ),
        )

    def append_line(self, name, data, color):
        line = render_line(data, self.stock.times, color, name)
        self.chart = self.chart.overlap(line)

    def render_ma(self, n=5):
        '''
        在蜡烛图上绘制移动平均线
        '''
        name = "MA{}".format(n)
        line = MA(n)(self.stock.closes)

        color = self.__next_color()
        self.append_line(name, line, color)

    def render_ema(self, n=5):
        '''
        在蜡烛图上绘制EMA
        '''
        name = "EMA{}".format(n)
        line = EMA(n)(self.stock.closes)

        color = self.__next_color()
        self.append_line(name, line, color)

