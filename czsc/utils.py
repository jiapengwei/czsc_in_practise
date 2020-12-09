# coding: utf-8
"""
工具类，比如线数据归一化处理等
"""

import pandas as pd

######################## compare method ###############################

def float_less(a, b):
    return a < b and not np.isclose(a, b)

def float_more(a, b):
    return a > b and not np.isclose(a, b)

def float_less_equal(a, b):
    return a < b or np.isclose(a, b)

def float_more_equal(a, b):
    return a > b or np.isclose(a, b)

def is_in_range(a, b, n):
    """判断数字n是否在区间[a, b]内"""
    assert float_less(a, b)
    return a < n < b3

def is_overlap(a, b):
    """
    判断2区间是否重叠
    参数
    :param a 数字数组,比如[1, 1.8]
    :param b 数字数组,比如[0.5, 1.8]
    返回
    True 重叠
    False 不重叠
    """
    return max(a[0], b[0]) <= min(a[1], b[1])

def __symbol_2_jq(symbol):
    """
    将标的代码格式化成聚宽代码格式，目前只支持A股
    参数
    :param symbol 标的代码，比如SH000001
    返回
    格式化后的代码，比如000001.XSHG
    """
    assert symbol is not None
    code = re.sub(r'\D', "", symbol)
    if code.startswith('6'):
        return '{}.XSHG'.format(code)
    return '{}.XSHE'.format(code)

def __symbol_2_ts(symbol):
    """
    将标的代码格式化成Tushare代码格式，目前只支持A股
    参数
    :param symbol 标的代码，比如SH000001
    返回
    格式化后的代码，比如000001.SH
    """
    assert symbol is not None
    code = re.sub(r'\D', "", symbol)
    if code.startswith('6'):
        return '{}.SH'.format(code)
    return '{}.SZ'.format(code)

def __bars_from_jq(symbol, df_klines):
    """
    将聚宽的get_bars数据归一化成本程序标准
    参数
    :param symbol 标的代码，比如SH000001
    :param df_klines 标的代码，从聚宽get_bars函数返回的数据（sdk或者网站环境）
    返回
    归一化后的k线数据，包含列 'symbol', 'dt', 'open', 'close', 'high', 'low', 'vol'
    """
    df_klines['symbol'] = symbol
    df_klines.rename({ 'date': 'dt', 'volume': 'vol'}, axis=1, inplace=True)
    df_klines.reset_index(drop=True, inplace=True)
    df_klines = df_klines[['symbol', 'dt', 'open', 'close', 'high', 'low', 'vol']]
    for col in ['open', 'close', 'high', 'low', 'vol']:
        df_klines.loc[:, col] = df_klines[col].apply(lambda x: round(float(x), 2))
    df_klines.loc[:, "dt"] = pd.to_datetime(df_klines['dt'])
    return df_klines

def __bars_from_ts(self, symbol, df_klines):
    """
    将tushare的pro_bar数据归一化成本程序标准
    参数
    :param symbol 标的代码，比如SH000001
    :param df_klines 标的代码，从tushare的pro_bar函数返回的数据
    返回
    归一化后的k线数据，包含列 'symbol', 'dt', 'open', 'close', 'high', 'low', 'vol'
    """
    df_klines['symbol'] = symbol
    df_klines.rename({'date': 'dt', 'volume': 'vol'}, axis=1, inplace=True)
    df_klines = df_klines[['symbol', 'dt', 'open', 'close', 'high', 'low', 'vol']]
    for col in ['open', 'close', 'high', 'low', 'vol']:
        df_klines.loc[:, col] = df_klines[col].apply(lambda x: round(float(x), 2))
    df_klines.loc[:, "dt"] = pd.to_datetime(df_klines['dt'])
    return df_klines

def normalize_symbol(symbol, to_):
    """
    标的代码转换
    参数
    :param symbol 标的代码，比如SH000001
    :param to_ 目标站点，目前支持聚宽(jq)/Tushare(ts)
    返回
    转换后的代码
    """
    if to_ == 'jq':
        return __symbol_2_jq(symbol)
    elif to_ == 'ts':
        return __symbol_2_ts(symbol)
    else:
        raise ValueError

def normalize_kbars(symbol, kbars, data_from):
    """
    K线数据归一化成本程序标准
    参数
    :param symbol 标的代码，比如SH000001
    :param to_ 目标站点，目前支持聚宽(jq)/Tushare(ts)
    返回
    归一化后的K线数据，包含列 'symbol', 'dt', 'open', 'close', 'high', 'low', 'vol'
    """
    if data_from == 'jq':
        return __bars_from_jq(symbol, kbars)
    elif data_from == 'ts':
        return __bars_from_ts(symbol, kbars)
    else:
        raise ValueError

def get_kbars(kline_raw, cur_freq, nxt_freq):
    """
    https://www.joinquant.com/view/community/detail/f05b9cbce3612bb2fad36740551d28be?type=1
    计算出要取的分钟bar个数，然后按照每unit个分钟bar合并。include_now = True时，最后一个合并的bar包含的分钟bar个数可能不是unit个。
    股票/基金/指数 一天有240个bar，能被5/15/30/60/120 整除，所以只有最后一个合并的bar有可能不是由unit个分钟bar合并的。
    注意：这里这是大概实现，若是按照整点取数算出来的数据理论上跟再次调用使一致的，但是当特殊取数时会导致数据不准确，比如当前是3m分时数据，聚合5m就会有问题
    参数
    :param kline_raw 归一后的K线
    :param cur_freq 当前级别，只支持xm，1d可以折换成240m，再大级别的没意义，时间不够
    :param nxt_freq 需要聚合的级别
    """
    cur_freq_unit = cur_freq[-1]
    nxt_freq_unit = nxt_freq[-1]
    if cur_freq_unit != 'm' or nxt_freq_unit != 'm':
        print('目前只支持分钟级别聚合，1d行情请用240m')
        raise ValueError
    
    cur_freq_val = int(cur_freq[0:-1])
    nxt_freq_val = int(nxt_freq[0:-1])
    if cur_freq_val >= nxt_freq_val or nxt_freq_val % cur_freq_val != 0:
        print('同级别分时只能聚合成整数倍分时数据，比如xm只能聚合n*xm的数据。{}，{}'.format(cur_freq_val, nxt_freq_val))
        raise ValueError
    interval = (int)(nxt_freq_val / cur_freq_val)

    kbars_new = []
    start_index=0
    for index in range(interval, len(kline_raw), interval):
        cur_index = index - 1
        kline = kline_raw[cur_index]
        kline['high'] = max([x['high'] for x in kline_raw[start_index:cur_index]])
        kline['low'] = min([x['low'] for x in kline_raw[start_index:cur_index]])
        kline['vol'] = sum([x['vol'] for x in kline_raw[start_index:cur_index]])
        kbars_new.append(kline)
        start_index=index
    
    if start_index < len(kline_raw):
        kline = kline_raw[-1]
        kline['high'] = max([x['high'] for x in kline_raw[start_index:len(kline_raw)]])
        kline['low'] = min([x['low'] for x in kline_raw[start_index:len(kline_raw)]])
        kline['vol'] = sum([x['vol'] for x in kline_raw[start_index:len(kline_raw)]])
        kbars_new.append(kline)
    # print('kbars new：{}'.format(kbars_new))
    return kbars_new
