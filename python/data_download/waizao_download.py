from operator import concat
import requests
import pandas as pd
import os
import datetime


def sava_csv(data, path):
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    if os.path.exists(path):
        og_data = pd.read_csv(path, dtype={'code':object})
        last_date = og_data["tdate"][-1:].values
        if last_date:
            data = data[data["tdate"] > last_date[0]]
            data = pd.concat([og_data, data])
    data.to_csv(path, index=0)


def RoughTimeDist(start_date, end_date):
    start_date = start_date.split('-')
    end_date = end_date.split('-')

    diff_count = 366 * (int(end_date[0]) - int(start_date[0])) 
    diff_count += 31 * (int(end_date[1]) - int(start_date[1])) 
    diff_count += int(end_date[2]) - int(start_date[2])
    return diff_count


class StockHSADayKlineDataset:
    '''
    从 http://www.waizaowang.com/ 获取沪深京A股数据,处理日线(周线、月线)数据
    '''
    def __init__(self, token, dic, load_info_fun) -> None:
        '''
        token: api凭证
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc/getStockHSADayKLine"
        self.dic = dic
        self.load_info = load_info_fun    #callback function

    def __loadDayKline(self, path):
        data = pd.read_csv(path, dtype={'code':object})
        return data

    def __getDayKline(self, codes, ktype, file_name, start_date):
        '''
        ktype : 101 日线， 102 周线， 103 月线
        更新K线信息
        前复权
        [   'code' : '股票代码'
            'name' : '股票名称'
            'ktype' : 'K线类别'
            'fq' : '复权信息，除沪深京A股、B股、港股外，其余复权值默认为前复权'
            'tdate' : '交易时间'
            'open' : '开盘价'
            'close' : '收盘价'
            'high' : '最高价'
            'low' : '最低价'
            'cjl' : '成交量'
            'cje' : '成交额'
            'hsl' : '换手率']
        '''

        code_str = codes[0]
        for i in range(1, len(codes)):
            code_str += ","
            code_str += codes[i]

        end_date = datetime.datetime.today().date()
        print("update {} from {} to {}".format(code_str,start_date,end_date))

        url = "{}?code={}&ktype={}&fq=1&startDate={}&endDate={}&export=5&token={}&fields=all".format(self.url_head, code_str, ktype, start_date, end_date, self.token)
        response = requests.get(url).json()
        datas = pd.DataFrame(data=response['data'], columns=response['en'])
        
        for code in codes:
            data = datas[datas["code"] == code]
            path = "{}/{}/{}".format(self.dic, code, file_name)
            sava_csv(data, path)
        return datas

    def __getLastUpdateDate(self, path, default="1990-01-01"):
        last_date = default
        if os.path.exists(path):
            data = self.__loadDayKline(path)
            date = data["tdate"][-1:].values
            if date:
                last_date = date[0]
        return last_date

    def __getLastUpdateDates(self, file_name, latest_date):
        info = self.load_info()
        update_index = []
        for code, row in info.iterrows():
            path = "{}/{}/{}".format(self.dic, code, file_name)
            last_date = self.__getLastUpdateDate(path, default=row["ssdate"])
            date_dist = RoughTimeDist(last_date, latest_date)
            update_index.append({"code" : code, "last_date":last_date, "date_dist" : date_dist})
        return update_index

    def __getLatestTime(self):
        data = self.__getDayKline(codes=["000001"], ktype="101", file_name="day_line.csv", start_date="1990-01-01")
        date = data["tdate"][-1:].values
        return date[0]

    def __updateKline(self, latest_date, items_th, ktype, file_name):
        last_dates = self.__getLastUpdateDates(file_name=file_name, latest_date=latest_date)
        last_dates = sorted(last_dates, key=lambda item: item["date_dist"])
        groups = []

        latest_group = []
        for i in range(len(last_dates)-1, 0, -1):
            if last_dates[i]["date_dist"] <= 0:
                continue
            max_items = 0
            if latest_group:
                max_items = max(latest_group, key=lambda item: item["date_dist"])["date_dist"]
            if len(latest_group) >= 50 or max_items * (len(latest_group) + 1) >= items_th:
                groups.append(latest_group)
                latest_group = []
            latest_group.append(last_dates[i])
        if latest_group:
            groups.append(latest_group)
        
        for group in groups:
            codes = []
            for item in group:
                codes.append(item["code"])
            self.__getDayKline(codes=codes, ktype=ktype, file_name=file_name, start_date=group[0]["last_date"])
        return groups

    def update(self):
        latest_date = self.__getLatestTime()
        self.__updateKline(latest_date=latest_date, ktype="101", file_name="day_line.csv", items_th=12000)
        self.__updateKline(latest_date=latest_date, ktype="102", file_name="week_line.csv", items_th=12000)
        self.__updateKline(latest_date=latest_date, ktype="103", file_name="month_line.csv", items_th=12000)

    def loadDayKline(self, code):
        return self.__loadDayKline(path="{}/{}/{}".format(self.dic, code, "day_line.csv"))

    def loadWeekKline(self, code):
        return self.__loadDayKline(path="{}/{}/{}".format(self.dic, code, "week_line.csv"))

    def loadMonthKline(self, code):
        return self.__loadDayKline(path="{}/{}/{}".format(self.dic, code, "month_line.csv"))


class StockHSAHourKlineDataset:
    '''
    从 http://www.waizaowang.com/ 获取沪深京A股时线数据(5分钟、15分钟、30分钟、60分钟数据)
    '''
    def __init__(self, token, dic) -> None:
        '''
        token: api凭证
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc/getStockHSAHourKLine"
        self.dic = dic

    def __getHourKline(self, codes, ktype, file_name, start_date, end_date):
        '''
        ktype : 5 5min, 15 15min, 30 30min, 60 60min
        更新K线信息
        不复权
        [   'code' : '股票代码'
            'tdate': '分时时间'
            'open' : '开盘价'
            'close' : '收盘价'
            'high' : '最高价'
            'low' : '最低价'
            'cjl' : '成交量（手）'
            'cje' : '成交额（元）'
            'cjjj': '成交均价']
        '''
        code_str = codes[0]
        for i in range(1, len(codes)):
            code_str += ","
            code_str += codes[i]

        print("update {} from {} to {}".format(code_str,start_date,end_date))

        url = "{}?code={}&ktype={}&startDate={}&endDate={}&export=5&token={}&fields=all".format(self.url_head, code_str, ktype, start_date, end_date, self.token)
        response = requests.get(url).json()
        datas = pd.DataFrame(data=response['data'], columns=response['en'])
        
        for code in codes:
            data = datas[datas["code"] == code]

            app = []
            tdate = data["tdate"]
            for line in tdate:
                date,time = line.split("T")
                time = time.split(".")
                app.append([line, date, time[0]])
            app = pd.DataFrame(app, columns = ['tdate', 'date','time'])
            data = pd.merge(data, app, on='tdate')
            data = data.rename(columns={'tdate' : 'og_date', 'date' : 'tdate'})

            path = "{}/{}/{}".format(self.dic, code, file_name)
            sava_csv(data, path)
        return datas

    def __updateKline(self, days_th, ktype, file_name, codes, dates):
        groups = []
        latest_group = []
        for code in codes:
            latest_group.append(code)
            if len(latest_group) >= 50:
                groups.append(latest_group)
                latest_group = []
        if latest_group:
            groups.append(latest_group)

        dates = sorted(dates)
        data_gap = []
        for i in range(len(dates)):
            if i % days_th == 0:
                data_gap.append(dates[i])
        if (len(dates) - 1) % days_th != 0:
            data_gap.append(dates[-1])
        
        for group in groups:
            for i in range(len(data_gap) - 1):
                self.__getHourKline(codes=group, ktype=ktype, file_name=file_name, start_date=data_gap[i], end_date=data_gap[i+1])

    def __loadKline(self, path):
        data = pd.read_csv(path, dtype={'code':object})
        return data

    def __getLatestUpdateDate(self):
        path = "{}/{}/{}".format(self.dic, "000001", "hour_kline_log.csv")
        last_date = "2022-01-01"
        if os.path.exists(path):
            data = self.__loadKline(path)
            date = data["tdate"][-1:].values
            if date:
                last_date = date[0]
        return last_date

    def __endUpdate(self):
        '''
        保存文件,用于下次更新
        '''
        path_from = "{}/{}/{}".format(self.dic, "000001", "min60_line.csv")
        path_to = "{}/{}/{}".format(self.dic, "000001", "hour_kline_log.csv")
        data = pd.read_csv(path_from, dtype={'code':object})
        data.to_csv(path_to, index=0)

    def update(self, codes, dates):
        '''
        5min 1day * 50
        15min 1week * 50
        30min 1month * 50
        1hour 1month * 50
        '''
        latest_update_date = self.__getLatestUpdateDate()
        dates_filtered = []
        for date in dates:
            if date > latest_update_date:
                dates_filtered.append(date)

        self.__updateKline(days_th=1, ktype="5", file_name="min5_line.csv", codes=codes, dates=dates_filtered)
        self.__updateKline(days_th=5, ktype="15", file_name="min15_line.csv", codes=codes, dates=dates_filtered)
        self.__updateKline(days_th=20, ktype="30", file_name="min30_line.csv", codes=codes, dates=dates_filtered)
        self.__updateKline(days_th=30, ktype="60", file_name="min60_line.csv", codes=codes, dates=dates_filtered)
        self.__endUpdate()

    def load5MinKline(self, code):
        return self.__loadKline(path="{}/{}/{}".format(self.dic, code, "min5_line.csv"))

    def load15MinKline(self, code):
        return self.__loadKline(path="{}/{}/{}".format(self.dic, code, "min15_line.csv"))

    def load30MinKline(self, code):
        return self.__loadKline(path="{}/{}/{}".format(self.dic, code, "min30_line.csv"))

    def load60MinKline(self, code):
        return self.__loadKline(path="{}/{}/{}".format(self.dic, code, "min60_line.csv"))


