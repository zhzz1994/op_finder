from operator import concat
import requests
import pandas as pd
import os
import datetime

from .stock import Stock


def RoughTimeDist(start_date, end_date):
    start_date = start_date.split('-')
    end_date = end_date.split('-')

    diff_count = 366 * (int(end_date[0]) - int(start_date[0])) 
    diff_count += 31 * (int(end_date[1]) - int(start_date[1])) 
    diff_count += int(end_date[2]) - int(start_date[2])
    return diff_count


class DayKlineDownloader:
    '''
    从 http://www.waizaowang.com/ 获取数据,处理日线(周线、月线)数据
    '''
    def __init__(self, token, dic, url_suffix, file_name, ktype) -> None:
        '''
        token: api凭证
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc/{}".format(url_suffix)
        self.dic = dic
        self.file_name = file_name
        self.ktype = ktype
        self.items_th = 12000

    def __getPath(self, code):
        path = "{}/{}/{}".format(self.dic, code, self.file_name)
        return path

    def __saveKline(self, data, code):
        path = self.__getPath(code)
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        if os.path.exists(path):
            og_data = pd.read_csv(path, dtype={'code':object})
            og_data = og_data[:-1] #先删除最后一行，因为month、week的kline最后一行也许不是周尾/月尾，需要更新
            last_date = og_data["tdate"][-1:].values
            if last_date:
                data = data[data["tdate"] > last_date[0]]
                data = pd.concat([og_data, data])
        data.to_csv(path, index=0)

    def loadKline(self, code):
        path = self.__getPath(code)
        data = pd.read_csv(path, dtype={'code':object})
        return data

    def updateDayKlines(self, codes, start_date):
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
        print("{} update {} from {} to {}".format(self.file_name, code_str,start_date,end_date))

        url = "{}?code={}&ktype={}&fq=1&startDate={}&endDate={}&export=5&token={}&fields=all".format(self.url_head, code_str, self.ktype, start_date, end_date, self.token)
        response = requests.get(url).json()
        try:
            datas = pd.DataFrame(data=response['data'], columns=response['en'])
        except KeyError as e:
            print(e)
            print(response)
            raise e

        lower_codes = datas["code"].str.lower()
        datas["code"] = lower_codes
        
        for code in codes:
            lower_code = code.lower()
            data = datas[datas["code"] == lower_code]
            self.__saveKline(data, code)
        return datas

    def __getLastUpdateDate(self, code, init_date):
        last_date = init_date
        path = self.__getPath(code)
        if os.path.exists(path):
            data = data = pd.read_csv(path, dtype={'code':object})
            date = data["tdate"][-1:].values
            if date:
                last_date = date[0]
        return last_date

    def update(self, codes, end_date):
        '''
        codes = [{code,start_date}]
        '''
        update_cands = []
        for i in range(len(codes)):
            last_update_date = self.__getLastUpdateDate(code=codes[i]["code"], init_date=codes[i]["start_date"])
            codes[i]["start_date"] = last_update_date
            date_dist = RoughTimeDist(codes[i]["start_date"], end_date)
            codes[i]["date_dist"] = date_dist
        codes = sorted(codes, key=lambda item: item["date_dist"])

        # 分组下载更新
        groups = []
        latest_group = []
        for i in range(len(codes)-1, 0, -1):
            if codes[i]["date_dist"] <= 0:
                continue
            max_items = 0
            if latest_group:
                max_items = max(latest_group, key=lambda item: item["date_dist"])["date_dist"]
            if len(latest_group) >= 50 or max_items * (len(latest_group) + 1) >= self.items_th:
                groups.append(latest_group)
                latest_group = []
            latest_group.append(codes[i])
        if latest_group:
            groups.append(latest_group)
        
        for group in groups:
            codes = []
            for item in group:
                codes.append(item["code"])
            self.updateDayKlines(codes=codes, start_date=group[0]["start_date"])
        return groups


class HourKlineDownloader:
    '''
    从 http://www.waizaowang.com/ 获取沪深京A股时线数据(5分钟、15分钟、30分钟、60分钟数据)
    与 DayKlineDownloader 相比,所有code每次更新时间范围一致
    '''
    def __init__(self, token, dic, url_suffix, file_name, ktype, days_th) -> None:
        '''
        token: api凭证
        days_th: 每次请求 时间范围(天)
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc/{}".format(url_suffix)
        self.dic = dic
        self.file_name = file_name
        self.ktype = ktype
        self.days_th = days_th

    def __getPath(self, code):
        path = "{}/{}/{}".format(self.dic, code, self.file_name)
        return path

    def loadKline(self, code):
        path = self.__getPath(code)
        data = pd.read_csv(path, dtype={'code':object})
        return data

    def __saveKline(self, data, code):
        path = self.__getPath(code)
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

    def __lastUpdateDate(self, code):
        path = self.__getPath(code)
        if os.path.exists(path):
            data = pd.read_csv(path, dtype={'code':object})
            last_date = data["tdate"][-1:].values
            if last_date:
                return last_date[0]
        return "1990-01-01"

    def updateHourKline(self, codes, start_date, end_date):
        '''
        ktype : 5 5min, 15 15min, 30 30min, 60 60min
        更新K线信息
        不复权
        股票：
        [   'code' : '股票代码'
            'tdate': '分时时间'
            'open' : '开盘价'
            'close' : '收盘价'
            'high' : '最高价'
            'low' : '最低价'
            'cjl' : '成交量（手）'
            'cje' : '成交额（元）'
            'cjjj': '成交均价']
        指数：
        [   'code' : '股票代码'
            'name' : '股票名称'
            'ktype': 'K线类别'(5|5分钟 15|15分钟 30|30分钟 60|60分钟)
            'tdate': '分时时间'
            'open' : '开盘价'
            'close' : '收盘价'
            'high' : '最高价'
            'low' : '最低价'
            'cjl' : '成交量（手）'
            'cje' : '成交额（元）'
            'hsl': '换手率']
        '''
        code_str = codes[0]
        for i in range(1, len(codes)):
            code_str += ","
            code_str += codes[i]

        print("{} update {} from {} to {}".format(self.file_name, code_str,start_date,end_date))

        url = "{}?code={}&ktype={}&startDate={}&endDate={}&export=5&token={}&fields=all".format(self.url_head, code_str, self.ktype, start_date, end_date, self.token)
        response = requests.get(url).json()

        # 处理错误
        if response.get("code") == -1:
            print("WARNNING : {}".format(response.get("message")))
            code_num = len(codes)
            if code_num > 1:
                codes_a = [codes[i] for i in range(0, code_num//2)]
                codes_b = [codes[i] for i in range(code_num//2, code_num)]
                self.updateHourKline(codes_a, start_date, end_date)
                self.updateHourKline(codes_b, start_date, end_date)
                return

        datas = pd.DataFrame(data=response['data'], columns=response['en'])

        lower_codes = datas["code"].str.lower()
        datas["code"] = lower_codes
        
        for code in codes:
            lower_code = code.lower()
            data = datas[datas["code"] == lower_code]

            app = []
            tdate = data["tdate"]
            for line in tdate:
                date,time = line.split("T")
                time = time.split(".")
                app.append([line, date, time[0]])
            app = pd.DataFrame(app, columns = ['tdate', 'date','time'])
            data = pd.merge(data, app, on='tdate')
            data = data.rename(columns={'tdate' : 'og_date', 'date' : 'tdate'})

            self.__saveKline(data, code)
        return datas

    def __filterCodes(self, codes, end_date):
        filtered_code =[]
        for code in codes:
            last_update_date = self.__lastUpdateDate(code)
            if end_date > last_update_date:
                filtered_code.append(code)
        print("file_name : before filtered code {}, after filtered code {}".format(len(codes), len(filtered_code)))
        return filtered_code

    def __filterDates(self, codes, dates):
        # 找到最早日期作为group更新的最早日期
        start_dates = []
        for code in codes:
            last_update_date = self.__lastUpdateDate(code)
            start_dates.append(last_update_date)
        start_date = start_dates[0]
        for date in start_dates:
            if date < start_date:
                start_date = date

        dates_cand = []
        for date in dates:
            if date > start_date:
                dates_cand.append(date)
        return dates_cand

    def __updateGroup(self, codes, dates):
        if len(codes)==0 or len(dates) < 2:
            return
        
        dates = self.__filterDates(codes, dates)
        dates = sorted(dates)
        # 将日期分为多段，分段更新
        data_gap = []
        for i in range(len(dates)):
            if i % self.days_th == 0:
                data_gap.append(dates[i])
        if (len(dates) - 1) % self.days_th != 0:
            data_gap.append(dates[-1])
        
        for i in range(len(data_gap) - 1):
            self.updateHourKline(codes=codes, start_date=data_gap[i], end_date=data_gap[i+1])

    def update(self, codes, dates):
        '''
        如果 len(dates) > days_th , 分几次更新
        每轮请求都是50个codes,通过 days_th 限制每批下载次数
        '''
        if len(codes)==0 or len(dates) < 2:
            return

        codes = self.__filterCodes(codes=codes, end_date=dates[-2])
        groups = []
        latest_group = []
        for code in codes:
            latest_group.append(code)
            if len(latest_group) >= 50:
                groups.append(latest_group)
                latest_group = []
        if latest_group:
            groups.append(latest_group)
        for group in groups:
            self.__updateGroup(codes=group, dates=dates)


class TradeCalender:
    '''
    交易日历
    '''
    def __init__(self, token, dic) -> None:
        self.day_loader = DayKlineDownloader(token=token, dic=dic, url_suffix="getStockHSADayKLine",
                                                file_name="day_line.csv", ktype="101")
        self.day_loader.updateDayKlines(codes=["000001"], start_date="1990-01-01")

    def getTradeDates(self):
        data = self.day_loader.loadKline("000001")
        all_dates = []
        for date in data["tdate"]:
            all_dates.append(date)
        dates = []
        for i in range(len(all_dates)):
            dates.append(all_dates[i])
        y,m,d = dates[-1].split("-")
        dates.append("{}-01-01".format(str(int(y)+1)))                                          
        return dates
        

class StockHSADownloader:
    '''
    从 http://www.waizaowang.com/ 获取沪深京A股数据
    '''
    def __init__(self, dic, token="") -> None:
        '''
        token: api凭证
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc"
        self.dic = "{}/stock_hsa".format(dic)

        self.day_loader = DayKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSADayKLine",
                                                file_name="day_line.csv", ktype="101")
        self.week_loader = DayKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSADayKLine",
                                                file_name="week_line.csv", ktype="102")
        self.month_loader = DayKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSADayKLine",
                                                file_name="month_line.csv", ktype="103")

        self.min5_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSAHourKLine",
                                                file_name="min5_line.csv", ktype="5", days_th=2)
        self.min15_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSAHourKLine",
                                                file_name="min15_line.csv", ktype="15", days_th=5)
        self.min30_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSAHourKLine",
                                                file_name="min30_line.csv", ktype="30", days_th=20)
        self.min60_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getStockHSAHourKLine",
                                                file_name="min60_line.csv", ktype="60", days_th=30)
        self.trade_calender = TradeCalender(token=self.token, dic="{}/stock_hsa".format(dic))

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
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        data.to_csv(path, index=0)
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

    def __updateDayKlines(self):
        info = self.loadBaseInfo()
        codes = []
        for code, row in info.iterrows():
            codes.append({"code" : code, "start_date" : row["ssdate"]})
        end_date = self.trade_calender.getTradeDates()[-2]
        self.day_loader.update(codes, end_date)
        self.week_loader.update(codes, end_date)
        self.month_loader.update(codes, end_date)

    def __updateHourLines(self):
        codes = self.__getAllCodes()
        trade_dates = self.trade_calender.getTradeDates()
        trade_dates = trade_dates[-50:]

        self.min5_loader.update(codes=codes, dates=trade_dates)
        self.min15_loader.update(codes=codes, dates=trade_dates)
        self.min30_loader.update(codes=codes, dates=trade_dates)
        self.min60_loader.update(codes=codes, dates=trade_dates)

    def updateKlineDataset(self):
        self.__updateDayKlines()
        self.__updateHourLines()
        print("update finish ! ^-^")

    def loadKline(self, code):
        day_kline = self.day_loader.loadKline(code)
        week_kline = self.week_loader.loadKline(code)
        month_kline = self.month_loader.loadKline(code)
        min5_kline = self.min5_loader.loadKline(code)
        min15_kline = self.min15_loader.loadKline(code)
        min30_kline = self.min30_loader.loadKline(code)
        min60_kline = self.min60_loader.loadKline(code)
        return {"day":day_kline, "week": week_kline, "month": month_kline,
                "min5":min5_kline, "min15":min15_kline, "min30":min30_kline, "min60":min60_kline}


def index_table():
    index_table = { "000001" : "上证指数", 
                    "000132": "上证100",
                    "000133": "上证150",
                    "000300": "沪深300",
                    "000688": "科创50",
                    "000002": "Ａ股指数",
                    "000003": "Ｂ股指数",
                    "000903": "中证100",
                    "000904": "中证200",
                    "000905": "中证500",
                    "000906": "中证800",
                    "000907": "中证700",
                    "HSI": "恒生指数",
                    "AEX": "荷兰AEX",
                    "AORD": "澳大利亚普通股",
                    "AS51": "澳大利亚标普200",
                    "ASE": "希腊雅典ASE",
                    "ATX": "奥地利ATX",
                    "AXX": "富时AIM全股",
                    "BDI": "波罗的海BDI指数",
                    "BFX": "比利时BFX",
                    "BVSP": "巴西BOVESPA",
                    "CRB": "路透CRB商品指数",
                    "CSEALL": "斯里兰卡科伦坡",
                    "DJIA": "道琼斯",
                    "FCHI": "法国CAC40",
                    "FTSE": "英国富时100",
                    "GDAXI": "德国DAX30",
                    "HEX": "芬兰赫尔辛基",
                    "IBEX": "西班牙IBEX35",
                    "ICEXI": "冰岛ICEX",
                    "ISEQ": "爱尔兰综合",
                    "JKSE": "印尼雅加达综合",
                    "KLSE": "富时马来西亚KLCI",
                    "KOSPI200": "韩国KOSPI200",
                    "KS11": "韩国KOSPI",
                    "KSE100": "巴基斯坦卡拉奇",
                    "MCX": "英国富时250",
                    "MIB": "富时意大利MIB",
                    "MXX": "墨西哥BOLSA",
                    "N225": "日经225",
                    "NDX": "纳斯达克",
                    "NZ50": "新西兰50",
                    "OMXC20": "OMX哥本哈根20",
                    "OMXSPI": "瑞典OMXSPI",
                    "OSEBX": "挪威OSEBX",
                    "PSI": "菲律宾马尼拉",
                    "PSI20": "葡萄牙PSI20",
                    "PX": "布拉格指数",
                    "RTS": "俄罗斯RTS",
                    "SENSEX": "印度孟买SENSEX",
                    "SET": "泰国SET",
                    "SPX": "标普500",
                    "SSMI": "瑞士SMI",
                    "STI": "富时新加坡海峡时报",
                    "SX5E": "欧洲斯托克50",
                    "TSX": "加拿大S&P/TSX",
                    "TWII": "台湾加权",
                    "UDI": "美元指数",
                    "VNINDEX": "越南胡志明",
                    "WIG": "波兰WIG",
    }
    return index_table


class GloabalIndexDownloader:
    '''
    从 http://www.waizaowang.com/ 获取指数数据
    '''
    def __init__(self,  dic, token) -> None:
        '''
        token: api凭证
        '''
        self.token = token
        self.url_head = "http://api.waizaowang.com/doc"
        self.dic = "{}/index_global".format(dic)

        self.day_loader = DayKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexDayKLine",
                                                file_name="day_line.csv", ktype="101")
        self.week_loader = DayKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexDayKLine",
                                                file_name="week_line.csv", ktype="102")
        self.month_loader = DayKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexDayKLine",
                                                file_name="month_line.csv", ktype="103")

        self.min5_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexHourKLine",
                                                file_name="min5_line.csv", ktype="5", days_th=2)
        self.min15_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexHourKLine",
                                                file_name="min15_line.csv", ktype="15", days_th=5)
        self.min30_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexHourKLine",
                                                file_name="min30_line.csv", ktype="30", days_th=20)
        self.min60_loader = HourKlineDownloader(token=self.token, dic=self.dic, url_suffix="getIndexHourKLine",
                                                file_name="min60_line.csv", ktype="60", days_th=30)
        self.trade_calender = TradeCalender(token=self.token, dic="{}/stock_hsa".format(dic))
        self.code_table = index_table()

    def updateIndexInfo(self, file_name="/base/info.csv"):
        '''
        更新全球指数基础信息[code,name]
        '''
        index_datas = []

        # 沪深指数列表
        hs_index_url = "{}/getIndexHSBaseInfo?code=all&export=5&token={}&fields=all".format(self.url_head, self.token)
        response = requests.get(hs_index_url).json()
        data = pd.DataFrame(data=response['data'], columns=response['en'])
        index_datas = data[["code", "name"]]

        # 香港指数列表
        hk_index_url = "{}/getIndexHKBaseInfo?code=all&export=5&token={}&fields=all".format(self.url_head, self.token)
        response = requests.get(hk_index_url).json()
        data = pd.DataFrame(data=response['data'], columns=response['en'])
        index_datas = pd.concat([index_datas, data[["code", "name"]]], ignore_index=True)

        # 全球指数列表
        global_index_url = "{}/getIndexQQBaseInfo?code=all&export=5&token={}&fields=all".format(self.url_head, self.token)
        response = requests.get(global_index_url).json()
        data = pd.DataFrame(data=response['data'], columns=response['en'])
        index_datas = pd.concat([index_datas, data[["code", "name"]]], ignore_index=True)

        path = self.dic + file_name
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        index_datas.to_csv(path, index=0)
        return index_datas

    def loadIndexInfo(self, file_name="/base/info.csv"):
        path = self.dic + file_name
        data = pd.read_csv(path, dtype={'code':object})
        return data

    def getIndexName(self, code):
        data = self.loadIndexInfo()
        return data[data["code"]==code]["name"].values[0]

    def getIndexCode(self, name):
        data = self.loadIndexInfo()
        return data[data["name"]==name]["code"].values[0]

    def __updateDayKlines(self):
        codes = []
        for code in self.code_table:
            codes.append({"code" : code, "start_date" : "1990-01-01"})
        end_date = self.trade_calender.getTradeDates()[-2]
        self.day_loader.update(codes, end_date)
        self.week_loader.update(codes, end_date)
        self.month_loader.update(codes, end_date)

    def __updateHourLines(self):
        codes = []
        for code in self.code_table:
            codes.append(code)
        trade_dates = self.trade_calender.getTradeDates()

        self.min5_loader.update(codes=codes, dates=trade_dates[-30:])
        self.min15_loader.update(codes=codes, dates=trade_dates[-30:])
        self.min30_loader.update(codes=codes, dates=trade_dates[-30:])
        self.min60_loader.update(codes=codes, dates=trade_dates[-2000:])

    def updateKlineDataset(self):
        self.__updateDayKlines()
        self.__updateHourLines()
        print("update finish ! ^-^")

    def loadKline(self, code):
        day_kline = self.day_loader.loadKline(code)
        week_kline = self.week_loader.loadKline(code)
        month_kline = self.month_loader.loadKline(code)
        min5_kline = self.min5_loader.loadKline(code)
        min15_kline = self.min15_loader.loadKline(code)
        min30_kline = self.min30_loader.loadKline(code)
        min60_kline = self.min60_loader.loadKline(code)
        return {"day":day_kline, "week": week_kline, "month": month_kline,
                "min5":min5_kline, "min15":min15_kline, "min30":min30_kline, "min60":min60_kline}


class WaiZaoStock(Stock):
    '''
    '''
    def __init__(self, klines) -> None:
        """
        klines = {"day":day_kline, "week": week_kline, "month": month_kline,
                "min5":min5_kline, "min15":min15_kline, "min30":min30_kline, "min60":min60_kline}
        """
        self.klines = klines

    def day(self):
        """
        """
        day_line = self.klines["day"]
        times = [item for item in day_line["tdate"]]
        candles = [line for line in zip(day_line["open"], day_line["close"], day_line["low"], day_line["high"])]
        # 换手率
        turnover_rate = [item for item in day_line["hsl"]]
        # 成交量
        turnover_count = [item for item in day_line["cjl"]]

        data = {"times": times, "candles": candles, "turnover_rate": turnover_rate, "turnover_count": turnover_count}
        return data

    def week(self):
        pass

    def month(self):
        pass

    def min5(self):
        pass

    def min15(self):
        pass

    def min30(self):
        pass

    def min60(self):
        pass


def fill_stock(kline):
    times = [item for item in kline["tdate"]]
    opens = [item for item in kline["open"]]
    closes = [item for item in kline["close"]]
    lows = [item for item in kline["low"]]
    highs = [item for item in kline["high"]]
    # 换手率
    turnover_rate = [item for item in kline["hsl"]]
    # 成交量
    turnover_count = [item for item in kline["cjl"]]
    data = {"times": times, "opens": opens, "closes": closes, "lows": lows, "highs": highs, 
            "turnover_rate": turnover_rate, "turnover_count": turnover_count}
    stock = Stock(data)
    return stock


class KlineDataset:
    '''
    加载沪深京A股数据
    '''
    def __init__(self, dic) -> None:
        self.stock_dic = "{}/stock_hsa".format(dic)
        self.index_dic = "{}/index_global".format(dic)

    def __loadKline(self, path):
        data = pd.read_csv(path, dtype={'code':object})
        return data

    def __loadKlines(self, code, dic):
        day_kline = self.__loadKline("{}/{}/{}".format(dic, code, "day_line.csv"))
        week_kline = self.__loadKline("{}/{}/{}".format(dic, code, "week_line.csv"))
        month_kline = self.__loadKline("{}/{}/{}".format(dic, code, "month_line.csv"))
        min5_kline = self.__loadKline("{}/{}/{}".format(dic, code, "min5_line.csv"))
        min15_kline = self.__loadKline("{}/{}/{}".format(dic, code, "min15_line.csv"))
        min30_kline = self.__loadKline("{}/{}/{}".format(dic, code, "min30_line.csv"))
        min60_kline = self.__loadKline("{}/{}/{}".format(dic, code, "min60_line.csv"))
        return {"day":day_kline, "week": week_kline, "month": month_kline,
                "min5":min5_kline, "min15":min15_kline, "min30":min30_kline, "min60":min60_kline}

    def loadStockHSAKline(self, code):
        return self.__loadKlines(code=code, dic=self.stock_dic)

    def loadGloabalIndexKline(self, code):
        return self.__loadKlines(code=code, dic=self.index_dic)

    def Stock(self, code):
        stock_klines = self.loadStockHSAKline(code)
        stocks = {}
        for key in stock_klines:
            stocks[key] = fill_stock(stock_klines[key])
        return stocks

    def Index(self, code):
        stock_klines = self.loadGloabalIndexKline(code)
        stocks = {}
        for key in stock_klines:
            stocks[key] = fill_stock(stock_klines[key])
        return stocks
    
    def IndexTables(self):
        return index_table()

    def StockTables(self):
        path = self.stock_dic + "/base/info.csv"
        info = pd.read_csv(path, dtype={'code':object}, index_col=['code'])
        stock_table = {}
        for code, row in info.iterrows():
            stock_table[code] = row["name"]
        return stock_table