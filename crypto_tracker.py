import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CryptoTracker:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def make_request(self, endpoint, params=None):
        """Make API request with error handling"""
        session = await self.get_session()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Rate limited by CoinGecko API")
                    await asyncio.sleep(60)  # Wait 1 minute
                    return None
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    async def get_crypto_price(self, crypto_symbol):
        """Get current price for a cryptocurrency"""
        try:
            # Convert symbol to CoinGecko ID if needed
            crypto_id = await self.symbol_to_id(crypto_symbol)
            if not crypto_id:
                return None
            
            params = {
                'ids': crypto_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            data = await self.make_request("simple/price", params)
            if data and crypto_id in data:
                return data[crypto_id]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {crypto_symbol}: {e}")
            return None
    
    async def get_multiple_prices(self, crypto_symbols):
        """Get prices for multiple cryptocurrencies"""
        try:
            # Convert symbols to IDs
            crypto_ids = []
            symbol_to_id_map = {}
            
            for symbol in crypto_symbols:
                crypto_id = await self.symbol_to_id(symbol)
                if crypto_id:
                    crypto_ids.append(crypto_id)
                    symbol_to_id_map[crypto_id] = symbol
            
            if not crypto_ids:
                return {}
            
            params = {
                'ids': ','.join(crypto_ids),
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            data = await self.make_request("simple/price", params)
            if not data:
                return {}
            
            # Convert back to symbol-based keys
            result = {}
            for crypto_id, price_data in data.items():
                if crypto_id in symbol_to_id_map:
                    symbol = symbol_to_id_map[crypto_id]
                    result[symbol] = price_data
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting multiple prices: {e}")
            return {}
    
    async def get_ohlc_data(self, crypto_symbol, days=30):
        """Get OHLC data for candlestick chart"""
        try:
            crypto_id = await self.symbol_to_id(crypto_symbol)
            if not crypto_id:
                return None
            
            params = {
                'vs_currency': 'usd',
                'days': days
            }
            
            data = await self.make_request(f"coins/{crypto_id}/ohlc", params)
            return data
            
        except Exception as e:
            logger.error(f"Error getting OHLC data for {crypto_symbol}: {e}")
            return None
    
    async def get_trending_cryptos(self):
        """Get trending cryptocurrencies"""
        try:
            data = await self.make_request("search/trending")
            if data and 'coins' in data:
                return [coin['item'] for coin in data['coins']]
            return []
            
        except Exception as e:
            logger.error(f"Error getting trending cryptos: {e}")
            return []
    
    async def get_detailed_market_data(self, crypto_symbol):
        """Get detailed market data for AI analysis"""
        try:
            crypto_id = await self.symbol_to_id(crypto_symbol)
            if not crypto_id:
                return None
            
            # Get comprehensive coin data
            data = await self.make_request(f"coins/{crypto_id}")
            if not data:
                return None
            
            # Extract relevant market data
            market_data = data.get('market_data', {})
            
            result = {
                'current_price': market_data.get('current_price', {}).get('usd', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'market_cap_rank': market_data.get('market_cap_rank', 0),
                'fully_diluted_valuation': market_data.get('fully_diluted_valuation', {}).get('usd', 0),
                'total_volume': market_data.get('total_volume', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_24h', 0),
                'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_percentage_7d': market_data.get('price_change_percentage_7d', 0),
                'price_change_percentage_30d': market_data.get('price_change_percentage_30d', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'total_supply': market_data.get('total_supply', 0),
                'max_supply': market_data.get('max_supply', 0),
                'ath': market_data.get('ath', {}).get('usd', 0),
                'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                'ath_date': market_data.get('ath_date', {}).get('usd', ''),
                'atl': market_data.get('atl', {}).get('usd', 0),
                'atl_change_percentage': market_data.get('atl_change_percentage', {}).get('usd', 0),
                'atl_date': market_data.get('atl_date', {}).get('usd', ''),
                'roi': data.get('roi', {}),
                'last_updated': data.get('last_updated', ''),
                'description': data.get('description', {}).get('en', ''),
                'categories': data.get('categories', []),
                'public_notice': data.get('public_notice', ''),
                'sentiment_votes_up_percentage': data.get('sentiment_votes_up_percentage', 0),
                'sentiment_votes_down_percentage': data.get('sentiment_votes_down_percentage', 0),
                'developer_score': data.get('developer_score', 0),
                'community_score': data.get('community_score', 0),
                'liquidity_score': data.get('liquidity_score', 0),
                'public_interest_score': data.get('public_interest_score', 0)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting detailed market data for {crypto_symbol}: {e}")
            return None
    
    async def symbol_to_id(self, symbol):
        """Convert cryptocurrency symbol to CoinGecko ID"""
        try:
            # Cache for symbol to ID mapping
            if not hasattr(self, '_symbol_cache'):
                self._symbol_cache = {}
            
            symbol_upper = symbol.upper()
            if symbol_upper in self._symbol_cache:
                return self._symbol_cache[symbol_upper]
            
            # Search for the coin
            params = {'query': symbol}
            data = await self.make_request("search", params)
            
            if data and 'coins' in data:
                for coin in data['coins']:
                    if coin['symbol'].upper() == symbol_upper:
                        coin_id = coin['id']
                        self._symbol_cache[symbol_upper] = coin_id
                        return coin_id
            
            # Fallback: try common mappings
            common_mappings = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'XRP': 'ripple',
                'LTC': 'litecoin',
                'BCH': 'bitcoin-cash',
                'LINK': 'chainlink',
                'MATIC': 'matic-network',
                'SOL': 'solana',
                'AVAX': 'avalanche-2',
                'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu'
            }
            
            if symbol_upper in common_mappings:
                coin_id = common_mappings[symbol_upper]
                self._symbol_cache[symbol_upper] = coin_id
                return coin_id
            
            logger.warning(f"Could not find CoinGecko ID for symbol: {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error converting symbol {symbol} to ID: {e}")
            return None