class StockHSADataset:
    '''
    从 http://www.waizaowang.com/ 获取沪深京A股数据
    '''
    def __init__(self, token, dic) -> None:
        '''
        token: api凭证
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc"
        self.dic = dic
        self.daylines = StockHSADayKlineDataset(self.token, self.dic, self.loadBaseInfo)
        self.hourlines = StockHSAHourKlineDataset(self.token, self.dic)

    def updataBaseInfo(self, file_name="/base/info.csv"):
        '''
        沪深京A股基本信息。
        [   'code' : '股票代码'
            'name' : '股票名称'
            'stype' : '股票类型 1：深证股票，2：上证股票，3：北证股票，4：港股'
            'hsgt' : '沪深港通 1：沪股通(港>沪)、2：深股通(港>深)、3：港股通(沪>港)、4：港股通(深>港)、5：港股通(深>港或沪>港)'
            'bk' : '所属板块，个股包括主板、创业板、科创板'
            'roe' : 'ROE'
            'zgb' : '总股本（股）'
            'ltgb' : '流通股本（股）'
            'ltsz' : '流通市值（元）'
            'zsz' : '总市值（元）'
            'ssdate' : '上市日期'
            'z50' : '归属行业板块名称'
            'z52' : '归属地域板块名称'
            'z53' : '归属概念板块名称']
        '''
        url = "{}/getStockHSABaseInfo?code=all&export=5&token={}&fields=all".format(self.url_head, self.token)
        response = requests.get(url).json()
        data = pd.DataFrame(data=response['data'], columns=response['en'])

        path = self.dic + file_name
        sava_csv(data, path)
        return data

    def loadBaseInfo(self, file_name="/base/info.csv"):
        path = self.dic + file_name
        data = pd.read_csv(path, dtype={'code':object}, index_col=['code'])
        return data

    def __getAllCodes(self):
        info = self.loadBaseInfo()
        codes = []
        for code, row in info.iterrows():
            codes.append(code)
        return codes

    def __getLatestTradeDate(self):
        data = self.daylines.loadDayKline("000001")
        all_dates = []
        for date in data["tdate"]:
            all_dates.append(date)
        dates = []
        for i in  range(len(all_dates)-50, len(all_dates), 1):
            dates.append(all_dates[i])
        y,m,d = dates[-1].split("-")
        dates.append("{}-01-01".format(str(int(y)+1)))
        return dates

    def updateKlineDataset(self):
        self.daylines.update()
        self.hourlines.update(self.__getAllCodes(), self.__getLatestTradeDate())

    def loadKline(self, code):
        day_kline = self.daylines.loadDayKline(code)
        week_kline = self.daylines.loadWeekKline(code)
        month_kline = self.daylines.loadMonthKline(code)
        min5_kline = self.hourlines.load5MinKline(code)
        min15_kline = self.hourlines.load15MinKline(code)
        min30_kline = self.hourlines.load30MinKline(code)
        min60_kline = self.hourlines.load60MinKline(code)
        return {"day":day_kline, "week": week_kline, "month": month_kline,
                "min5_kline":min5_kline, "min15_kline":min15_kline, "min30_kline":min30_kline, "min60_kline":min60_kline}



