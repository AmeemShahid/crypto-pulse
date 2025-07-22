# Crypto Discord Bot

## Overview

This is a comprehensive Discord bot for cryptocurrency tracking with AI-powered trading signals. The bot provides real-time price monitoring, automatic channel management, candlestick chart generation, and AI-driven trading advice using Groq AI. It's designed for deployment on both local and cloud environments with built-in keepalive functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

### Chart Requirements:
- OHLC charts should show 30 days of data (not 7 days)
- Include MA20 and MA50 moving averages with yellow and pink colors
- Dark theme with bright green/red candlesticks
- Professional styling matching trading platforms

### Channel Management:
- Category name must be "Crypto Tracking" (not "stocks tracking")
- Each tracked crypto gets its own dedicated channel
- Format: "{crypto}-tracking" (e.g., "btc-tracking")

## System Architecture

### Overall Architecture
The bot follows a modular, component-based architecture with clear separation of concerns:

- **Bot Core**: Discord.py-based bot handling commands and events
- **Data Layer**: File-based JSON storage for configuration and tracking data
- **External APIs**: CoinGecko for crypto data, Groq AI for trading analysis
- **Chart Generation**: Matplotlib-based candlestick chart creation
- **Keepalive Service**: Flask web server for uptime monitoring

### Key Design Decisions
- **Modular Components**: Each major functionality is separated into dedicated classes
- **Async/Await Pattern**: Full async implementation for non-blocking operations
- **File-Based Storage**: JSON files for simplicity and portability
- **Environment-Based Configuration**: Secure token/API key management

## Key Components

### 1. Bot Core (`main.py`)
- **Purpose**: Main Discord bot class extending `commands.Bot`
- **Responsibilities**: Command handling, event processing, component orchestration
- **Architecture**: Uses Discord.py's slash command system and task loops

### 2. Cryptocurrency Tracking (`crypto_tracker.py`)
- **Purpose**: Interface with CoinGecko API for crypto data
- **Key Features**: Price fetching, market data retrieval, rate limiting
- **Error Handling**: Comprehensive retry logic and rate limit management

### 3. AI Trading Advisor (`ai_advisor.py`)
- **Purpose**: Generate AI-powered trading recommendations using Groq
- **Model**: Llama3-8b-8192 via Groq API
- **Analysis Types**: Technical, fundamental, sentiment, and risk assessment

### 4. Chart Generation (`chart_generator.py`)
- **Purpose**: Create professional candlestick charts
- **Library**: Matplotlib with dark theme styling
- **Output**: PNG images for Discord embedding

### 5. Data Management (`data_manager.py`)
- **Purpose**: Handle persistent data storage and retrieval
- **Storage Format**: JSON files with backup functionality
- **Data Types**: Tracked cryptos, guild settings, channel mappings

### 6. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Environment Variables**: Discord tokens, API keys, runtime settings
- **Defaults**: Sensible fallback values for all configurations

### 7. Keepalive Service (`keepalive.py`)
- **Purpose**: HTTP server for uptime monitoring
- **Framework**: Flask with health check endpoints
- **Deployment**: Separate thread to avoid blocking bot operations

## Data Flow

### Command Processing Flow
1. User invokes slash command in Discord
2. Bot validates command and parameters
3. Relevant component processes the request (e.g., CryptoTracker for prices)
4. External API calls are made asynchronously
5. Response data is formatted and sent back to Discord

### Price Tracking Flow
1. Bot maintains list of tracked cryptocurrencies per guild
2. Periodic task loops fetch current prices from CoinGecko
3. Significant price changes trigger automatic channel updates
4. Charts and AI analysis are generated on-demand

### Data Persistence Flow
1. Bot operations modify in-memory data structures
2. Changes are automatically saved to JSON files
3. Backup files are created before overwrites
4. Data is loaded at startup and periodically synchronized

## External Dependencies

### APIs
- **CoinGecko API**: Free tier cryptocurrency data (prices, market data, OHLC)
- **Groq AI API**: Fast LLM inference for trading analysis
- **Discord API**: Bot functionality via Discord.py library

### Key Libraries
- **discord.py**: Discord bot framework with slash command support
- **aiohttp**: Async HTTP client for API requests
- **matplotlib**: Chart generation and visualization
- **pandas**: Data manipulation for OHLC processing
- **flask**: Lightweight web server for keepalive

### Environment Requirements
- **Python 3.8+**: Modern async/await support
- **Environment Variables**: `DISCORD_TOKEN`, `GROQ_API_KEY`, optional `PORT`

## Deployment Strategy

### Local Development
- Direct Python execution with local environment variables
- File-based data persistence in local `data/` directory
- Manual dependency installation via pip

### Cloud Deployment (Replit/Heroku)
- Keepalive server prevents idle shutdown
- Environment variables via platform configuration
- Automatic dependency resolution via requirements.txt
- Health check endpoints for monitoring

### Data Persistence Strategy
- **Local Files**: JSON storage for simplicity and portability
- **Backup System**: Automatic backup creation before data modification
- **Recovery**: Fallback to default values if corruption occurs
- **Future Consideration**: Could be upgraded to database for scalability

### Scaling Considerations
- Single-instance design suitable for most Discord servers
- Rate limiting implemented for API compliance
- Memory-efficient data structures for tracked cryptos
- Modular design allows easy component replacement or enhancement