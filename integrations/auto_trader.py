from polymarket.lib.trade import TradeExecutor
from polymarket.lib.position_storage import PositionStorage
from polymarket.lib.wallet_manager import WalletManager

class AutoTrader:
    def __init__(self, private_key=None, max_position_size=50):
        self.wallet = WalletManager(private_key)
        self.trade_executor = TradeExecutor()
        self.position_storage = PositionStorage()
        self.max_position_size = max_position_size
    
    async def execute_trade(self, market_id, side, amount):
        """Execute trade with risk management"""
        # Check position limits
        if not self.check_position_limits(amount):
            return {"success": False, "reason": "Position limit exceeded"}
            
        # Validate wallet balance
        if not await self.wallet.has_sufficient_balance(amount):
            return {"success": False, "reason": "Insufficient balance"}
        
        # Execute the trade
        try:
            result = await self.trade_executor.execute(
                market_id=market_id,
                side=side,
                amount=amount
            )
            
            if result["success"]:
                # Record position
                self.position_storage.add_position({
                    "market_id": market_id,
                    "side": side,
                    "amount": amount,
                    "entry_price": result["price"],
                    "timestamp": result["timestamp"]
                })
                
            return result
            
        except Exception as e:
            return {"success": False, "reason": str(e)}
    
    def check_position_limits(self, new_amount):
        """Check if new trade would exceed position limits"""
        total_exposure = self.get_total_exposure()
        return total_exposure + new_amount <= self.max_position_size
    
    def get_total_exposure(self):
        """Calculate total position exposure"""
        positions = self.position_storage.get_all_positions()
        return sum(float(pos["amount"]) for pos in positions)