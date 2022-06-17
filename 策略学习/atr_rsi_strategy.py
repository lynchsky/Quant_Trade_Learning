'''策略文件：atr_rsi_strategy.py
ATR 指标：平均真实波动范围(Average True Range)，简称 ATR 指标。ATR 指标主要用来衡量市场波动的强烈度，即用来显示市场变化率的指标。这一指标主要用来衡量价格的波动，并不能直接反映价格趋势及
其趋势稳定性。
RSI 指标：相对强弱指标(Rekatuve Strength Index)。RSI 指标是根据市场上供求关系平稳的原理，通过比较一段时期内单个标的物或整个市场指数的涨跌幅度，来分析判断市场上多空双方买卖力量的强弱程度
，从而判断未来市场趋势的技术指标。

平均真实范围范围（ATR）的计算方法：
1、当前交易日的最高价与最低价间的波幅--今日振幅
2、前一交易日收盘价与当个交易日最高价间的波幅--今日最高与昨收的差价
3、前一交易日收盘价与当个交易日最低价间的波幅--今日最低与昨收的差价
其三者之间的最大值，为真实波幅，在有了真实波幅后，就可以利用一段时间的平均值计算ATR了。至于用多久计算，不同的使用者习惯不同，10天、20天乃至65天都有。

策略原理：ATR 用于过滤，RSI 用于产生交易信号，固定百分比点位移动止损。该策略只用到两个指标。ATR 用于过滤，当 ATR>ATRMa 时，显示市场波动性增大，趋势正在增强。只有在市场出现趋势的时候做单
（追涨杀跌），盈利的机会才会增大。RSI 用于产生交易信号，当 RSI>规定上限时，开仓做多；反之，当 RSI<规定下限时，开仓做空。开仓之后就需要考虑如何盈利离场或止损离场，该策略用固定百分比点位移
动止损。'''


from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class AtrRsiStrategy(CtaTemplate):##
    """"""

    author = "李崇灿"

    '''策略的参数列表，实例化是需要人为指定'''
    atr_length = 22 # ATR的指标计算天数
    atr_ma_length = 10 # 取ATR移动平均的天数
    rsi_length = 5 # RSI指标计算天数
    rsi_entry = 16 #RSI指标入口范围
    trailing_percent = 0.8 #回撤止损百分比
    fixed_size = 1 #每次固定的买卖数量


    '''策略的变量列表，随策略的运行变化'''
    atr_value = 0
    atr_ma = 0
    rsi_value = 0
    rsi_buy = 0
    rsi_sell = 0
    intra_trade_high = 0
    intra_trade_low = 0

    parameters = [
        "atr_length",
        "atr_ma_length",
        "rsi_length",
        "rsi_entry",
        "trailing_percent",
        "fixed_size"
    ]
    variables = [
        "atr_value",
        "atr_ma",
        "rsi_value",
        "rsi_buy",
        "rsi_sell",
        "intra_trade_high",
        "intra_trade_low"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        #super().__init__()，就是在重写的基础上继承父类的init方法，同样可以使用super()去继承其他方法
        self.bg = BarGenerator(self.on_bar)#K线合成器
        self.am = ArrayManager()#K线序列管理工具

    def on_init(self):
        """
        策略初始化时的回调函数
        """
        self.write_log("策略初始化")#windows的日志函数
        #ris_entry是作为策略的参数，实例化可以修改。
        #变量rsi_buy和rsi_sell是策略的变量
        self.rsi_buy = 50 + self.rsi_entry
        self.rsi_sell = 50 - self.rsi_entry

        self.load_bar(10)

    def on_start(self):
        """
        策略启动时的回调函数
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        策略结束时的回调函数
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        收到行情Tick推送的回调函数.
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        收到新K线数据的回调函数.
        """
        #撤销由策略发出的所有活动的委托
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        #根据接收到的K线数据计算相应指标
        atr_array = am.atr(self.atr_length, array=True)#
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_length:].mean()
        self.rsi_value = am.rsi(self.rsi_length)

        if self.pos == 0:#如果当前空值
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            if self.atr_value > self.atr_ma:
                if self.rsi_value > self.rsi_buy:
                    self.buy(bar.close_price + 5, self.fixed_size)
                elif self.rsi_value < self.rsi_sell:
                    self.short(bar.close_price - 5, self.fixed_size)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price

            long_stop = self.intra_trade_high * \
                (1 - self.trailing_percent / 100)
            self.sell(long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.intra_trade_high = bar.high_price

            short_stop = self.intra_trade_low * \
                (1 + self.trailing_percent / 100)
            self.cover(short_stop, abs(self.pos), stop=True)

        self.put_event()

    def on_order(self, order: OrderData):
        """
        收到委托变化推送的回调函数.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        收到成交推送的回调函数.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        收到停止单推送的回调函数.
        """
        pass

