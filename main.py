import discord
from discord.ext import commands, tasks
import asyncio
import json
import logging
from datetime import datetime
import threading
import os
from crypto_tracker import CryptoTracker
from chart_generator import ChartGenerator
from ai_advisor import AIAdvisor
from data_manager import DataManager
from config import Config
from keepalive import keep_alive

from dotenv import load_dotenv
import os

load_dotenv()  # 👈 Must be before os.getenv

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.guild_messages = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize components
        self.config = Config()
        self.data_manager = DataManager()
        self.crypto_tracker = CryptoTracker()
        self.chart_generator = ChartGenerator()
        self.ai_advisor = AIAdvisor()
        
        # Bot state
        self.tracked_cryptos = self.data_manager.load_tracked_cryptos()
        self.guild_categories = self.data_manager.load_guild_categories()
        self.crypto_channels = self.data_manager.load_crypto_channels()
        
    async def setup_hook(self):
        """Setup hook called when bot starts"""
        logger.info("Setting up bot...")
        await self.sync_commands()
        
    async def sync_commands(self):
        """Sync slash commands"""
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Start price monitoring task
        self.price_monitor.start()
        logger.info("Price monitoring started")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        logger.info(f"Joined guild: {guild.name} ({guild.id})")
        await self.setup_guild_category(guild)
    
    async def setup_guild_category(self, guild):
        """Setup stocks tracking category in guild"""
        try:
            category_name = "Crypto Tracking"
            category = discord.utils.get(guild.categories, name=category_name)
            
            if not category:
                category = await guild.create_category(category_name)
                logger.info(f"Created category '{category_name}' in {guild.name}")
            
            self.guild_categories[str(guild.id)] = category.id
            self.data_manager.save_guild_categories(self.guild_categories)
            
        except Exception as e:
            logger.error(f"Failed to setup category in {guild.name}: {e}")
    
    async def create_crypto_channel(self, guild, crypto_symbol):
        """Create a dedicated channel for a cryptocurrency"""
        try:
            # First try to find existing category by name
            category_name = "Crypto Tracking"
            category = discord.utils.get(guild.categories, name=category_name)
            
            # If category doesn't exist, create it
            if not category:
                category = await guild.create_category(category_name)
                logger.info(f"Created category '{category_name}' in {guild.name}")
                
                # Store the new category ID
                self.guild_categories[str(guild.id)] = category.id
                self.data_manager.save_guild_categories(self.guild_categories)
            
            channel_name = f"{crypto_symbol.lower()}-tracking"
            
            # Check if channel already exists
            existing_channel = discord.utils.get(category.channels, name=channel_name)
            if existing_channel:
                return existing_channel
            
            # Create new channel
            channel = await guild.create_text_channel(
                channel_name,
                category=category,
                topic=f"Real-time tracking for {crypto_symbol.upper()}"
            )
            
            # Store channel info
            guild_key = str(guild.id)
            if guild_key not in self.crypto_channels:
                self.crypto_channels[guild_key] = {}
            
            self.crypto_channels[guild_key][crypto_symbol.upper()] = channel.id
            self.data_manager.save_crypto_channels(self.crypto_channels)
            
            logger.info(f"Created channel {channel_name} in {guild.name}")
            return channel
            
        except Exception as e:
            logger.error(f"Failed to create channel for {crypto_symbol} in {guild.name}: {e}")
            return None
    
    @tasks.loop(minutes=5)
    async def price_monitor(self):
        """Monitor cryptocurrency prices and post updates"""
        if not self.tracked_cryptos:
            return
        
        try:
            # Get current prices
            current_prices = await self.crypto_tracker.get_multiple_prices(list(self.tracked_cryptos.keys()))
            
            for crypto_symbol, price_data in current_prices.items():
                if crypto_symbol not in self.tracked_cryptos:
                    continue
                
                old_price = self.tracked_cryptos[crypto_symbol].get('last_price', 0)
                new_price = price_data['usd']
                
                # Check for significant price change (1% threshold)
                if old_price and abs((new_price - old_price) / old_price) >= 0.01:
                    await self.broadcast_price_update(crypto_symbol, price_data, old_price)
                
                # Update stored price
                self.tracked_cryptos[crypto_symbol]['last_price'] = new_price
                self.tracked_cryptos[crypto_symbol]['last_update'] = datetime.now().isoformat()
            
            # Save updated prices
            self.data_manager.save_tracked_cryptos(self.tracked_cryptos)
            
        except Exception as e:
            logger.error(f"Error in price monitoring: {e}")
    
    async def broadcast_price_update(self, crypto_symbol, price_data, old_price):
        """Broadcast price update to all relevant channels"""
        new_price = price_data['usd']
        change_percent = ((new_price - old_price) / old_price) * 100
        
        # Create embed
        embed = discord.Embed(
            title=f"{crypto_symbol.upper()} Price Update",
            color=discord.Color.green() if change_percent > 0 else discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="Current Price",
            value=f"${new_price:,.6f}",
            inline=True
        )
        
        embed.add_field(
            name="Previous Price", 
            value=f"${old_price:,.6f}",
            inline=True
        )
        
        embed.add_field(
            name="Change",
            value=f"{change_percent:+.2f}%",
            inline=True
        )
        
        # Send to all guild channels
        for guild in self.guilds:
            guild_key = str(guild.id)
            if guild_key in self.crypto_channels and crypto_symbol.upper() in self.crypto_channels[guild_key]:
                channel_id = self.crypto_channels[guild_key][crypto_symbol.upper()]
                channel = guild.get_channel(channel_id)
                
                if channel and hasattr(channel, 'send'):
                    try:
                        await channel.send(embed=embed)
                    except Exception as e:
                        logger.error(f"Failed to send update to {channel.name}: {e}")

