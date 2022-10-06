from pyecharts.charts import Kline, Bar, Grid, Line, Timeline
from pyecharts import options as opts

def merge_chart(charts, width=1400, gap=40):
    """
    合并多个表格
    charts = [{chart, height(px)}, ...]
    width : 宽度(px)
    gap : 每个表格间隙(px)
    """
    total_height = gap
    xaxis_index = []
    for i in range(len(charts)):
        xaxis_index.append(i)
        total_height += charts[i]["height"]
        total_height += gap

    grid_chart = Grid(init_opts=opts.InitOpts(width="{}px".format(width), height="{}px".format(total_height)))
    charts[0]["chart"].set_global_opts( 
        datazoom_opts = opts.DataZoomOpts(type_="inside", is_show=False, xaxis_index=xaxis_index),
        title_opts=opts.TitleOpts(title="Kline"),
    )

    buttom = gap
    for i in range(len(charts)):
        top_px = "{}px".format(buttom)
        height_px = "{}px".format(charts[i]["height"])
        grid_chart.add(
            charts[i]["chart"],
            grid_opts=opts.GridOpts(
                pos_left="4%", pos_right="1%", pos_top=top_px, height=height_px
            ),
        )
        buttom += gap + charts[i]["height"]
    return grid_chart