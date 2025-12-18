"""
Configuration constants for Novig Kalshi Charts.
Minimal MVP configuration - colors, paths, and defaults.
"""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
OUTPUT_DIR = Path.home() / "Downloads"  # Save to Downloads for easy access

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)

# Asset paths
DHARMA_FONT_PATH = ASSETS_DIR / "DharmaGothicE-ExBold.ttf"
LOGO_PNG_PATH = ASSETS_DIR / "novig_n_color.png"
LOGO_SVG_PATH = ASSETS_DIR / "novig_logo.svg"

# Novig brand colors
NOVIG_STYLE = {
    'bg_dark': '#0a1628',      # Dark navy background
    'cyan': '#5cc8ff',         # Primary accent (bars)
    'cyan_glow': '#7dd4ff',    # Glow effects
    'white': '#ffffff',        # Text
    'gray': '#4a5d75',         # Secondary text
    'grid': '#1a2d4a',         # Grid lines
}

# Chart dimensions (MVP: square only)
CHART_CONFIG = {
    'square': {'width': 1080, 'height': 1080, 'dpi': 100},
}

# Video export settings
VIDEO_CONFIG = {
    'codec': 'libx264',
    'bitrate': 8000,  # Higher quality
    'pix_fmt': 'yuv420p',
}

# Default titles for popular series
SERIES_TITLES = {
    'KXMICHCOACH': "WHO WILL BE MICHIGAN'S NEXT HEAD COACH?",
    'KXPRESWIN': "WHO WILL WIN THE 2024 PRESIDENTIAL ELECTION?",
    'KXFEDRATE': "WHAT WILL THE FED DO WITH INTEREST RATES?",
    'KXSUPERBOWL': "WHO WILL WIN THE SUPER BOWL?",
    'KXNFLMVP': "WHO WILL WIN NFL MVP?",
}


def get_default_title(series_ticker: str) -> str:
    """Get a default title for a known series, or generate one."""
    if series_ticker in SERIES_TITLES:
        return SERIES_TITLES[series_ticker]
    cleaned = series_ticker.replace('KX', '').replace('_', ' ')
    return f"{cleaned.upper()} MARKET"
