from abc import ABC, abstractmethod


class Stock(ABC):
    @abstractmethod
    def day(self):
        """{"times": times, "candles": candles, "turnover_rate": turnover_rate, "turnover_count": turnover_count}
        """
        pass

    @abstractmethod
    def week(self):
        pass

    @abstractmethod
    def month(self):
        pass

    @abstractmethod
    def min5(self):
        pass

    @abstractmethod
    def min15(self):
        pass

    @abstractmethod
    def min30(self):
        pass

    @abstractmethod
    def min60(self):
        pass