# Initialize bot instance
bot = CryptoBot()

@bot.tree.command(name="price", description="Get current price and OHLC chart for a cryptocurrency")
async def price_command(interaction: discord.Interaction, crypto: str):
    """Get cryptocurrency price with OHLC chart"""
    try:
        await interaction.response.defer(thinking=True)
    except Exception as e:
        logger.error(f"Failed to defer interaction: {e}")
        return
    
    try:
        crypto_symbol = crypto.upper()
        
        # Get price data
        price_data = await bot.crypto_tracker.get_crypto_price(crypto_symbol)
        if not price_data:
            await interaction.followup.send(f"❌ Could not find cryptocurrency: {crypto_symbol}")
            return
        
        # Get OHLC data for chart
        ohlc_data = await bot.crypto_tracker.get_ohlc_data(crypto_symbol)
        
        # Generate chart
        chart_path = None
        if ohlc_data:
            chart_path = bot.chart_generator.create_candlestick_chart(crypto_symbol, ohlc_data)
        
        # Create embed
        embed = discord.Embed(
            title=f"{crypto_symbol} Price Information",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Current Price", value=f"${price_data['usd']:,.6f}", inline=True)
        embed.add_field(name="24h Change", value=f"{price_data.get('usd_24h_change', 0):+.2f}%", inline=True)
        embed.add_field(name="Market Cap", value=f"${price_data.get('usd_market_cap', 0):,.0f}", inline=True)
        
        # Send response with chart
        if chart_path and os.path.exists(chart_path):
            file = discord.File(chart_path, filename=f"{crypto_symbol}_chart.png")
            embed.set_image(url=f"attachment://{crypto_symbol}_chart.png")
            await interaction.followup.send(embed=embed, file=file)
            
            # Clean up chart file
            try:
                os.remove(chart_path)
            except:
                pass
        else:
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        logger.error(f"Error in price command: {e}")
        await interaction.followup.send("❌ An error occurred while fetching price data.")

@bot.tree.command(name="trending", description="Get trending cryptocurrencies")
async def trending_command(interaction: discord.Interaction):
    """Get trending cryptocurrencies"""
    await interaction.response.defer()
    
    try:
        trending_data = await bot.crypto_tracker.get_trending_cryptos()
        
        if not trending_data:
            await interaction.followup.send("❌ Could not fetch trending data.")
            return
        
        embed = discord.Embed(
            title="🔥 Trending Cryptocurrencies",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        for i, crypto in enumerate(trending_data[:10], 1):
            name = crypto.get('name', 'Unknown')
            symbol = crypto.get('symbol', 'Unknown').upper()
            price_btc = crypto.get('price_btc', 0)
            
            embed.add_field(
                name=f"{i}. {name} ({symbol})",
                value=f"₿ {price_btc:.8f}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in trending command: {e}")
        await interaction.followup.send("❌ An error occurred while fetching trending data.")

@bot.tree.command(name="advice", description="Get AI-powered trading advice for a cryptocurrency")
async def advice_command(interaction: discord.Interaction, crypto: str):
    """Get AI trading advice"""
    try:
        await interaction.response.defer(thinking=True)
    except Exception as e:
        logger.error(f"Failed to defer interaction: {e}")
        return
    
    try:
        crypto_symbol = crypto.upper()
        
        # Get comprehensive market data
        price_data = await bot.crypto_tracker.get_crypto_price(crypto_symbol)
        if not price_data:
            await interaction.followup.send(f"❌ Could not find cryptocurrency: {crypto_symbol}")
            return
        
        market_data = await bot.crypto_tracker.get_detailed_market_data(crypto_symbol)
        
        # Get AI advice
        advice = await bot.ai_advisor.get_trading_advice(crypto_symbol, price_data, market_data)
        
        if not advice:
            await interaction.followup.send("❌ Could not generate trading advice at this time.")
            return
        
        # Split advice into chunks if too long for Discord
        max_length = 4096
        advice_chunks = [advice[i:i+max_length] for i in range(0, len(advice), max_length)]
        
        for i, chunk in enumerate(advice_chunks):
            embed = discord.Embed(
                title=f"🤖 AI Trading Advice for {crypto_symbol}" + (f" (Part {i+1})" if len(advice_chunks) > 1 else ""),
                description=chunk,
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            
            if i == 0:  # Add price info to first embed
                embed.add_field(name="Current Price", value=f"${price_data['usd']:,.6f}", inline=True)
                embed.add_field(name="24h Change", value=f"{price_data.get('usd_24h_change', 0):+.2f}%", inline=True)
            
            await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in advice command: {e}")
        await interaction.followup.send("❌ An error occurred while generating trading advice.")

@bot.tree.command(name="track", description="Start tracking a cryptocurrency in a dedicated channel")
async def track_command(interaction: discord.Interaction, crypto: str):
    """Start tracking a cryptocurrency"""
    crypto_symbol = crypto.upper()
    
    # Quick response first - no defer needed
    await interaction.response.send_message(f"🔄 Setting up tracking for {crypto_symbol}...", ephemeral=True)
    
    try:        
        # Verify cryptocurrency exists
        price_data = await bot.crypto_tracker.get_crypto_price(crypto_symbol)
        if not price_data:
            await interaction.edit_original_response(content=f"❌ Could not find cryptocurrency: {crypto_symbol}")
            return
        
        # Create dedicated channel
        channel = await bot.create_crypto_channel(interaction.guild, crypto_symbol)
        if not channel:
            await interaction.edit_original_response(content=f"❌ Failed to create tracking channel for {crypto_symbol}")
            return
        
        # Add to tracked cryptos
        bot.tracked_cryptos[crypto_symbol] = {
            'last_price': price_data['usd'],
            'last_update': datetime.now().isoformat(),
            'added_by': interaction.user.id
        }
        
        bot.data_manager.save_tracked_cryptos(bot.tracked_cryptos)
        
        embed = discord.Embed(
            title="✅ Tracking Started",
            description=f"Now tracking {crypto_symbol} in {channel.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Current Price", value=f"${price_data['usd']:,.6f}", inline=True)
        
        await interaction.edit_original_response(content="", embed=embed)
        
        # Send initial message to tracking channel
        welcome_embed = discord.Embed(
            title=f"📊 {crypto_symbol} Tracking Started",
            description=f"This channel will receive real-time updates for {crypto_symbol}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        welcome_embed.add_field(name="Current Price", value=f"${price_data['usd']:,.6f}", inline=True)
        welcome_embed.add_field(name="Started by", value=interaction.user.mention, inline=True)
        
        await channel.send(embed=welcome_embed)
        
    except Exception as e:
        logger.error(f"Error in track command: {e}")
        await interaction.edit_original_response(content="❌ An error occurred while setting up tracking.")

@bot.tree.command(name="untrack", description="Stop tracking a cryptocurrency")
async def untrack_command(interaction: discord.Interaction, crypto: str):
    """Stop tracking a cryptocurrency"""
    await interaction.response.defer()
    
    try:
        crypto_symbol = crypto.upper()
        
        if crypto_symbol not in bot.tracked_cryptos:
            await interaction.followup.send(f"❌ {crypto_symbol} is not currently being tracked.")
            return
        
        # Remove from tracked cryptos
        del bot.tracked_cryptos[crypto_symbol]
        bot.data_manager.save_tracked_cryptos(bot.tracked_cryptos)
        
        # Optionally delete the channel (commented out to preserve chat history)
        # guild_key = str(interaction.guild.id)
        # if guild_key in bot.crypto_channels and crypto_symbol in bot.crypto_channels[guild_key]:
        #     channel_id = bot.crypto_channels[guild_key][crypto_symbol]
        #     channel = interaction.guild.get_channel(channel_id)
        #     if channel:
        #         await channel.delete()
        #         del bot.crypto_channels[guild_key][crypto_symbol]
        #         bot.data_manager.save_crypto_channels(bot.crypto_channels)
        
        embed = discord.Embed(
            title="✅ Tracking Stopped",
            description=f"Stopped tracking {crypto_symbol}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Error in untrack command: {e}")
        await interaction.followup.send("❌ An error occurred while stopping tracking.")

@bot.tree.command(name="help", description="Show bot commands and features")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    embed = discord.Embed(
        title="🤖 Crypto Bot Help",
        description="Your AI-powered cryptocurrency tracking companion",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="/price <crypto>",
        value="Get current price and OHLC candlestick chart",
        inline=False
    )
    
    embed.add_field(
        name="/trending",
        value="View trending cryptocurrencies",
        inline=False
    )
    
    embed.add_field(
        name="/advice <crypto>",
        value="Get AI-powered trading analysis and recommendations",
        inline=False
    )
    
    embed.add_field(
        name="/track <crypto>",
        value="Start tracking a crypto in a dedicated channel",
        inline=False
    )
    
    embed.add_field(
        name="/untrack <crypto>",
        value="Stop tracking a cryptocurrency",
        inline=False
    )
    
    embed.add_field(
        name="Features",
        value="• Real-time price monitoring\n• Automatic channel creation\n• AI trading signals\n• OHLC charts\n• Price alerts",
        inline=False
    )
    
    embed.set_footer(text="Powered by CoinGecko API & Groq AI")
    
    await interaction.response.send_message(embed=embed)

def main():
    """Main function to run the bot"""
    # Start keepalive server in a separate thread
    keepalive_thread = threading.Thread(target=keep_alive, daemon=True)
    keepalive_thread.start()
    logger.info("Keepalive server started")
    
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    # Run the bot
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()
