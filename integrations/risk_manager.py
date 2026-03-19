from datetime import datetime, timedelta
import json
import os

class RiskManager:
    def __init__(self, max_daily_loss=10, max_position_size=50):
        self.max_daily_loss = max_daily_loss
        self.max_position_size = max_position_size
        self.positions_file = 'positions.json'
        self.trades_file = 'trades.json'
        
    def can_take_trade(self, market_id, amount):
        """Check if trade meets risk criteria"""
        daily_pnl = self.calculate_daily_pnl()
        total_exposure = self.get_total_exposure()
        
        checks = {
            "within_daily_loss": daily_pnl > -self.max_daily_loss,
            "within_position_limit": total_exposure + amount <= self.max_position_size,
            "market_diversified": self.is_market_diversified(market_id)
        }
        
        return all(checks.values()), checks
        
    def calculate_daily_pnl(self):
        """Calculate P&L for current day"""
        try:
            with open(self.trades_file, 'r') as f:
                trades = json.load(f)
                
            today = datetime.now().date()
            daily_trades = [
                t for t in trades 
                if datetime.fromisoformat(t['timestamp']).date() == today
            ]
            
            return sum(float(t['pnl']) for t in daily_trades)
        except FileNotFoundError:
            return 0
            
    def get_total_exposure(self):
        """Get total position exposure"""
        try:
            with open(self.positions_file, 'r') as f:
                positions = json.load(f)
            return sum(float(p['amount']) for p in positions)
        except FileNotFoundError:
            return 0
            
    def is_market_diversified(self, market_id):
        """Check market concentration"""
        try:
            with open(self.positions_file, 'r') as f:
                positions = json.load(f)
                
            market_exposure = sum(
                float(p['amount']) 
                for p in positions 
                if p['market_id'] == market_id
            )
            
            return market_exposure < (self.max_position_size * 0.3)  # Max 30% per market
        except FileNotFoundError:
            return True
            
    def log_trade(self, trade_data):
        """Log trade for tracking"""
        try:
            with open(self.trades_file, 'r') as f:
                trades = json.load(f)
        except FileNotFoundError:
            trades = []
            
        trades.append({
            **trade_data,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(self.trades_file, 'w') as f:
            json.dump(trades, f)