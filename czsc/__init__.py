# coding: utf-8

from .analyze import KlineAnalyze
from .utils import *

__version__ = "v20201119.1"
__author__ = "kaybinwong(@126.com)"
print('czsc by {}, current version is {}'.format(__author__, __version__))


def create_ka(symbol, freq, bi_mode="old", max_xd_len=20, zs_mode='xd', ma_params=(5, 20, 60), verbose=False):
    """
    构建分析器
    """
    return KlineAnalyze(symbol, freq, bi_mode=bi_mode, max_xd_len=max_xd_len, zs_mode=zs_mode, ma_params=ma_params, verbose=verbose)
