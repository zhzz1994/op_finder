from pyecharts import options as opts
from pyecharts.charts import Kline, Line

from ..indicator import MA

class CandleDrawer:
    """
    绘制蜡烛图
    """
    def __init__(self, data, y_axis_type="log") -> None:
        '''
        data = {times, candles, ...}
        candles = [[start, end, low, high]]
        y_axis = y轴类型["log", "value"]
        '''
        self.chart = Kline()
        self.times = data["times"]
        self.candles = data["candles"]
        self.y_axis_type = y_axis_type

        self.colors = ["red", "yellow"]
        self.color_id = 0

    def render_base_candle(self):
        '''
        渲染基础的蜡烛图
        '''
        self.chart.add_xaxis(xaxis_data = self.times)
        self.chart.add_yaxis(
            series_name='',
            y_axis=self.candles,
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
            title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
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
                min_="dataMin", 
                max_="dataMax", 
                # min_=14, 
                # max_=20, 
                # min_interval=1,
                # split_number=10,
            ),
        )

    def __render_ma(self, name, ma_data, color):
        line = (
            Line()
            .add_xaxis(xaxis_data=self.times)
            .add_yaxis(
                color=color,
                series_name=name,
                y_axis=ma_data,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=1,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=1,
                    split_number=3,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
            )
        )
        return line
            
        overlap_kline_line = kline_chart.overlap(ma5_line)


    def render_ma(self, n=5):
        '''
        在蜡烛图上绘制移动平均线
        '''
        name = "MA{}".format(n)
        ma_data = MA(n)(self.candles)

        #颜色轮换
        color = self.colors[self.color_id % len(self.colors)]
        self.color_id += 1

        ma_line= self.__render_ma(name=name, ma_data=ma_data, color=color)
        # Overlap candle + ma line
        self.chart = self.chart.overlap(ma_line)
