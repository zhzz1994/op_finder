from json import tool
from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid, Line, Timeline
from pyecharts.faker import Faker
from pyecharts.commons.utils import JsCode

from .commons import calculate_ma

def render_base_candle(data):
    '''
    K线图
    data = {times, candles, ...}
    candles = [[hign, low, start, end]]
    '''

    chart = Kline()
    chart.add_xaxis(xaxis_data = data["times"])
    chart.add_yaxis(
        series_name='',
        y_axis=data["candles"],
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
    chart.set_global_opts(
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
            type_ = 'log', 
            is_scale=True,               
            min_="dataMin", 
            max_="dataMax", 
            # min_=14, 
            # max_=20, 
            min_interval=1,
            split_number=10,
        ),
    )
    return chart


def add_MA5(kline_chart, data):
    data_end = [line[3] for line in data["candles"]]
    ma5_line = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(
            series_name="MA5",
            y_axis=calculate_ma(data=data_end, day_count=5),
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
    # Overlap Kline + Line
    overlap_kline_line = kline_chart.overlap(ma5_line)
    return overlap_kline_line


def add_MA20(kline_chart, data):
    data_end = [line[3] for line in data["candles"]]
    ma_line = (
        Line()
        .add_xaxis(xaxis_data=data["times"])
        .add_yaxis(
            color="red",
            series_name="MA20",
            y_axis=calculate_ma(data=data_end, day_count=20),
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
    # Overlap Kline + Line
    overlap_kline_line = kline_chart.overlap(ma_line)
    return overlap_kline_line


def render_turnover(data):       
    '''
    换手率
    data = {times, turnovers, candles, ...}
    candles = [[hign, low, start, end]]
    '''   
    red_data = []
    green_data = []
    for i in range(len(data["turnovers"])):
        if data["candles"][i][0] >  data["candles"][i][1]:
            red_data.append(data["turnovers"][i])
            green_data.append(0.0);
        else:
            green_data.append(data["turnovers"][i])
            red_data.append(0.0);

    chart = Bar()
    chart.add_xaxis(xaxis_data = data["times"])
    chart.add_yaxis(
        series_name="",
        y_axis=green_data,
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(color='#ef232a'),
        stack="stack1",
    )
    chart.add_yaxis(
        series_name="",
        y_axis=red_data,
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(color='#14b143'),
        stack="stack1",
    )
    chart.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            is_scale=True,
            boundary_gap=False,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            split_number=20,
            min_="dataMin",
            max_="dataMax",
            axislabel_opts=opts.LabelOpts(is_show=False),
        ),
        yaxis_opts = opts.AxisOpts(
            type_ = 'value', 
            is_scale=True, 
            splitline_opts=opts.SplitLineOpts(is_show=True),                 
            min_=0, 
            max_="dataMax", 
            min_interval=1,
            split_number=10
        ),
    )
    return chart


def render_MACD(data):  
    '''
    MACD
    data = {times, macd, ...}
    '''   

    chart = Bar()
    chart.add_xaxis(xaxis_data = data["times"])
    chart.add_yaxis(
        series_name="",
        y_axis=data["macd"],
        label_opts=opts.LabelOpts(is_show=False),
        itemstyle_opts=opts.ItemStyleOpts(
            color=JsCode(
                """
                    function(params) {
                        var colorList;
                        if (params.data >= 0) {
                            colorList = '#ef232a';
                        } else {
                            colorList = '#14b143';
                        }
                        return colorList;
                    }
                """
            )
        )
    )
    chart.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            is_scale=True,
            boundary_gap=False,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            split_number=20,
            min_="dataMin",
            max_="dataMax",
            axislabel_opts=opts.LabelOpts(is_show=False),
        ),
        yaxis_opts = opts.AxisOpts(
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(is_show=True),
        ),
    )
    return chart


def render_time(data):
    '''
    换手率
    data = {times, turnovers, candles, ...}
    candles = [[hign, low, start, end]]
    '''   

    chart = Timeline()
    for i in range(len(data["times"])):
        bar = Bar()
        bar.add_xaxis(Faker.choose())
        bar.add_yaxis("商家A", Faker.values(), label_opts=opts.LabelOpts(position="right"))
        bar.add_yaxis("商家B", Faker.values(), label_opts=opts.LabelOpts(position="right"))
        bar.reversal_axis()
        bar.set_global_opts(
            title_opts=opts.TitleOpts("Timeline-Bar-Reversal {}".format(data["times"][i]))
        )
        chart.add(bar, data["times"][i])
    return chart


def merge_chart(charts):
    grid_chart = Grid(init_opts=opts.InitOpts(width="1400px", height="900px"))
    charts[0].set_global_opts( 
        datazoom_opts = opts.DataZoomOpts(type_="inside", is_show=True, xaxis_index=[0, 1, 2]),
        title_opts=opts.TitleOpts(title="Kline-DataZoom-inside"),
    )
    # K线图
    grid_chart.add(
        charts[0],
        grid_opts=opts.GridOpts(pos_left="3%", pos_right="1%", height="60%"),
    )
    # Volumn 柱状图
    grid_chart.add(
        charts[1],
        grid_opts=opts.GridOpts(
            pos_left="3%", pos_right="1%", pos_top="71%", height="10%"
        ),
    )
    grid_chart.add(
        charts[2],
        grid_opts=opts.GridOpts(
            pos_left="3%", pos_right="1%", pos_top="81%", height="10%"
        ),
    )
    return grid_chart





