#!/usr/bin/env python3
"""
Novig Kalshi Charts - CLI
Generate animated bar race charts from Kalshi prediction market data.

Usage:
    python main.py --series KXMICHCOACH --days 7
    python main.py --series KXPRESWIN --title "2024 Election" --output election.mp4
"""

import argparse
from datetime import datetime

from kalshi_api import KalshiClient
from chart_generator import create_multi_market_chart
from config import OUTPUT_DIR, get_default_title


def main():
    parser = argparse.ArgumentParser(
        description="Generate animated bar race charts from Kalshi market data"
    )
    parser.add_argument("--series", required=True, help="Kalshi series ticker (e.g., KXMICHCOACH)")
    parser.add_argument("--days", type=int, default=7, help="Days of historical data (default: 7)")
    parser.add_argument("--output", help="Output filename (default: auto-generated)")
    parser.add_argument("--title", help="Custom chart title")
    
    args = parser.parse_args()
    
    # Generate output filename
    if args.output:
        output_file = args.output if args.output.endswith('.mp4') else f"{args.output}.mp4"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{args.series}_{timestamp}.mp4"
    
    output_path = OUTPUT_DIR / output_file
    title = args.title or get_default_title(args.series)
    
    print(f"Series: {args.series}")
    print(f"Days: {args.days}")
    print(f"Title: {title}")
    print(f"Output: {output_path}")
    print()
    
    # Fetch data
    client = KalshiClient()
    
    print("Loading markets...")
    markets = client.get_series_markets(args.series)
    
    if not markets:
        print(f"Error: No markets found for series {args.series}")
        return 1
    
    print(f"Found {len(markets)} markets")
    top_markets = markets[:8]
    print(f"Using top {len(top_markets)} for chart\n")
    
    print("Fetching historical data...")
    df = client.get_multi_market_history(
        top_markets,
        args.series,
        days_back=args.days,
        max_markets=len(top_markets)
    )
    
    if df.empty:
        print("Error: No historical data available")
        return 1
    
    print(f"\nLoaded {len(df)} data points")
    print(f"Range: {df['timestamp'].min()} to {df['timestamp'].max()}\n")
    
    print("Generating chart (this may take a minute)...")
    
    result_path = create_multi_market_chart(
        df=df,
        title=title.upper(),
        output=str(output_path),
        fps=30,
        duration=8.0,
        format='square',
        max_candidates=8,
        show_gridlines=True
    )
    
    print(f"\n✅ Done! Saved to: {result_path}")
    return 0


if __name__ == "__main__":
    exit(main())
