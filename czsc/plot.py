# coding: utf-8
"""
使用 pyecharts 定制绘图模块
"""

from typing import List

from pyecharts import options as opts
from pyecharts.charts import Bar, EffectScatter, Grid, HeatMap, Kline, Line
from pyecharts.commons.utils import JsCode


def to_grid(ka,
              kline_mode: str = "new",
              with_bi: bool = False,
              with_xd: bool = False,
              with_zs: bool = False,
              with_bs: bool = False,
              with_ma: bool = False,
              with_vol: bool = False,
              with_macd: bool = False,
              title: str = "ChanLun In Practise",
              width: str = "1440px",
              height: str = '900px') -> Grid:
    """绘制缠中说禅K线分析结果
    :param kline: K线 new / raw，new标识标准化后的k线，raw标识原始k线
    :param with_bi: 是否显示笔识别结果，默认True，不输出False
    :param with_xd: 是否显示线段识别结果
    :param with_zs: 是否显示中枢识别结果
    :param with_bs: 是否显示买卖点
    :param with_ma: 是否显示均线，默认True，不输出False
    :param with_macd: 是否显示macd，默认True，不输出False
    :param with_vol: 是否显示成交量，默认True，不输出False
    :param title: 图表标题
    :param width: 图表宽度
    :param height: 图表高度
    :return: 用Grid组合好的图表
    """
    
    # 配置项设置
    # ------------------------------------------------------------------------------------------------------------------
    bg_color = "#1f212d"    # 背景
    up_color = "#F9293E"
    down_color = "#00aa3b"

    init_opts = opts.InitOpts(bg_color=bg_color, width='1400px', height='800px')
    title_opts = opts.TitleOpts(title=title, pos_top="1%",
                                title_textstyle_opts=opts.TextStyleOpts(color=up_color, font_size=20),
                                subtitle_textstyle_opts=opts.TextStyleOpts(color=down_color, font_size=12))

    label_not_show_opts = opts.LabelOpts(is_show=False)
    legend_not_show_opts = opts.LegendOpts(is_show=False)
    red_item_style = opts.ItemStyleOpts(color=up_color)
    green_item_style = opts.ItemStyleOpts(color=down_color)
    k_style_opts = opts.ItemStyleOpts(color=up_color, color0=down_color, border_color=up_color,
                                      border_color0=down_color, opacity=0.8)

    legend_opts = opts.LegendOpts(is_show=True, pos_top="1%", pos_left="30%", item_width=14, item_height=8,
                                  textstyle_opts=opts.TextStyleOpts(font_size=12, color="#0e99e2"))
    brush_opts = opts.BrushOpts(tool_box=["rect", "polygon", "keep", "clear"],
                                x_axis_index="all", brush_link="all",
                                out_of_brush={"colorAlpha": 0.1}, brush_type="lineX")

    axis_pointer_opts = opts.AxisPointerOpts(is_show=True, link=[{"xAxisIndex": "all"}])

    dz_inside = opts.DataZoomOpts(False, "inside", xaxis_index=[0, 1, 2])
    dz_slider = opts.DataZoomOpts(True, "slider", xaxis_index=[0, 1, 2], pos_top="96%", pos_bottom="0%")

    yaxis_opts = opts.AxisOpts(is_scale=True, axislabel_opts=opts.LabelOpts(color="#c7c7c7", font_size=8, position="inside"))

    grid0_xaxis_opts = opts.AxisOpts(type_="category", grid_index=0, axislabel_opts=label_not_show_opts,
                                     split_number=20, min_="dataMin", max_="dataMax",
                                     is_scale=True, boundary_gap=False, axisline_opts=opts.AxisLineOpts(is_on_zero=False))

    tool_tip_opts = opts.TooltipOpts(
        trigger="axis",
        axis_pointer_type="cross",
        background_color="rgba(245, 245, 245, 0.8)",
        border_width=1,
        border_color="#ccc",
        textstyle_opts=opts.TextStyleOpts(color="#000"),
    )


    # 数据预处理
    # ------------------------------------------------------------------------------------------------------------------
    kline = ka.kline_new if kline_mode == 'new' else ka.kline_raw
    dts = [x['dt'] for x in kline]
    k_data = [[x['open'], x['close'], x['low'], x['high']] for x in kline]

    # seriesname
    aggregation = len(ka.ka_list)>0
    # {'freq': {'kline', 'ma', 'vol', 'macd'}}
    agg_dict = {}    
    agg_dict[ka.freq] = {
        "kline": k_data,
        "ma": ka.ma,
        "vol": kline,
        "macd": ka.macd
    }
    if aggregation:
        for high_ka in ka.ka_list:
            agg_dict[high_ka.freq] = {}
            _high_k_data = high_ka.kline_new if kline_mode == 'new' else high_ka.kline_raw
            high_k_data = []
            high_ma_data = []
            high_vol_data = []
            high_macd_data = []
            for i in range(len(dts)):
                high_k_data.append([])
                high_ma_data.append({})
                high_vol_data.append(None)
                high_macd_data.append(None)
            for ki in range(len(kline)):
                k = kline[ki]  
                _start = 0                              
                for h_ki in range(_start, len(_high_k_data)):
                    h_k = _high_k_data[h_ki]                    
                    if (h_k['dt'] == k['dt']):                        
                        high_k_data[ki] = [h_k['open'], h_k['close'], h_k['low'], h_k['high']]
                        high_ma_data[ki] = high_ka.ma[h_ki]
                        high_vol_data[ki] = h_k
                        high_macd_data[ki] = high_ka.macd[h_ki]
                        _start = h_ki+1
                        break
            agg_dict[high_ka.freq] = {
                "kline": high_k_data,
                "ma": high_ma_data,
                "vol": high_vol_data,
                "macd": high_macd_data
            }
            
    # K 线主图
    # ------------------------------------------------------------------------------------------------------------------
    chart_k = Kline()
    chart_k.add_xaxis(xaxis_data=dts)
    for k, v in agg_dict.items():
        chart_k.add_yaxis(series_name=k if aggregation else 'kline', y_axis=v['kline'], itemstyle_opts=k_style_opts)
        is_selected = False

    chart_k.set_global_opts(
            legend_opts=legend_opts,
            datazoom_opts=[dz_inside, dz_slider],
            yaxis_opts=yaxis_opts,
            tooltip_opts=tool_tip_opts,
            axispointer_opts=axis_pointer_opts,
            brush_opts=brush_opts,
            title_opts=title_opts,
            xaxis_opts=grid0_xaxis_opts,
    )

    if with_ma:
        # 均线图
        # ------------------------------------------------------------------------------------------------------------------
        ma_keys = [x for x in agg_dict[ka.freq]['ma'][0].keys() if "ma" in x][:3]
        ma_colors = ["#39afe6", "#da6ee8", "#00940b"]

        chart_ma = Line()
        chart_ma.add_xaxis(xaxis_data=dts)

        for key, vals in agg_dict.items():
            for i, k in enumerate(ma_keys):
                y_data = [x[k] if k in x else None for x in v['ma']]
                chart_ma.add_yaxis(series_name=key if aggregation else k.upper(), y_axis=y_data, is_smooth=True,
                                is_selected=True, is_connect_nones=True, symbol_size=0, label_opts=label_not_show_opts,
                                linestyle_opts=opts.LineStyleOpts(opacity=0.8, width=1.0, color=ma_colors[i]))

        chart_ma.set_global_opts(xaxis_opts=grid0_xaxis_opts, legend_opts=legend_not_show_opts)
        chart_k = chart_k.overlap(chart_ma)

    # 缠论结果
    # ------------------------------------------------------------------------------------------------------------------
    def __draw_bi_line(_ka):
        bi_dts = [x['dt'] for x in _ka.bi_list]
        bi_val = [x['bi'] for x in _ka.bi_list]
        chart_bi = Line()
        chart_bi.add_xaxis(bi_dts)
        chart_bi.add_yaxis(series_name=_ka.freq if aggregation else "BI", y_axis=bi_val, is_selected=True,
                        symbol="diamond", symbol_size=10, label_opts=label_not_show_opts,)

        chart_bi.set_global_opts(xaxis_opts=grid0_xaxis_opts, legend_opts=legend_not_show_opts)
        return chart_bi

    if with_bi:
        chark_k = chart_k.overlap(__draw_bi_line(ka))
        for _ka in ka.ka_list:
            chark_k = chart_k.overlap(__draw_bi_line(_ka))

    def __draw_xd_line(_ka):
        
        xd_dts = [x['dt'] for x in _ka.xd_list]
        xd_val = [x['xd'] for x in _ka.xd_list]
        chart_xd = Line()
        chart_xd.add_xaxis(xd_dts)
        chart_xd.add_yaxis(series_name=_ka.freq if aggregation else "XD", y_axis=xd_val, is_selected=True, symbol="triangle", symbol_size=10,)

        chart_xd.set_global_opts(xaxis_opts=grid0_xaxis_opts, legend_opts=legend_not_show_opts)
        return chart_xd

    if with_xd:
        chark_k = chart_k.overlap(__draw_xd_line(ka))
        for _ka in ka.ka_list:
            chark_k = chart_k.overlap(__draw_xd_line(_ka))

    def __draw_zs_area(_ka):
        lines = []
        scatters = []
        for _zs in _ka.zs_list:
            x_start = _zs['start_point']['dt']

            if _zs['zs_finished']:# 中枢完成
                x_end = _zs['end_point']['dt']

                chart_b = EffectScatter()

                if 'buy3' in _zs:
                    chart_b.add_xaxis([_zs['buy3']['dt']])
                    chart_b.add_yaxis(series_name=_ka.freq if aggregation else "B", y_axis=[_zs['buy3']['xd']], is_selected=False, symbol="circle", symbol_size=8,
                                itemstyle_opts=opts.ItemStyleOpts(color="red",))
                    chart_b.set_global_opts(xaxis_opts=grid0_xaxis_opts, legend_opts=legend_not_show_opts)
                    scatters.append(chart_b)
                elif 'sell3' in _zs:
                    chart_b.add_xaxis([_zs['sell3']['dt']])
                    chart_b.add_yaxis(series_name=_ka.freq if aggregation else "S", y_axis=[_zs['sell3']['xd']], is_selected=False, symbol="circle", symbol_size=8,
                                itemstyle_opts=opts.ItemStyleOpts(color="green",))
                    chart_b.set_global_opts(xaxis_opts=grid0_xaxis_opts, legend_opts=legend_not_show_opts)
                    scatters.append(chart_b)
            elif len(_zs['points'])>=5:# 中枢成立但未完成，有3笔或段以上
                x_end = _zs['points'][-1]['dt']
            else:                       # 中枢未完成，且未确定
                continue
            
            ZD = _zs['ZD']
            ZG = _zs['ZG']
            area_data=[[ {'xAxis': x_start, 'yAxis': ZD, 'value': ZD }, {'xAxis': x_end, 'yAxis': ZG, 'value': ZG }]]
            line = (Line()
            .add_xaxis([x_start, x_end])
            .add_yaxis(series_name=_ka.freq if aggregation else "ZS", y_axis=[ZD, ZG], symbol='none' 
            """        
            , markpoint_opts = opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="ZG"),
                    opts.MarkPointItem(type_="min", name="ZD"),
                ]
            )
            """
            , markline_opts=opts.MarkLineOpts(
                label_opts=opts.LabelOpts(
                    position="middle", color="blue", font_size=15,
                ),
                linestyle_opts=opts.LineStyleOpts(type_="dashed"),
                data=area_data,
                symbol=["none", "none"],
            )
            )
            .set_series_opts(
                markarea_opts=opts.MarkAreaOpts(data=area_data, itemstyle_opts=opts.ItemStyleOpts(color="#dcdcdc",opacity=0.1))
            ))
            lines.append(line)
        return lines, scatters

    if with_zs:
        _areas, _scatters = __draw_zs_area(ka)
        for _ka in ka.ka_list:
            _a, _s = __draw_zs_area(_ka)
            _areas.extend(_a)
            _scatters.extend(_s)
        for _area in _areas:
            chark_k = chart_k.overlap(_area)
        for _scatter in _scatters:
            chark_k = chart_k.overlap(_scatter)

    # if with_vol:
    # 成交量图
    # ------------------------------------------------------------------------------------------------------------------
    chart_vol = Bar()
    chart_vol.add_xaxis(dts)
    for k, v in agg_dict.items():
        vol = []
        for row in v['vol']:
            if not row:
                row = {'close': 0, 'open': 0, 'vol': 0}
            item_style = red_item_style if row['close'] > row['open'] else green_item_style
            bar = opts.BarItem(name=None, value=row['vol'], itemstyle_opts=item_style, label_opts=label_not_show_opts)
            vol.append(bar)
        chart_vol.add_yaxis(series_name=k if aggregation else "Volume", y_axis=vol, bar_width='60%')

    chart_vol.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=1,
                axislabel_opts=opts.LabelOpts(is_show=True, font_size=8, color="#9b9da9"),
            ),
            yaxis_opts=yaxis_opts, legend_opts=legend_not_show_opts,
        )

    #if with_macd:
    # MACD图
    # ------------------------------------------------------------------------------------------------------------------
    
    chart_macd = Bar()
    chart_macd.add_xaxis(dts)
    
    for k, v in agg_dict.items():
        macd_bar = []
        for row in v['macd']:
            if not row:
                row = {'macd': 0}
            item_style = red_item_style if row['macd'] > 0 else green_item_style
            bar = opts.BarItem(name=None, value=round(row['macd'], 4), itemstyle_opts=item_style, label_opts=label_not_show_opts)
            macd_bar.append(bar)

        chart_macd.add_yaxis(series_name=k if aggregation else "MACD", y_axis=macd_bar, bar_width='60%')

    chart_macd.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=2,
                split_number=4,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=True, color="#c7c7c7"),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )


    line = Line()
    line.add_xaxis(dts)
    for k, v in agg_dict.items():
        macd = v['macd']
        diff = [round(x['diff'], 4) if x else None for x in macd]
        dea = [round(x['dea'], 4) if x else None for x in macd]        
        line.add_yaxis(series_name=k if aggregation else "DIFF", y_axis=diff, label_opts=label_not_show_opts, is_symbol_show=False
                    , is_connect_nones=True, linestyle_opts=opts.LineStyleOpts(opacity=0.8, width=1.0, color="#EDCB89"))
        line.add_yaxis(series_name=k if aggregation else "DEA", y_axis=dea, label_opts=label_not_show_opts, is_symbol_show=False
                    , is_connect_nones=True, linestyle_opts=opts.LineStyleOpts(opacity=0.8, width=1.0, color="#FFFFFF"))

    chart_macd = chart_macd.overlap(line)
    
    grid0_opts = opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="12%", height="58%")
    grid1_opts = opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="74%", height="8%")
    grid2_opts = opts.GridOpts(pos_left="3%", pos_right="1%", pos_top="86%", height="10%")
    grid_chart = Grid(init_opts)
    grid_chart.add(chart_k, grid_opts=grid0_opts)
    grid_chart.add(chart_vol, grid_opts=grid1_opts)    
    grid_chart.add(chart_macd, grid_opts=grid2_opts)
    return grid_chart
