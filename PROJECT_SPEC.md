# Novig Kalshi Charts - MVP Project Specification

## Overview

A minimal Python CLI tool that generates animated bar race charts from Kalshi prediction market data. This MVP focuses on core functionality with clean, aesthetically pleasing design - we'll iterate and add features later.

---

## MVP Scope

**What's Included:**

- Bar race chart generation (multi-candidate comparison)
- Kalshi API integration for fetching market data
- Novig brand styling (dark navy background, cyan bars, proper fonts, logo)
- Clean, aesthetically pleasing design
- MP4 video output
- Simple CLI interface

**What's Deferred (for future iterations):**

- Streamlit web dashboard
- Line charts (single market)
- Multiple output formats (GIF, different aspect ratios)
- Configurable settings UI (hardcoded defaults for MVP)

---

## Architecture

```
novig-kalshi-charts/
├── main.py              # Simple CLI entry point
├── kalshi_api.py        # Kalshi API wrapper
├── chart_generator.py   # Bar race animation engine
├── config.py            # Configuration (colors, fonts, paths)
├── requirements.txt     # Python dependencies
├── assets/
│   ├── DharmaGothicE-ExBold.ttf   # Brand font
│   └── novig_n_color.png          # Logo PNG
└── output/              # Generated videos
```

---

## Core Components

### 1. `main.py` - CLI Entry Point

Simple command-line interface:

```bash
python main.py --series KXMICHCOACH --days 7 --output chart.mp4
```

**Arguments:**

- `--series`: Kalshi series ticker (required)
- `--days`: Days of historical data (default: 7)
- `--output`: Output filename (default: `chart.mp4`)
- `--title`: Optional custom title

### 2. `kalshi_api.py` - API Client

Kalshi public API wrapper with:

- `get_series_markets(series_ticker)` - Get all markets in series
- `get_multi_market_history(markets, series, days_back)` - Fetch historical data
- Basic rate limiting (0.3s delay)
- Returns DataFrame with columns: `timestamp`, `candidate1`, `candidate2`, ...

API endpoint: `https://api.elections.kalshi.com/trade-api/v2`

### 3. `chart_generator.py` - Chart Animation

Clean, aesthetically pleasing bar race animator:

