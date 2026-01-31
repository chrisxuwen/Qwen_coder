import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    计算MACD指标
    :param data: 股票数据
    :param fast: 快速EMA周期
    :param slow: 慢速EMA周期
    :param signal: 信号线EMA周期
    :return: MACD线, 信号线, MACD柱状图
    """
    close_prices = data['Close']
    
    # 计算快速和慢速EMA
    ema_fast = close_prices.ewm(span=fast).mean()
    ema_slow = close_prices.ewm(span=slow).mean()
    
    # 计算MACD线
    macd_line = ema_fast - ema_slow
    
    # 计算信号线
    signal_line = macd_line.ewm(span=signal).mean()
    
    # 计算柱状图
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_rsi(data, period=14):
    """
    计算RSI指标
    :param data: 股票数据
    :param period: RSI计算周期
    :return: RSI值
    """
    close_prices = data['Close']
    
    # 计算价格变化
    price_diff = close_prices.diff()
    
    # 分离上涨和下跌的价格变化
    gain = price_diff.where(price_diff > 0, 0)
    loss = -price_diff.where(price_diff < 0, 0)
    
    # 计算平均收益和平均损失
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # 计算RS (相对强度)
    rs = avg_gain / avg_loss
    
    # 计算RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def detect_macd_signals(macd_line, signal_line):
    """
    检测MACD买卖信号
    :param macd_line: MACD线
    :param signal_line: 信号线
    :return: 买入信号、卖出信号列表
    """
    # MACD线上穿信号线为买入信号
    buy_signals = []
    sell_signals = []
    
    for i in range(1, len(macd_line)):
        if macd_line.iloc[i-1] <= signal_line.iloc[i-1] and macd_line.iloc[i] > signal_line.iloc[i]:
            buy_signals.append(i)
        elif macd_line.iloc[i-1] >= signal_line.iloc[i-1] and macd_line.iloc[i] < signal_line.iloc[i]:
            sell_signals.append(i)
    
    return buy_signals, sell_signals


def detect_rsi_signals(rsi_data):
    """
    检测RSI买卖信号
    :param rsi_data: RSI数据
    :return: 买入信号、卖出信号列表
    """
    buy_signals = []  # 当RSI从下向上突破30时为买入信号
    sell_signals = []  # 当RSI从上向下跌破70时为卖出信号
    
    for i in range(1, len(rsi_data)):
        # RSI从下向上突破30为超卖反弹，可能是买入信号
        if pd.notna(rsi_data.iloc[i-1]) and pd.notna(rsi_data.iloc[i]):
            if rsi_data.iloc[i-1] <= 30 and rsi_data.iloc[i] > 30:
                buy_signals.append(i)
            # RSI从上向下跌破70为超买回调，可能是卖出信号
            elif rsi_data.iloc[i-1] >= 70 and rsi_data.iloc[i] < 70:
                sell_signals.append(i)
    
    return buy_signals, sell_signals


def detect_overbought_oversold(rsi_value):
    """
    检测RSI是否处于超买或超卖状态
    :param rsi_value: 当前RSI值
    :return: 状态描述
    """
    if rsi_value > 70:
        return "超买"
    elif rsi_value < 30:
        return "超卖"
    else:
        return "正常"


def get_stock_data(symbol, period="6mo"):
    """
    获取股票数据
    :param symbol: 股票代码
    :param period: 数据时间范围
    :return: 股票数据DataFrame
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        
        if data.empty:
            print(f"无法获取 {symbol} 的数据")
            return None
        
        return data
    except Exception as e:
        print(f"获取 {symbol} 数据时出错: {e}")
        return None


