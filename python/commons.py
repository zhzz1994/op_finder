from typing import List, Sequence, Union



def calculate_ma(data, day_count):
    result = []
    sum_total = 0.0
    for i in range(len(data)):
        sum_total += data[i]
        if i < day_count - 1 :
            result.append("-")
        else:
            result.append(float("%.2f" % (sum_total / day_count)))
            sum_total -= data[i - day_count]
    return result