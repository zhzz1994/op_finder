import os
import pandas as pd
import datetime
import ipywidgets as widgets


class IndexSelecter:
    def __init__(self, dataset):
        self.index_table = dataset.IndexTables()

    def draw(self):
        index_list = []
        for key in self.index_table:
            index_list.append(self.index_table[key])
        self.index_selecter = widgets.Dropdown(
            options=index_list,
            description='Index:',
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
    def __init__(self, dataset, cache_path = "cache/stock_code_cache.csv"):
        self.stock_table = dataset.StockTables()
        self.cache_path = cache_path

    def draw(self):
        stock_list = []
        if os.path.exists(self.cache_path):
            data = pd.read_csv(self.cache_path, dtype={'code':object})
            for code, row in data.iterrows():
                stock_list.append(row["name"])
        self.cache_selecter = widgets.Dropdown(
            options=stock_list,
            description='Stock Cache:',
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
            description='Stock:',
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
            data = pd.DataFrame(data=data_line, columns=["code", "name"])
        data.to_csv(self.cache_path, index = 0)
    

class DateSelecter:
    def draw(self, year=2020, month=1, day=1):
        self.date_picker = widgets.DatePicker(
            description='Start Date',
            disabled=False,
        )
        self.date_picker.value = datetime.date(year, month, day)
        display(self.date_picker)

    def choosen_date(self):
        return str(self.date_picker.value)
