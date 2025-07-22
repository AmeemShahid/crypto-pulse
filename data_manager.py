import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # File paths
        self.tracked_cryptos_file = os.path.join(data_dir, "tracked_cryptos.json")
        self.guild_categories_file = os.path.join(data_dir, "guild_categories.json")
        self.crypto_channels_file = os.path.join(data_dir, "crypto_channels.json")
        self.bot_settings_file = os.path.join(data_dir, "bot_settings.json")
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def load_json_file(self, file_path, default_value=None):
        """Load JSON file with error handling"""
        if default_value is None:
            default_value = {}
            
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Loaded data from {file_path}")
                    return data
            else:
                logger.info(f"File {file_path} doesn't exist, returning default value")
                return default_value
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return default_value
    
    def save_json_file(self, file_path, data):
        """Save data to JSON file with error handling"""
        try:
            # Create backup if file exists
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                with open(file_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # Save new data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def load_tracked_cryptos(self):
        """Load tracked cryptocurrencies data"""
        return self.load_json_file(self.tracked_cryptos_file, {})
    
    def save_tracked_cryptos(self, tracked_cryptos):
        """Save tracked cryptocurrencies data"""
        # Save directly as the crypto data
        return self.save_json_file(self.tracked_cryptos_file, tracked_cryptos)
    
    def load_guild_categories(self):
        """Load guild categories data"""
        return self.load_json_file(self.guild_categories_file, {})
    
    def save_guild_categories(self, guild_categories):
        """Save guild categories data"""
        return self.save_json_file(self.guild_categories_file, guild_categories)
    
    def load_crypto_channels(self):
        """Load crypto channels data"""
        return self.load_json_file(self.crypto_channels_file, {})
    
    def save_crypto_channels(self, crypto_channels):
        """Save crypto channels data"""
        return self.save_json_file(self.crypto_channels_file, crypto_channels)
    
    def load_bot_settings(self):
        """Load bot settings"""
        default_settings = {
            'price_update_interval': 5,  # minutes
            'significant_change_threshold': 0.01,  # 1%
            'max_tracked_cryptos': 50,
            'enable_auto_updates': True,
            'enable_ai_advice': True
        }
        
        data = self.load_json_file(self.bot_settings_file, default_settings)
        return data.get('settings', default_settings)
    
    def save_bot_settings(self, settings):
        """Save bot settings"""
        data = {
            'last_updated': datetime.now().isoformat(),
            'settings': settings
        }
        return self.save_json_file(self.bot_settings_file, data)
    
    def add_tracked_crypto(self, crypto_symbol, user_id, guild_id=None):
        """Add a cryptocurrency to tracking"""
        tracked_cryptos = self.load_tracked_cryptos()
        
        crypto_data = tracked_cryptos.get('cryptos', {})
        crypto_data[crypto_symbol.upper()] = {
            'added_by': user_id,
            'added_at': datetime.now().isoformat(),
            'guild_id': guild_id,
            'last_price': None,
            'last_update': None
        }
        
        return self.save_tracked_cryptos(crypto_data)
    
    def remove_tracked_crypto(self, crypto_symbol):
        """Remove a cryptocurrency from tracking"""
        tracked_cryptos = self.load_tracked_cryptos()
        crypto_data = tracked_cryptos.get('cryptos', {})
        
        if crypto_symbol.upper() in crypto_data:
            del crypto_data[crypto_symbol.upper()]
            return self.save_tracked_cryptos(crypto_data)
        
        return False
    
    def get_tracked_cryptos_list(self):
        """Get list of tracked cryptocurrency symbols"""
        tracked_cryptos = self.load_tracked_cryptos()
        crypto_data = tracked_cryptos.get('cryptos', {})
        return list(crypto_data.keys())
    
    def cleanup_old_data(self, days=30):
        """Clean up old data files and backups"""
        try:
            import glob
            from datetime import timedelta
            
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # Clean up backup files
            backup_files = glob.glob(os.path.join(self.data_dir, "*.backup"))
            
            for backup_file in backup_files:
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
                if file_mod_time < cutoff_time:
                    os.remove(backup_file)
                    logger.info(f"Removed old backup file: {backup_file}")
            
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
    
    def export_data(self, export_path=None):
        """Export all bot data to a single file"""
        try:
            if not export_path:
                export_path = f"crypto_bot_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'tracked_cryptos': self.load_tracked_cryptos(),
                'guild_categories': self.load_guild_categories(),
                'crypto_channels': self.load_crypto_channels(),
                'bot_settings': self.load_bot_settings()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data exported to: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return None
    
    def import_data(self, import_path):
        """Import bot data from exported file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import each data type
            if 'tracked_cryptos' in import_data:
                cryptos = import_data['tracked_cryptos'].get('cryptos', {})
                self.save_tracked_cryptos(cryptos)
            
            if 'guild_categories' in import_data:
                categories = import_data['guild_categories'].get('categories', {})
                self.save_guild_categories(categories)
            
            if 'crypto_channels' in import_data:
                channels = import_data['crypto_channels'].get('channels', {})
                self.save_crypto_channels(channels)
            
            if 'bot_settings' in import_data:
                settings = import_data['bot_settings'].get('settings', {})
                self.save_bot_settings(settings)
            
            logger.info(f"Data imported from: {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
