class Stock:
    def __init__(self, datas) -> None:
        self.og_datas = datas
        self.keys = []
        for key in datas:
            self.__dict__[key] = self.og_datas[key]
            if key != "times":
                self.keys.append(key)

    def __reset_datas(self):
        for key in self.og_datas:
            self.__dict__[key] = []

    def __append_zero(self):
        for key in self.keys:
            self.__dict__[key].append(0.0)

    def __append_data(self, index):
        for key in self.keys:
            self.__dict__[key].append(self.og_datas[key][index])

    def sync_times(self, times):
        """更改时间轴,截断或者填0"""
        self.__reset_datas()
        for time in times:
            self.times.append(time)
            if time in self.og_datas["times"]:
                index = self.og_datas["times"].index(time)
                self.__append_data(index)
            else:
                self.__append_zero()
