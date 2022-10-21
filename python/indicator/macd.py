from .moving_average import EMA

class MACD:
    """
    MACD(Moving Average Convergence and Divergence)
    利用收盘价的短期(常用为12日)指数移动平均线与长期(常用为26日)指数移动平均线之间的聚合与分离状况，对买进、卖出时机作出研判的技术指标。
    """
    def __init__(self, short=10, long=20, dea=5) -> None:
        """
        短线默认使用2周数据,长线默认使用4周数据
        """
        self.short = 10
        self.long = 20
        self.ema_short = EMA(self.short)
        self.ema_long = EMA(self.long)
        self.ema_diff= EMA(dea)

    def __call__(self, datas):
        """
        return
            diff,dea,bar
        """
        result = {"diff" : [], "dea" : [], "bar" : []}
        for item in datas:
            diff, dea, bar = self.get_next(item)
            result["diff"].append(diff)
            result["dea"].append(dea)
            result["bar"].append(bar)
        return result

    def get_next(self, item):
        """
        return
            diff,dea,bar
        """
        # diff = EMA(short) - EMA(long)
        diff = self.ema_short.get_next(item) - self.ema_long.get_next(item)
        dea = self.ema_diff.get_next(diff)
        bar = 2 * (diff - dea)
        return diff, dea, bar