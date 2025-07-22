import os
import logging
from groq import Groq
from datetime import datetime

logger = logging.getLogger(__name__)

class AIAdvisor:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY', 'default_groq_key')
        self.client = Groq(api_key=self.api_key)
        self.model = "llama3-8b-8192"  # Using Groq's fast Llama model
        
    async def get_trading_advice(self, crypto_symbol, price_data, market_data=None):
        """Get comprehensive AI trading advice"""
        try:
            # Prepare market context
            current_price = price_data.get('usd', 0)
            price_change_24h = price_data.get('usd_24h_change', 0)
            market_cap = price_data.get('usd_market_cap', 0)
            volume_24h = price_data.get('usd_24h_vol', 0)
            
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(
                crypto_symbol, current_price, price_change_24h, 
                market_cap, volume_24h, market_data
            )
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert cryptocurrency analyst and trading advisor with deep knowledge of market dynamics, technical analysis, and fundamental analysis. Provide detailed, actionable trading insights."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=4000,  # Allow for detailed responses
                temperature=0.7
            )
            
            if response.choices and len(response.choices) > 0:
                advice = response.choices[0].message.content
                return advice
            else:
                logger.error("No response from Groq AI")
                return None
                
        except Exception as e:
            logger.error(f"Error getting AI advice for {crypto_symbol}: {e}")
            return None
    
    def _build_analysis_prompt(self, crypto_symbol, current_price, price_change_24h, 
                              market_cap, volume_24h, market_data):
        """Build comprehensive analysis prompt"""
        
        prompt = f"""
Provide a comprehensive cryptocurrency trading analysis for {crypto_symbol.upper()}.

CURRENT MARKET DATA:
- Current Price: ${current_price:,.6f}
- 24h Price Change: {price_change_24h:+.2f}%
- Market Cap: ${market_cap:,.0f}
- 24h Volume: ${volume_24h:,.0f}
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""

        if market_data:
            prompt += f"""
DETAILED MARKET METRICS:
- Market Cap Rank: #{market_data.get('market_cap_rank', 'N/A')}
- Fully Diluted Valuation: ${market_data.get('fully_diluted_valuation', 0):,.0f}
- Price Change 7d: {market_data.get('price_change_percentage_7d', 0):+.2f}%
- Price Change 30d: {market_data.get('price_change_percentage_30d', 0):+.2f}%
- Circulating Supply: {market_data.get('circulating_supply', 0):,.0f}
- Total Supply: {market_data.get('total_supply', 0):,.0f}
- Max Supply: {market_data.get('max_supply', 'Unlimited') if market_data.get('max_supply') else 'Unlimited'}
- All-Time High: ${market_data.get('ath', 0):,.6f}
- ATH Change: {market_data.get('ath_change_percentage', 0):+.2f}%
- All-Time Low: ${market_data.get('atl', 0):,.6f}
- ATL Change: {market_data.get('atl_change_percentage', 0):+.2f}%
- Community Sentiment (Bullish): {market_data.get('sentiment_votes_up_percentage', 0):.1f}%
- Community Sentiment (Bearish): {market_data.get('sentiment_votes_down_percentage', 0):.1f}%
- Developer Score: {market_data.get('developer_score', 0):.1f}/100
- Community Score: {market_data.get('community_score', 0):.1f}/100
- Liquidity Score: {market_data.get('liquidity_score', 0):.1f}/100
"""

        prompt += """
ANALYSIS REQUIREMENTS:
Please provide a detailed analysis covering the following areas with specific actionable insights:

1. **TECHNICAL ANALYSIS:**
   - Price momentum assessment based on recent price movements
   - Support and resistance level analysis
   - Volume analysis and its implications
   - Short-term and medium-term trend identification

2. **FUNDAMENTAL ANALYSIS:**
   - Market capitalization assessment relative to sector
   - Token economics evaluation (supply metrics, inflation/deflation)
   - Adoption and utility analysis
   - Competitive positioning

3. **MARKET SENTIMENT:**
   - Current market sentiment indicators
   - Social media buzz and community strength
   - Institutional interest signals
   - Fear & Greed index implications

4. **RISK ASSESSMENT:**
   - Volatility analysis and risk factors
   - Regulatory risks and market risks
   - Liquidity concerns
   - Correlation with Bitcoin and broader markets

5. **TRADING RECOMMENDATION:**
   Provide a clear recommendation with specific reasoning:
   - **BUY/SELL/HOLD** decision with confidence level (1-10)
   - **Entry points** (if buying) with specific price levels
   - **Exit strategy** with profit targets and stop-loss levels
   - **Position sizing** recommendations
   - **Time horizon** for the trade (short/medium/long term)

6. **SCENARIO ANALYSIS:**
   - Bull case: What could drive price higher (with target prices)
   - Bear case: What could drive price lower (with target prices)
   - Most likely scenario based on current data

7. **ACTIONABLE INSIGHTS:**
   - Specific catalysts to watch
   - Key support/resistance levels to monitor
   - Timeline for potential price movements
   - Risk management strategies

Please be specific with price levels, percentages, and timeframes. Base your analysis on the current market data provided and general market conditions. Avoid generic advice and focus on actionable, data-driven insights specific to {crypto_symbol.upper()}.

Use clear formatting with headers and bullet points for easy reading. Provide reasoning for all recommendations.
"""
        
        return prompt
    
    async def get_market_summary(self, trending_cryptos):
        """Get AI market summary for trending cryptocurrencies"""
        try:
            crypto_list = [f"{crypto['name']} ({crypto['symbol'].upper()})" for crypto in trending_cryptos[:5]]
            
            prompt = f"""
Provide a brief market summary and analysis for the current trending cryptocurrencies:

TRENDING CRYPTOS:
{chr(10).join([f"- {crypto}" for crypto in crypto_list])}

Please provide:
1. Overall market sentiment analysis
2. Key trends driving these cryptocurrencies
3. Market outlook for the next 24-48 hours
4. Top recommendation from the trending list
5. Risk factors to consider

Keep the response concise but informative (under 1000 characters).
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a cryptocurrency market analyst. Provide concise, actionable market insights."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return None
