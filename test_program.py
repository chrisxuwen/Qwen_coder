#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试程序的核心功能
"""
import sys
sys.path.append('/workspace')

from stock_indicator_monitor import calculate_macd, calculate_rsi, detect_macd_signals, detect_rsi_signals
import yfinance as yf

def test_with_sample_data():
    """使用真实数据测试程序功能"""
    print("正在获取AAPL的历史数据进行测试...")
    
    # 获取AAPL的数据作为示例
    try:
        stock = yf.Ticker("AAPL")
        data = stock.history(period="2mo")  # 获取2个月的数据
        
        if data.empty:
            print("无法获取数据")
            return
        
        print(f"获取到 {len(data)} 条数据")
        
        # 计算MACD
        print("\n计算MACD指标...")
        macd_line, signal_line, histogram = calculate_macd(data)
        
        # 计算RSI
        print("计算RSI指标...")
        rsi = calculate_rsi(data)
        
        # 检测信号
        print("检测MACD信号...")
        macd_buy_signals, macd_sell_signals = detect_macd_signals(macd_line, signal_line)
        
        print("检测RSI信号...")
        rsi_buy_signals, rsi_sell_signals = detect_rsi_signals(rsi)
        
        # 显示结果
        print(f"\n--- 测试结果 ---")
        print(f"最新MACD值: {macd_line.iloc[-1]:.4f}")
        print(f"最新信号线值: {signal_line.iloc[-1]:.4f}")
        print(f"最新RSI值: {rsi.iloc[-1]:.2f}")
        
        print(f"MACD买入信号次数: {len(macd_buy_signals)}")
        print(f"MACD卖出信号次数: {len(macd_sell_signals)}")
        
        print(f"RSI买入信号次数: {len(rsi_buy_signals)}")
        print(f"RSI卖出信号次数: {len(rsi_sell_signals)}")
        
        print("程序功能测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_with_sample_data()