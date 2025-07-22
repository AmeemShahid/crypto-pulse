import os
from datetime import timedelta

class Config:
    """Configuration class for the crypto bot"""
    
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', '')
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'default_groq_key')
    
    # CoinGecko API Configuration
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_REQUEST_TIMEOUT = 30  # seconds
    COINGECKO_RATE_LIMIT_DELAY = 1  # seconds between requests
    
    # Groq AI Configuration
    GROQ_MODEL = "llama3-8b-8192"
    GROQ_MAX_TOKENS = 4000
    GROQ_TEMPERATURE = 0.7
    
    # Bot Configuration
    COMMAND_PREFIX = '!'
    BOT_DESCRIPTION = "AI-powered cryptocurrency tracking bot"
    
    # Price Monitoring Configuration
    PRICE_UPDATE_INTERVAL = 5  # minutes
    SIGNIFICANT_CHANGE_THRESHOLD = 0.01  # 1% change threshold
    MAX_TRACKED_CRYPTOS = 50
    
    # Channel Configuration
    CATEGORY_NAME = "Crypto Tracking"
    CHANNEL_TOPIC_TEMPLATE = "Real-time tracking for {symbol}"
    
    # Chart Configuration
    CHART_WIDTH = 12
    CHART_HEIGHT = 8
    CHART_DPI = 300
    CHART_STYLE = 'dark_background'
    
    # Data Storage Configuration
    DATA_DIRECTORY = "data"
    BACKUP_RETENTION_DAYS = 30
    
    # Keepalive Configuration
    KEEPALIVE_PORT = int(os.getenv('PORT', 5000))
    KEEPALIVE_HOST = '0.0.0.0'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Rate Limiting
    API_RATE_LIMIT = timedelta(seconds=1)
    COMMAND_COOLDOWN = timedelta(seconds=5)
    
    # Error Handling
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    
    # Feature Flags
    ENABLE_AI_ADVICE = True
    ENABLE_CHARTS = True
    ENABLE_AUTO_UPDATES = True
    ENABLE_TRENDING = True
    
    # Message Configuration
    EMBED_COLOR_SUCCESS = 0x00FF00
    EMBED_COLOR_ERROR = 0xFF0000
    EMBED_COLOR_WARNING = 0xFFFF00
    EMBED_COLOR_INFO = 0x0099FF
    EMBED_COLOR_PRIMARY = 0x7289DA
    
    # File Extensions
    CHART_FILE_EXTENSION = '.png'
    DATA_FILE_EXTENSION = '.json'
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN environment variable is required")
        
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == 'default_groq_key':
            errors.append("GROQ_API_KEY environment variable is required")
        
        return errors
    
    @classmethod
    def get_chart_config(cls):
        """Get chart configuration dictionary"""
        return {
            'width': cls.CHART_WIDTH,
            'height': cls.CHART_HEIGHT,
            'dpi': cls.CHART_DPI,
            'style': cls.CHART_STYLE
        }
    
    @classmethod
    def get_api_config(cls):
        """Get API configuration dictionary"""
        return {
            'coingecko_base_url': cls.COINGECKO_BASE_URL,
            'coingecko_timeout': cls.COINGECKO_REQUEST_TIMEOUT,
            'groq_model': cls.GROQ_MODEL,
            'groq_max_tokens': cls.GROQ_MAX_TOKENS,
            'groq_temperature': cls.GROQ_TEMPERATURE
        }
    
    @classmethod
    def get_monitoring_config(cls):
        """Get monitoring configuration dictionary"""
        return {
            'update_interval': cls.PRICE_UPDATE_INTERVAL,
            'change_threshold': cls.SIGNIFICANT_CHANGE_THRESHOLD,
            'max_tracked': cls.MAX_TRACKED_CRYPTOS
        }
