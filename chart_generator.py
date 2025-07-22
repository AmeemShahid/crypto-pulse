import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from datetime import datetime
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    def __init__(self):
        # Set matplotlib to use Agg backend for headless operation
        plt.switch_backend('Agg')
        
        # Chart styling
        plt.style.use('dark_background')
        
    def create_candlestick_chart(self, crypto_symbol, ohlc_data, width=12, height=8, days=30):
        """Create a professional candlestick chart with moving averages"""
        try:
            if not ohlc_data or len(ohlc_data) < 2:
                logger.warning(f"Insufficient OHLC data for {crypto_symbol}")
                return None
            
            # Convert OHLC data to DataFrame
            df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Calculate moving averages
            df['MA20'] = df['close'].rolling(window=20, min_periods=1).mean()
            df['MA50'] = df['close'].rolling(window=50, min_periods=1).mean()
            
            # Create figure with dark theme
            fig, ax = plt.subplots(figsize=(width, height))
            fig.patch.set_facecolor('#2C2F33')
            ax.set_facecolor('#36393F')
            
            # Plot candlesticks with improved styling
            for i, row in df.iterrows():
                timestamp = mdates.date2num(row['timestamp'])
                open_price = row['open']
                high_price = row['high']
                low_price = row['low']
                close_price = row['close']
                
                # Determine colors (bright green/red)
                is_bullish = close_price >= open_price
                candle_color = '#00FF00' if is_bullish else '#FF0000'
                wick_color = '#00FF00' if is_bullish else '#FF0000'
                
                # Draw the high-low wick
                ax.plot([timestamp, timestamp], [low_price, high_price], 
                       color=wick_color, linewidth=1.2, alpha=0.8)
                
                # Calculate candle body
                body_height = abs(close_price - open_price)
                body_bottom = min(open_price, close_price)
                candle_width = 0.6
                
                # Draw candle body with proper fill
                if body_height > 0:
                    rect = Rectangle((timestamp - candle_width/2, body_bottom), 
                                   candle_width, body_height,
                                   facecolor=candle_color, 
                                   edgecolor=candle_color,
                                   alpha=0.9,
                                   linewidth=0.8)
                    ax.add_patch(rect)
                else:
                    # Doji candle (open == close)
                    ax.plot([timestamp - candle_width/2, timestamp + candle_width/2], 
                           [close_price, close_price], 
                           color=candle_color, linewidth=1.5)
            
            # Plot moving averages with yellow and pink colors
            ax.plot(df['timestamp'], df['MA20'], 
                   color='yellow', linewidth=2, alpha=0.9, label='MA20')
            ax.plot(df['timestamp'], df['MA50'], 
                   color='#ff6b9d', linewidth=2, alpha=0.9, label='MA50')
            
            # Enhanced title and labels
            ax.set_title(f'{crypto_symbol.upper()} - OHLC Chart ({days} days)', 
                        fontsize=18, fontweight='bold', color='white', pad=25)
            
            ax.set_ylabel('Price (USD)', fontsize=14, color='white', fontweight='bold')
            ax.set_xlabel('Date', fontsize=14, color='white', fontweight='bold')
            
            # Enhanced grid matching your example
            ax.grid(True, alpha=0.3, color='#404040', linewidth=0.8)
            ax.set_axisbelow(True)
            
            # Format axes with better styling
            ax.tick_params(axis='both', colors='white', labelsize=11)
            
            # Format y-axis with proper price formatting
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.2f}'))
            
            # Format x-axis with proper date formatting
            if len(df) > 30:
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            else:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df)//10)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center', color='white')
            
            # Add legend with custom styling
            legend = ax.legend(loc='upper left', frameon=True, 
                             facecolor='#2a2a2a', edgecolor='#404040',
                             fontsize=11, labelcolor='white')
            legend.get_frame().set_alpha(0.9)
            
            # Remove top and right spines for cleaner look
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#404040')
            ax.spines['bottom'].set_color('#404040')
            
            # Adjust layout
            plt.tight_layout(pad=2.0)
            
            # Save with high quality
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', 
                                                  prefix=f'{crypto_symbol}_chart_')
            chart_path = temp_file.name
            temp_file.close()
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', 
                       facecolor='#2C2F33', edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Generated enhanced chart for {crypto_symbol}: {chart_path}")
            return chart_path
            
        except Exception as e:
            logger.error(f"Error creating candlestick chart for {crypto_symbol}: {e}")
            return None
    
    def create_price_trend_chart(self, crypto_symbol, price_history, width=10, height=6):
        """Create a simple price trend chart"""
        try:
            if not price_history or len(price_history) < 2:
                logger.warning(f"Insufficient price history for {crypto_symbol}")
                return None
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(width, height))
            fig.patch.set_facecolor('#2C2F33')
            ax.set_facecolor('#36393F')
            
            # Extract timestamps and prices
            timestamps = [datetime.fromtimestamp(item[0]/1000) for item in price_history]
            prices = [item[1] for item in price_history]
            
            # Plot the price line
            ax.plot(timestamps, prices, color='#00D4AA', linewidth=2, alpha=0.8)
            
            # Fill area under the curve
            ax.fill_between(timestamps, prices, alpha=0.3, color='#00D4AA')
            
            # Customize the chart
            ax.set_title(f'{crypto_symbol.upper()} - Price Trend', 
                        fontsize=14, fontweight='bold', color='white', pad=15)
            
            ax.set_xlabel('Time', fontsize=10, color='white')
            ax.set_ylabel('Price (USD)', fontsize=10, color='white')
            
            # Format axes
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='white')
            ax.tick_params(axis='y', colors='white')
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'${x:,.2f}'))
            
            # Add grid
            ax.grid(True, alpha=0.3, color='gray')
            
            # Tight layout
            plt.tight_layout()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', prefix=f'{crypto_symbol}_trend_')
            chart_path = temp_file.name
            temp_file.close()
            
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', 
                       facecolor='#2C2F33', edgecolor='none')
            plt.close(fig)
            
            logger.info(f"Generated trend chart for {crypto_symbol}: {chart_path}")
            return chart_path
            
        except Exception as e:
            logger.error(f"Error creating price trend chart for {crypto_symbol}: {e}")
            return None
