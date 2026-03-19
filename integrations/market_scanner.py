from polymarket.lib.gamma_client import GammaClient
from polymarket.lib.coverage import CoverageTier
from datetime import datetime, timedelta

class MarketScanner:
    def __init__(self):
        self.gamma = GammaClient()
        self.coverage = CoverageTier()
    
    async def scan_trending(self, limit=10):
        """Scan trending markets and return opportunities"""
        markets = await self.gamma.get_trending_markets(limit=limit)
        return self.analyze_markets(markets)
    
    def analyze_markets(self, markets):
        opportunities = []
        for market in markets:
            analysis = {
                'id': market['id'],
                'question': market['question'],
                'volume_24h': market['volume24h'],
                'liquidity': market['liquidity'],
                'risk_score': self.calculate_risk(market),
                'potential_return': self.estimate_return(market)
            }
            if self.meets_criteria(analysis):
                opportunities.append(analysis)
        return opportunities
    
    def calculate_risk(self, market):
        # Risk scoring based on multiple factors
        score = 0
        # Volume factor
        if float(market.get('volume24h', 0)) > 10000:
            score += 1
        # Liquidity factor    
        if float(market.get('liquidity', 0)) > 5000:
            score += 1
        # Time factor
        if market.get('expirationDate'):
            expiry = datetime.fromisoformat(market['expirationDate'].replace('Z', '+00:00'))
            if expiry - datetime.now() > timedelta(days=2):
                score += 1
        return score

    def estimate_return(self, market):
        # Conservative return estimation
        yes_price = float(market.get('yes_price', 0))
        no_price = float(market.get('no_price', 0))
        spread = abs(yes_price - no_price)
        volume = float(market.get('volume24h', 0))
        
        if spread > 0.1 and volume > 5000:
            return 'HIGH'
        elif spread > 0.05 and volume > 1000:
            return 'MEDIUM'
        return 'LOW'

    def meets_criteria(self, analysis):
        # Basic filtering criteria
        return (
            analysis['risk_score'] >= 2 and
            analysis['potential_return'] in ['HIGH', 'MEDIUM']
        )