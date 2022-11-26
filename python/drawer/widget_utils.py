import os
import pandas as pd
import datetime
import ipywidgets as widgets


class IndexSelecter:
    def __init__(self, dataset, name="Index"):
        self.index_table = dataset.IndexTables()
        self.name = name

    def draw(self):
        index_list = []
        for key in self.index_table:
            index_list.append(self.index_table[key])
        self.index_selecter = widgets.Dropdown(
            options=index_list,
            description=self.name,
            disabled=False,
        )
        display(self.index_selecter)

    def choosen_name(self):
        return self.index_selecter.value

    def choosen_code(self):
        choosen_name = self.choosen_name()
        for key in self.index_table:
            if choosen_name == self.index_table[key]:
                return key


class StockSelecter:
    def __init__(self, dataset, name="Stock", cache_path = "cache/stock_code_cache.csv"):
        self.stock_table = dataset.StockTables()
        self.cache_path = cache_path
        self.name = name

    def draw(self):
        stock_list = []
        if os.path.exists(self.cache_path):
            data = pd.read_csv(self.cache_path, dtype={'code':object})
            for code, row in data.iterrows():
                stock_list.append(row["name"])
        self.cache_selecter = widgets.Dropdown(
            options=stock_list,
            description=self.name + ' Cache:',
            disabled=False,
        )
        display(self.cache_selecter)

    def choosen_name(self):
        return self.cache_selecter.value

    def choosen_code(self):
        choosen_name = self.choosen_name()
        for key in self.stock_table:
            if choosen_name == self.stock_table[key]:
                return key

    def draw_all(self):
        stock_list = []
        for key in self.stock_table:
            stock_list.append(self.stock_table[key])
        self.stock_all_selecter = widgets.Dropdown(
            options=stock_list,
            description=self.name,
            disabled=False,
        )
        display(self.stock_all_selecter)

    def cache_selected(self):
        name = self.stock_all_selecter.value
        code = ""
        for key in self.stock_table:
            if self.stock_table[key] == name:
                code = key
        self.add_cache(code)

    def add_cache(self, code):
        data_line = pd.DataFrame(data=[[code, self.stock_table[code]]], columns=["code", "name"])
        if os.path.exists(self.cache_path):
            data = pd.read_csv(self.cache_path, dtype={'code':object})
            if code not in data["code"].values:
                data = pd.concat([data_line, data])
        else:
            os.makedirs(os.path.dirname(self.cache_path))
            data = pd.DataFrame(data=data_line, columns=["code", "name"])
        data.to_csv(self.cache_path, index = 0)
    

class DateSelecter:
    def __init__(self, name="Date"):
        self.name = name

    def draw(self, year=2020, month=1, day=1):
        self.date_picker = widgets.DatePicker(
            description=self.name,
            disabled=False,
        )
        self.date_picker.value = datetime.date(year, month, day)
        display(self.date_picker)

    def choosen_date(self):
        return str(self.date_picker.value)


class ChartTypeSelecter:
    def draw(self):
        draw_type_list = ["log", "value"]
        self.draw_type_selecter = widgets.Dropdown(
            options=draw_type_list,
            description='Draw Type:',
            disabled=False,
        )
        display(self.draw_type_selecter)
        chart_type_list = ["day", "week", "month", "min5", "min15", "min30", "min60"]
        self.chart_type_selecter = widgets.Dropdown(
            options=chart_type_list,
            description='Chart Type:',
            disabled=False,
        )
        display(self.chart_type_selecter)

    def draw_type(self):
        return self.draw_type_selecter.value

    def chart_type(self):
        return self.chart_type_selecter.value