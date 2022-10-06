from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid, Line, Timeline
from pyecharts.commons.utils import JsCode


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
