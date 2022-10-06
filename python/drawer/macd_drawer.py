from pyecharts import options as opts
from pyecharts.charts import Kline, Bar, Grid, Line, Timeline
from pyecharts.commons.utils import JsCode

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