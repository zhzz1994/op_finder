
class EMA:
    """EMA(Exponential Moving Average)指数平均数指标
    """
    def __init__(self) -> None:
        pass


class MACD:
    """
    MACD(Moving Average Convergence and Divergence)
    利用收盘价的短期(常用为12日)指数移动平均线与长期(常用为26日)指数移动平均线之间的聚合与分离状况，对买进、卖出时机作出研判的技术指标。
    """
    def __init__(self, short=10, long=20) -> None:
        """
        短线默认使用2周数据,长线默认使用4周数据
        """
        self.short = 10
        self.long = 20

    def __call__(self, dayline):
        """
        MACD只能用日线计算
        """



        pass