def analyze_stock_indicators(symbol):
    """
    分析股票的技术指标
    :param symbol: 股票代码
    """
    print(f"\n正在分析 {symbol.upper()} 的技术指标...")
    
    # 获取股票数据
    data = get_stock_data(symbol)
    if data is None:
        return
    
    # 计算MACD
    macd_line, signal_line, histogram = calculate_macd(data)
    
    # 计算RSI
    rsi = calculate_rsi(data)
    
    # 添加到数据中
    data['MACD'] = macd_line
    data['Signal_Line'] = signal_line
    data['Histogram'] = histogram
    data['RSI'] = rsi
    
    # 检测MACD信号
    macd_buy_signals, macd_sell_signals = detect_macd_signals(macd_line, signal_line)
    
    # 检测RSI信号
    rsi_buy_signals, rsi_sell_signals = detect_rsi_signals(rsi)
    
    # 显示最新数据
    latest_date = data.index[-1].strftime('%Y-%m-%d')
    latest_price = round(data['Close'].iloc[-1], 2)
    latest_macd = round(data['MACD'].iloc[-1], 4) if pd.notna(data['MACD'].iloc[-1]) else "N/A"
    latest_signal = round(data['Signal_Line'].iloc[-1], 4) if pd.notna(data['Signal_Line'].iloc[-1]) else "N/A"
    latest_rsi = round(data['RSI'].iloc[-1], 2) if pd.notna(data['RSI'].iloc[-1]) else "N/A"
    rsi_status = detect_overbought_oversold(latest_rsi) if isinstance(latest_rsi, float) else "N/A"
    
    print(f"日期: {latest_date}")
    print(f"收盘价: ${latest_price}")
    print(f"MACD: {latest_macd}")
    print(f"信号线: {latest_signal}")
    print(f"RSI: {latest_rsi} ({rsi_status})")
    
    # 显示MACD信号
    print("\n--- MACD 信号 ---")
    if macd_buy_signals:
        recent_macd_buy_dates = [data.index[idx].strftime('%Y-%m-%d') for idx in macd_buy_signals[-3:]]
        print(f"最近MACD买入信号日期: {recent_macd_buy_dates}")
    else:
        print("最近没有MACD买入信号")
    
    if macd_sell_signals:
        recent_macd_sell_dates = [data.index[idx].strftime('%Y-%m-%d') for idx in macd_sell_signals[-3:]]
        print(f"最近MACD卖出信号日期: {recent_macd_sell_dates}")
    else:
        print("最近没有MACD卖出信号")
    
    # 显示RSI信号
    print("\n--- RSI 信号 ---")
    if rsi_buy_signals:
        recent_rsi_buy_dates = [data.index[idx].strftime('%Y-%m-%d') for idx in rsi_buy_signals[-3:]]
        print(f"最近RSI买入信号日期: {recent_rsi_buy_dates}")
    else:
        print("最近没有RSI买入信号")
    
    if rsi_sell_signals:
        recent_rsi_sell_dates = [data.index[idx].strftime('%Y-%m-%d') for idx in rsi_sell_signals[-3:]]
        print(f"最近RSI卖出信号日期: {recent_rsi_sell_dates}")
    else:
        print("最近没有RSI卖出信号")
    
    # 综合信号分析
    print("\n--- 综合信号分析 ---")
    combined_buy_signals = []
    combined_sell_signals = []
    
    # 检查是否有同时出现的MACD和RSI信号
    for date_idx in macd_buy_signals:
        date = data.index[date_idx]
        # 检查该日期附近是否有RSI买入信号
        rsi_buy_dates = [data.index[idx] for idx in rsi_buy_signals]
        for rsi_date in rsi_buy_dates:
            if abs((date - rsi_date).days) <= 2:  # 在2天内同时出现信号
                combined_buy_signals.append(date.strftime('%Y-%m-%d'))
                
    for date_idx in macd_sell_signals:
        date = data.index[date_idx]
        # 检查该日期附近是否有RSI卖出信号
        rsi_sell_dates = [data.index[idx] for idx in rsi_sell_signals]
        for rsi_date in rsi_sell_dates:
            if abs((date - rsi_date).days) <= 2:  # 在2天内同时出现信号
                combined_sell_signals.append(date.strftime('%Y-%m-%d'))
    
    if combined_buy_signals:
        print(f"最近同时出现MACD和RSI买入信号的日期: {combined_buy_signals[-3:]}")
    else:
        print("最近没有同时出现MACD和RSI买入信号")
    
    if combined_sell_signals:
        print(f"最近同时出现MACD和RSI卖出信号的日期: {combined_sell_signals[-3:]}")
    else:
        print("最近没有同时出现MACD和RSI卖出信号")


def main():
    """
    主函数
    """
    print("美股技术指标监测程序 (MACD & RSI)")
    print("=" * 50)
    
    while True:
        symbol = input("\n请输入美股股票代码 (如 AAPL, TSLA, QQQ, SPY 等)，或输入 'quit' 退出: ").strip().upper()
        
        if symbol == 'QUIT':
            print("程序已退出。")
            break
        
        if not symbol:
            print("请输入有效的股票代码。")
            continue
        
        analyze_stock_indicators(symbol)


if __name__ == "__main__":
    main()