- Horizontal bars showing candidate odds over time
- Smooth interpolation between data points
- Novig brand styling:
  - Dark navy background (#0a1628)
  - Cyan bars (#5cc8ff) with subtle glow effects
  - White text for candidate names and percentages
  - Dharma Gothic font for all text
  - Novig logo in bottom-left corner (properly sized)
  - Timestamp in bottom-right
- Hardcoded: 30 FPS, 8 seconds duration, 1080x1080 square format
- Top 8 candidates by default
- Clean layout with proper spacing and typography

### 4. `config.py` - Configuration

Essential constants:

- Brand colors (dark navy, cyan, etc.)
- Font path (Dharma Gothic)
- Logo path (Novig logo PNG)
- Chart dimensions (1080x1080)
- Default FPS (30), duration (8s)
- Output directory path

---

## Dependencies

```
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
Pillow>=9.0.0
ffmpeg-python>=0.2.0
```

**Note:** Requires `ffmpeg` installed on system (for MP4 encoding). Assets folder must contain:
- `DharmaGothicE-ExBold.ttf` (font file)
- `novig_n_color.png` (logo file)

---

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install ffmpeg (required for MP4 export)
brew install ffmpeg  # macOS
# apt install ffmpeg  # Linux

# 3. Run
python main.py --series KXMICHCOACH --days 7
```

---

## Usage

```bash
# Basic usage
python main.py --series KXMICHCOACH --days 7 --output michigan.mp4

# With custom title
python main.py --series KXPRESWIN --days 14 --title "2024 Election" --output election.mp4
```

---

## Output

- MP4 video file saved to `output/` directory
- 1080x1080 square format
- 8 seconds duration at 30 FPS
- Shows top 8 candidates by current odds

---

## Data Flow

1. User provides series ticker via CLI
2. `kalshi_api.py` fetches all markets in series
3. Fetches historical candlestick data for top markets
4. `chart_generator.py` creates animated bar race
5. Saves MP4 to output directory

---

## Visual Layout (Bar Race)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│          WHO WILL BE MICHIGAN'S NEXT HEAD COACH?        │  <- Title (38pt, white, Dharma Gothic)
│                    NOVIG MARKET DATA                     │  <- Subtitle (18pt, cyan)
│                                                         │
│  SHERRONE MOORE ████████████████████████████  45.2%    │  <- Bars with glow
│  LANCE LEIPOLD  ██████████████████           30.1%     │
│  MATT RHULE     ████████████                 18.5%     │
│  DEION SANDERS  ██████                        6.2%     │
│                                                         │
│                                                         │
│  [N Logo]                            Dec 17, 2024 14:30 │  <- Logo + timestamp
└─────────────────────────────────────────────────────────┘
```

---

## Animation Details

- **Frame Interpolation**: Smooth transitions between data points using linear interpolation
- **Position Transitions**: Bars smoothly animate when rankings change (0.15 transition speed)
- **Glow Effects**: Cyan glow behind bars for depth
- **Highlight Effects**: White highlight strip on top of each bar
- **Logo Placement**: Bottom-left corner, properly sized (~8% of height)
- **Typography**: Dharma Gothic font for all text elements

---

## Simplifications for MVP

1. **No Streamlit** - CLI only for MVP (can add web UI later)
2. **No line charts** - Bar race only (can add single-market charts later)
3. **Hardcoded defaults** - No configuration UI (FPS, duration, format fixed)
4. **MP4 only** - No GIF option (can add later)
5. **Square format only** - No wide/other aspect ratios (can add later)
6. **Top 8 candidates** - Fixed limit, no selection UI (can add later)

**What we keep for MVP (smart, simple, nice-looking):**

- ✅ Custom Dharma Gothic font (looks professional)
- ✅ Novig logo placement (branding)
- ✅ Clean aesthetics (proper colors, spacing, typography)
- ✅ Smooth animations (interpolation, transitions)
- ✅ Subtle visual effects (glow, highlights for polish)

---

## API Rate Limiting

The Kalshi public API has rate limits. The client handles this with:
- 0.3s delay between requests
- Automatic retry on 429 errors (2s wait)
- Default limit of 10 markets per multi-market query

---

## Popular Kalshi Markets

| Series Ticker | Description |
|--------------|-------------|
| `KXMICHCOACH` | Michigan next head coach |
| `KXPRESWIN` | Presidential election winner |
| `KXFEDRATE` | Fed rate decisions |
| `KXSUPERBOWL` | Super Bowl winner |
| `KXNFLMVP` | NFL MVP |
| `KXGDP` | GDP growth |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No markets found" | Verify the series ticker exists on Kalshi |
| Rate limiting errors | Wait and retry, or reduce market count |
| Font not loading | Ensure `DharmaGothicE-ExBold.ttf` is in `assets/` |
| Logo not showing | Ensure `novig_n_color.png` is in `assets/` |
| Video not playing | Use VLC; file uses H.264 codec |
| ffmpeg errors | Ensure ffmpeg is installed and in PATH |

---

## Future Iterations

After MVP is working, we can add:

- Streamlit web dashboard (interactive UI)
- Line charts for single markets
- Multiple output formats (GIF, different sizes)
- Configurable settings UI (FPS, duration, format selection)
- Candidate selection UI (choose which candidates to include)
- More chart types

---

## Success Criteria

MVP is complete when:

- ✅ Can generate a bar race chart from any Kalshi series
- ✅ Video plays correctly and shows animated bars
- ✅ Novig brand styling applied (colors, fonts, logo)
- ✅ Looks aesthetically pleasing (clean layout, proper typography)
- ✅ Works via simple CLI command
- ✅ Handles common errors gracefully (no data, API errors)
