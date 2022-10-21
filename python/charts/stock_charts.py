import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from drawer import CandleDrawer, TurnoverRateDrawer, TurnoverCountDrawer, MACDDrawer, merge_chart


class DayChart:
    '''
    '''
    def __init__(self, data) -> None:
        self.data = data

    def candle_chart(self):
        candle_chart = CandleDrawer(self.data)
        candle_chart.render_base_candle()

        candle_chart.render_ema(20)
        candle_chart.render_ema(5)
        candle_chart.render_ma(20)
        candle_chart.render_ma(5)
        return candle_chart.chart

    def turnovers_rate_chart(self):
        turnovers_rate_chart = TurnoverRateDrawer(self.data)
        turnovers_rate_chart.render()
        return turnovers_rate_chart.chart

    def turnovers_count_chart(self):
        turnovers_count_chart = TurnoverCountDrawer(self.data)
        turnovers_count_chart.render()
        return turnovers_count_chart.chart

    def macd_chart(self):
        macd_chart = MACDDrawer(self.data)
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
