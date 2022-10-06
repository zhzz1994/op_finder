


class MA:
    """MA: Moving Average, 移動平均線
    简单移动平均线指标,简单收盘价平均
    """
    def __init__(self, n=5) -> None:
        self.n = n

    def __call__(self, candles):
        '''
        candles = [[start, end, low, high]]
        早于n的日期i,结果为 data[:i] 平均价格
        '''
        result = []
        sum_total = 0
        for i in range(len(candles)):
            sum_total += candles[i][1]
            if i < self.n:
                ma = sum_total / (i + 1)
            else:
                sum_total -= candles[i - self.n][1]
                ma = sum_total / self.n
            result.append(ma)
        return result
