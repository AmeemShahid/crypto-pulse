# Crypto Discord Bot

A comprehensive Discord bot for real-time cryptocurrency tracking with AI-powered trading signals, automatic channel management, and local/cloud deployment compatibility.

## Features

### 🔥 Core Features
- **Real-time Price Tracking**: Monitor cryptocurrency prices with automatic updates
- **AI Trading Signals**: Get detailed buy/sell/hold recommendations using Groq AI
- **Automatic Channel Management**: Creates dedicated tracking channels for each cryptocurrency
- **OHLC Charts**: Beautiful candlestick charts for technical analysis
- **Trending Cryptos**: Stay updated with market trending cryptocurrencies

### 📊 Commands
- `/price <crypto>` - Get current price and OHLC candlestick chart
- `/trending` - View trending cryptocurrencies
- `/advice <crypto>` - Get AI-powered trading analysis and recommendations
- `/track <crypto>` - Start tracking a crypto in a dedicated channel
- `/untrack <crypto>` - Stop tracking a cryptocurrency
- `/help` - Show all available commands

### 🤖 AI Features
- Comprehensive market analysis using Groq AI
- Technical and fundamental analysis
- Risk assessment and position sizing recommendations
- Market sentiment analysis
- Detailed trading signals with entry/exit points

## Quick Setup

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Groq AI API Key (free tier available)

### Local Installation (Easy Method)

1. **Download all files** to a folder on your computer

2. **For Windows users:**
   - Double-click `run_local.bat`
   - Follow the setup prompts

3. **For Linux/Mac users:**
   - Run: `./run_local.sh`
   - Follow the setup prompts

### Manual Installation

1. **Install dependencies:**
   ```bash
   pip install discord.py aiohttp matplotlib pandas groq flask python-dotenv
   ```

2. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the bot:**
   ```bash
   python main.py
   ```

### Environment Variables
Create a `.env` file with:

```bash
DISCORD_TOKEN=your_discord_bot_token
GROQ_API_KEY=your_groq_api_key
PORT=5000  # Optional, for keepalive server
```

### UptimeRobot Setup (Keep Bot Running 24/7)

The bot includes a keepalive server that prevents it from sleeping on cloud platforms:

1. **Keepalive URL**: `http://your-domain:5000/ping`
2. **Health Check**: `http://your-domain:5000/health`
3. **UptimeRobot Settings**:
   - Monitor Type: HTTP(s)
   - URL: Your keepalive URL
   - Interval: 5 minutes

### Getting API Keys

#### Discord Bot Token:
1. Go to https://discord.com/developers/applications
2. Create new application → Bot section
3. Copy the token and add to `.env` file
4. Enable necessary bot permissions in OAuth2 section

#### Groq AI API Key:
1. Visit https://console.groq.com
2. Sign up for free account
3. Create API key in dashboard
4. Add to `.env` file

## Features in Detail

### 🔄 Automatic Channel Management
- Creates "stocks tracking" category automatically
- Creates dedicated channels for each tracked crypto
- Example: `#bitcoin-tracking`, `#ethereum-tracking`

### 📊 Real-time Price Monitoring
- 5-minute price check intervals
- Automatic alerts for 1%+ price changes
- Persistent data storage in JSON files

### 🤖 AI Trading Analysis
- Powered by Groq's fast Llama3-8b model
- Comprehensive technical and fundamental analysis
- Risk assessment with specific entry/exit points
- No word limits on detailed trading signals

### 📈 Professional Charts
- OHLC candlestick charts with 7-day history
- Dark theme optimized for Discord
- High-resolution PNG output

### 💾 Local Storage & Portability
- No database required - uses JSON files
- All data stored in `data/` folder
- Easy backup and restore
- Works offline for basic functions

## File Structure

```
crypto-bot/
├── main.py              # Main bot file
├── crypto_tracker.py    # CoinGecko API handler
├── chart_generator.py   # Chart creation
├── ai_advisor.py        # Groq AI integration
├── data_manager.py      # JSON data management
├── config.py           # Configuration settings
├── keepalive.py        # UptimeRobot server
├── setup_local.py      # Local setup script
├── run_local.bat       # Windows launcher
├── run_local.sh        # Linux/Mac launcher
├── .env.example        # Environment template
├── deps.txt           # Dependencies list
└── data/              # Auto-created data folder
