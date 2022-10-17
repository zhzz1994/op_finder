class MA:
    """MA: Moving Average, 移動平均線
    简单移动平均线指标,简单收盘价平均
    """
    def __init__(self, n=5) -> None:
        self.n = n
        self.count = 0
        self.sum = 0
        self.range_data = []

    def __call__(self, datas):
        result = []
        for item in datas:
            result.append(self.get_next(item))
        return result

    def get_next(self, item):
        """返回下一步结果
        早于n的日期i,结果为 data[:i] 平均价格
        item: 输入数据
        """
        self.sum += item
        self.count += 1
        self.range_data.append(item)
        if self.count <= self.n:
            return self.sum / (self.count)
        else:
            prev = self.range_data.pop(0)
            self.sum -= prev
            return self.sum / self.n


class EMA:
    """EMA(Exponential Moving Average)指数平均数指标
        EMA(n) = (n-1/n+1)*EMA(n-1) + (2/n+1)*data[n]
    """
    def __init__(self, n) -> None:
        self.count = 0
        self.ema = 0
        self.n = n
        self.beta = (n - 1) / (n + 1) 

    def __call__(self, datas):
        result = []
        for item in datas:
            result.append(self.get_next(item))
        return result

    def get_next(self, item):
        self.count += 1
        if self.count > 1:
            self.ema = self.ema * (self.beta) + (1 - self.beta) * item
        else:
            self.ema = item
        return self.ema