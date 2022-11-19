import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from drawer import CandleDrawer, TurnoverRateDrawer, TurnoverCountDrawer, MACDDrawer, merge_chart


class DayChart:
    def __init__(self, stock, chart_type="log") -> None:
        self.stock = stock
        self.reference = {}
        self.chart_type = chart_type

    def candle_chart(self, min="dataMin", max="dataMax"):
        candle_chart = CandleDrawer(self.stock, y_axis_type=self.chart_type)
        candle_chart.render_base_candle(min=min, max=max)

        candle_chart.render_ema(20)
        candle_chart.render_ema(5)
        candle_chart.render_ma(20)
        candle_chart.render_ma(5)
        if self.reference:
            candle_chart.append_line(name="reference", time=self.reference["times"], data=self.reference["datas"])
        return candle_chart.chart

    def add_reference(self, stock, start_date=""):
        ref_data = stock.get_data(start_date)
        data = self.stock.get_data(start_date)
        start_date = ref_data["times"] if ref_data["times"] > data["times"] else data["times"]
        ref_data = stock.get_data(start_date)
        data = self.stock.get_data(start_date)

        scale = ref_data["closes"] / data["closes"]
        times = []
        closes = []
        for time, close in zip(stock.times, stock.closes):
            if time >= start_date:
                times.append(time)
                closes.append(close / scale)
        self.reference = {"times": times, "datas": closes}

    def turnovers_rate_chart(self):
        turnovers_rate_chart = TurnoverRateDrawer(self.stock)
        turnovers_rate_chart.render()
        return turnovers_rate_chart.chart

    def turnovers_count_chart(self):
        turnovers_count_chart = TurnoverCountDrawer(self.stock)
        turnovers_count_chart.render()
        return turnovers_count_chart.chart

    def macd_chart(self):
        macd_chart = MACDDrawer(self.stock)
        macd_chart.render()
        return macd_chart.chart

    def combine_chart(self):
        candle_chart = self.candle_chart()
        turnovers_count_chart = self.turnovers_count_chart()
        macd_chart = self.macd_chart()
        charts = [{"chart": candle_chart, "height": 600},
            {"chart": turnovers_count_chart, "height": 100},
            {"chart": macd_chart, "height": 150},
        ]
        combine_chart = merge_chart(charts)
        return combine_chart
