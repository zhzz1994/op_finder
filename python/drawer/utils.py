from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid, Line, Timeline
from pyecharts.commons.utils import JsCode


def color_map():
    map = {
        "red": "#ef232a",
        "green": "#14b143",
        "orange": "#FF9900",
        "yellow": "#FFFF33",
        "blue": "#3D5AFF",
        "purple": "#FF27FF",
        "gray": "#666666",
        "white": "#FFFFFF",
        "black": "#000000",
    }
    return map


def color_code(color):
    map = color_map()
    return map.get(color, map["white"])


def color_table(index):
    index = index % len(color_map())
    keys = list(color_map().keys())
    return keys[index]


def render_color_bar(datas, axis, name="bar"):
    """绘制彩色状图
    datas : [[color, data]]
    axis : x轴
    """

    groups = {}
    for color, _ in datas:
        groups[color] = []
    
    for color, data in datas:
        for key,v in groups.items():
            if key == color:
                groups[key].append(data)
            else:
                groups[key].append(0.0)
    
    chart = Bar()
    chart.add_xaxis(xaxis_data = axis)
    for color, values in groups.items():
        chart.add_yaxis(
            series_name="",
            y_axis=values,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color=color_code(color)),
            stack=name,
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
            min_="dataMin", 
            max_="dataMax", 
            min_interval=1,
            split_number=10
        ),
    )
    return chart

def render_line(data, axis, color, name="line"):
    line = (
            Line()
            .add_xaxis(xaxis_data=axis)
            .add_yaxis(
                series_name=name,
                y_axis=data,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5, color=color_code(color), width=2),
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

