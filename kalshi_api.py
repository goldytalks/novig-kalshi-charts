"""
Kalshi API client for fetching market data.
Minimal implementation for MVP - bar race charts only.
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class KalshiClient:
    """Client for Kalshi public API."""

    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self, rate_limit_delay: float = 0.3):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'NovigCharts/1.0'
        })
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request with rate limiting."""
        self._rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_series_markets(self, series_ticker: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all markets in a series."""
        params = {"series_ticker": series_ticker, "limit": limit}
        response = self._get("/markets", params=params)
        return response.get('markets', [])

    def get_candlesticks(
        self,
        series_ticker: str,
        market_ticker: str,
        days_back: int = 7,
        period_interval: int = 60
    ) -> List[Dict[str, Any]]:
        """Get historical candlestick data for a market."""
        end_ts = int(datetime.now().timestamp())
        start_ts = int((datetime.now() - timedelta(days=days_back)).timestamp())

        endpoint = f"/series/{series_ticker}/markets/{market_ticker}/candlesticks"
        params = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "period_interval": period_interval
        }

        response = self._get(endpoint, params=params)
        return response.get('candlesticks', [])

    def _extract_price(self, candle: Dict) -> float:
        """Extract close price from candlestick (in cents)."""
        if 'price' in candle and isinstance(candle['price'], dict):
            price_data = candle['price']
            return price_data.get('close') or price_data.get('mean') or 0
        return candle.get('close', candle.get('yes_price', 0)) or 0

    def _extract_candidate_name(self, market: Dict) -> str:
        """Extract clean candidate name from market data."""
        # Try yes_sub_title first (most specific)
        if name := market.get('yes_sub_title', '').strip():
            return name
        if name := market.get('subtitle', '').strip():
            return name
        
        # Extract from title pattern "Will X win?"
        title = market.get('title', '')
        for pattern in ['Will ', 'will ']:
            if pattern in title:
                name = title.split(pattern)[-1].split('?')[0].split(' win')[0].split(' be ')[0]
                return name.strip()
        
        # Fall back to ticker suffix
        ticker = market.get('ticker', '')
        if '-' in ticker:
            return ticker.split('-')[-1].upper()
        return ticker or 'Unknown'

    def get_multi_market_history(
        self,
        markets: List[Dict[str, Any]],
        series_ticker: str,
        days_back: int = 7,
        period_interval: int = 60,
        max_markets: int = 10
    ) -> pd.DataFrame:
        """
        Get historical data for multiple markets.
        
        Returns DataFrame with columns: timestamp, candidate1, candidate2, ...
        """
        all_data = []
        markets_to_fetch = markets[:max_markets]

        for i, market in enumerate(markets_to_fetch):
            ticker = market.get('ticker', '')
            name = self._extract_candidate_name(market)
            print(f"  [{i+1}/{len(markets_to_fetch)}] Fetching: {name}")

            try:
                candlesticks = self.get_candlesticks(
                    series_ticker=series_ticker,
                    market_ticker=ticker,
                    days_back=days_back,
                    period_interval=period_interval
                )

                for candle in candlesticks:
                    price_cents = self._extract_price(candle)
                    all_data.append({
                        'timestamp': candle.get('end_period_ts', candle.get('ts')),
                        'candidate': name,
                        'odds': price_cents / 100
                    })

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"    Rate limited, retrying...")
                    time.sleep(2)
                    try:
                        candlesticks = self.get_candlesticks(
                            series_ticker=series_ticker,
                            market_ticker=ticker,
                            days_back=days_back,
                            period_interval=period_interval
                        )
                        for candle in candlesticks:
                            price_cents = self._extract_price(candle)
                            all_data.append({
                                'timestamp': candle.get('end_period_ts', candle.get('ts')),
                                'candidate': name,
                                'odds': price_cents / 100
                            })
                    except Exception as retry_e:
                        print(f"    Retry failed: {retry_e}")
                else:
                    print(f"    Error: {e}")
            except Exception as e:
                print(f"    Error: {e}")

        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Pivot to wide format
        df_wide = df.pivot_table(
            index='timestamp',
            columns='candidate',
            values='odds',
            aggfunc='last'
        ).reset_index()

        df_wide = df_wide.sort_values('timestamp').reset_index(drop=True)
        df_wide = df_wide.ffill().bfill()

        return df_wide
