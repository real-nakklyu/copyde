class BinanceOfficialCopyTradingClient:
    """Abstraction point for official Binance Copy Trading endpoints when available."""

    async def list_supported_features(self) -> dict:
        return {"available": False, "message": "Official copy-trading endpoint support is not enabled in this app."}

