"""
Novig Kalshi Charts - Streamlit Dashboard
Generate animated bar race charts from Kalshi prediction market data.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

from kalshi_api import KalshiClient
from chart_generator import create_multi_market_chart, create_preview_image
from config import NOVIG_STYLE

# Page config
st.set_page_config(
    page_title="Novig Charts",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme matching Novig brand
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(180deg, #0d1f35 0%, #060d18 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0a1628;
        border-right: 1px solid #1a3350;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 700;
    }
    
    /* Text */
    p, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background-color: #0f2644 !important;
        color: #ffffff !important;
        border: 1px solid #1e4060 !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: #0f2644 !important;
        border: 1px solid #1e4060 !important;
    }
    
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: #00d4ff !important;
        color: #0a1628 !important;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #00d4ff !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #0091b3 0%, #00d4ff 100%);
        color: #ffffff;
        border: none;
        font-weight: 700;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #00d4ff 0%, #7df3ff 100%);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Success/Info boxes */
    .stSuccess, .stInfo {
        background-color: #0f2644 !important;
        border: 1px solid #00d4ff !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #7df3ff 100%);
        color: #0a1628;
        font-weight: 700;
    }
    
    /* Checkbox */
    .stCheckbox label span {
        color: #ffffff !important;
    }
    
    /* Metric */
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
    }
    
    /* Divider */
    hr {
        border-color: #1a3350 !important;
    }
    
    /* Candidate list styling */
    .candidate-item {
        padding: 8px 12px;
        margin: 4px 0;
        background: #0f2644;
        border-radius: 6px;
        border-left: 3px solid #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# Downloads folder path
DOWNLOADS_FOLDER = Path.home() / "Downloads"

# Popular series for quick selection
POPULAR_SERIES = {
    "Michigan Coach": "KXMICHCOACH",
    "NFL MVP": "KXNFLMVP", 
    "Super Bowl Winner": "KXSUPERBOWL",
    "Fed Interest Rate": "KXFEDRATE",
}

# Initialize session state
if 'markets_loaded' not in st.session_state:
    st.session_state.markets_loaded = False
if 'available_markets' not in st.session_state:
    st.session_state.available_markets = []
if 'selected_candidates' not in st.session_state:
    st.session_state.selected_candidates = []
if 'current_series' not in st.session_state:
    st.session_state.current_series = ""
if 'preview_image' not in st.session_state:
    st.session_state.preview_image = None
if 'preview_df' not in st.session_state:
    st.session_state.preview_df = None
if 'preview_title' not in st.session_state:
    st.session_state.preview_title = None
if 'last_video_path' not in st.session_state:
    st.session_state.last_video_path = None


def extract_candidate_name(market):
    """Extract clean candidate name from market data."""
    if name := market.get('yes_sub_title', '').strip():
        return name
    if name := market.get('subtitle', '').strip():
        return name
    
    title = market.get('title', '')
    for pattern in ['Will ', 'will ']:
        if pattern in title:
            name = title.split(pattern)[-1].split('?')[0].split(' win')[0].split(' be ')[0]
            return name.strip()
    
    ticker = market.get('ticker', '')
    if '-' in ticker:
        return ticker.split('-')[-1].upper()
    return ticker or 'Unknown'


def load_markets(series_ticker):
    """Load available markets for a series."""
    with st.spinner(f"Loading markets for {series_ticker}..."):
        client = KalshiClient()
        markets = client.get_series_markets(series_ticker)
        
        # Extract candidate info
        candidates = []
        for market in markets:
            name = extract_candidate_name(market)
            # Get current price/odds
            yes_price = market.get('yes_bid', 0) or market.get('last_price', 0) or 0
            odds = yes_price / 100 if yes_price else 0
            
            candidates.append({
                'name': name,
                'ticker': market.get('ticker', ''),
                'odds': odds,
                'market': market
            })
        
        # Sort by odds (highest first)
        candidates.sort(key=lambda x: x['odds'], reverse=True)
        
        return candidates


def main():
    # Header
    st.markdown("""
    # 📊 NOVIG CHARTS
    ### Generate Animated Bar Race Charts from Kalshi Markets
    """)
    
    st.divider()
    
    # Sidebar - Settings
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.divider()
        
        # Market Selection
        st.markdown("### 📈 Market")
        
        use_preset = st.toggle("Use preset market", value=True)
        
        if use_preset:
            selected_name = st.selectbox(
                "Select Market",
                options=list(POPULAR_SERIES.keys()),
                index=0
            )
            series_ticker = POPULAR_SERIES[selected_name]
        else:
            series_ticker = st.text_input(
                "Series Ticker",
                value="KXMICHCOACH",
                help="Enter Kalshi series ticker (e.g., KXMICHCOACH)"
            ).upper()
        
        st.markdown(f"**Ticker:** `{series_ticker}`")
        
        # Load markets button
        if st.button("🔄 Load Candidates", use_container_width=True):
            candidates = load_markets(series_ticker)
            st.session_state.available_markets = candidates
            st.session_state.markets_loaded = True
            st.session_state.current_series = series_ticker
            # Pre-select top 8 by default
            st.session_state.selected_candidates = [c['name'] for c in candidates[:8]]
            st.rerun()
        
        st.divider()
        
        # Time Range - Date Pickers
        st.markdown("### 📅 Date Range")
        
        # Default: last 14 days
        default_end = datetime.now().date()
        default_start = default_end - pd.Timedelta(days=14)
        
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            help="Beginning of data range"
        )
        
        end_date = st.date_input(
            "End Date", 
            value=default_end,
            help="End of data range"
        )
        
        # Calculate days_back from date range
        days_back = (end_date - start_date).days
        if days_back < 1:
            days_back = 1
            st.warning("End date must be after start date")
        
        st.divider()
        
        # Chart Settings
        st.markdown("### 🎬 Video Settings")
        
        duration = st.slider(
            "Duration (seconds)",
            min_value=8,
            max_value=30,
            value=15,
            help="Length of the output video"
        )
        
        fps = st.selectbox(
            "Frame Rate",
            options=[24, 30, 60],
            index=1,
            help="Higher = smoother but larger file"
        )
        
        st.divider()
        
        # Visual Settings
        st.markdown("### 🎨 Visual")
        
        show_gridlines = st.toggle("Show grid lines", value=True)
        
        custom_title = st.text_input(
            "Custom Title (optional)",
            value="",
            help="Leave empty for auto-generated title"
        )
        
        st.divider()
        
        # Output Settings
        st.markdown("### 💾 Output")
        
        output_filename = st.text_input(
            "Filename",
            value=f"{series_ticker.lower()}_chart",
            help="Output filename (without extension)"
        )
    
    # Main content area - Candidate Selection (Collapsible)
    if not st.session_state.markets_loaded:
        st.markdown("## Select Candidates")
        st.info("👈 Click **Load Candidates** in the sidebar first")
    else:
        candidates = st.session_state.available_markets
        # Filter out empty/invalid selections
        valid_selected = [n for n in st.session_state.selected_candidates if n and n.strip()]
        st.session_state.selected_candidates = valid_selected  # Clean up state
        selected_count = len(valid_selected)
        
        if not candidates:
            st.warning("No candidates found")
        else:
            # Collapsible expander - expanded by default until selections made
            expander_label = f"📋 Select Candidates ({selected_count} of {len(candidates)} selected)"
            with st.expander(expander_label, expanded=(selected_count == 0)):
                # Quick select buttons in a row
                c1, c2, c3, c4 = st.columns(4)
                
                if c1.button("Top 5", key="btn_top5"): 
                    st.session_state.selected_candidates = [c['name'] for c in candidates[:5]]
                    st.rerun()
                if c2.button("Top 8", key="btn_top8"): 
                    st.session_state.selected_candidates = [c['name'] for c in candidates[:8]]
                    st.rerun()
                if c3.button("Top 12", key="btn_top12"): 
                    st.session_state.selected_candidates = [c['name'] for c in candidates[:12]]
                    st.rerun()
                if c4.button("Clear", key="btn_clear"): 
                    st.session_state.selected_candidates = []
                    st.rerun()
                
                st.markdown("---")
                
                # Use a form to batch all checkbox selections
                with st.form(key="candidate_form"):
                    # Two columns of checkboxes
                    col_left, col_right = st.columns(2)
                    
                    half = len(candidates) // 2
                    checkbox_states = {}
                    
                    with col_left:
                        for cand in candidates[:half]:
                            odds_pct = cand['odds'] * 100
                            is_selected = cand['name'] in st.session_state.selected_candidates
                            label = f"{cand['name']} ({odds_pct:.1f}%)"
                            checkbox_states[cand['name']] = st.checkbox(
                                label, value=is_selected, key=f"form_cb_{cand['ticker']}"
                            )
                    
                    with col_right:
                        for cand in candidates[half:]:
                            odds_pct = cand['odds'] * 100
                            is_selected = cand['name'] in st.session_state.selected_candidates
                            label = f"{cand['name']} ({odds_pct:.1f}%)"
                            checkbox_states[cand['name']] = st.checkbox(
                                label, value=is_selected, key=f"form_cb_{cand['ticker']}"
                            )
                    
                    st.markdown("---")
                    
                    # Submit button
                    submitted = st.form_submit_button(
                        "✅ Apply Selection", 
                        use_container_width=True,
                        type="primary"
                    )
                    
                    if submitted:
                        # Update selected candidates based on checkbox states
                        st.session_state.selected_candidates = [
                            name for name, checked in checkbox_states.items() if checked
                        ]
                        st.rerun()
            
            # Show summary outside expander - filter out any empty names
            valid_selected = [n for n in st.session_state.selected_candidates if n and n.strip()]
            actual_count = len(valid_selected)
            if actual_count > 0:
                selected_names = ", ".join(valid_selected[:5])
                if actual_count > 5:
                    selected_names += f" +{actual_count - 5} more"
                st.caption(f"Selected: {selected_names}")
    
    st.divider()
    
    # Preview and Generate section
    can_generate = (
        st.session_state.markets_loaded and 
        len(st.session_state.selected_candidates) >= 2
    )
    
    if not can_generate:
        st.warning("Select at least 2 candidates")
    
    col_preview, col_generate = st.columns(2)
    
    with col_preview:
        if st.button("👁 PREVIEW", use_container_width=True, disabled=not can_generate):
            # Get selected market data
            selected_markets = [
                c['market'] for c in st.session_state.available_markets 
                if c['name'] in st.session_state.selected_candidates
            ]
            generate_preview(
                series_ticker=st.session_state.current_series,
                selected_markets=selected_markets,
                days_back=days_back,
                show_gridlines=show_gridlines,
                custom_title=custom_title
            )
    
    with col_generate:
        if st.button("🚀 GENERATE VIDEO", use_container_width=True, type="primary", disabled=not can_generate):
            # Get selected market data
            selected_markets = [
                c['market'] for c in st.session_state.available_markets 
                if c['name'] in st.session_state.selected_candidates
            ]
            
            generate_chart(
                series_ticker=st.session_state.current_series,
                selected_markets=selected_markets,
                days_back=days_back,
                duration=duration,
                fps=fps,
                show_gridlines=show_gridlines,
                custom_title=custom_title,
                output_filename=output_filename
            )
    
    st.caption(f"Output: ~/Downloads/{output_filename}.mp4")
    
    # Video Player Section
    st.divider()
    st.markdown("## 🎬 Player")
    
    # Check if we have a video to show
    has_video = (
        'last_video_path' in st.session_state and 
        st.session_state.last_video_path and 
        os.path.exists(st.session_state.last_video_path)
    )
    
    # Show preview image if no video yet
    if 'preview_image' in st.session_state and st.session_state.preview_image and not has_video:
        st.image(st.session_state.preview_image, use_container_width=True)
        st.caption("Preview frame - Generate video to see animation")
    
    # Video player with controls
    if has_video:
        video_path = st.session_state.last_video_path
        
        # Video info bar
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("File", Path(video_path).name)
        col_info2.metric("Size", f"{file_size:.1f} MB")
        col_info3.metric("Location", "~/Downloads")
        
        # Main video player - read as bytes for reliable playback
        try:
            with open(video_path, 'rb') as video_file:
                video_bytes = video_file.read()
            st.video(video_bytes, format='video/mp4')
        except Exception as e:
            st.error(f"Could not load video: {e}")
            st.info(f"Video saved at: {video_path}")
        
        # Playback tip
        st.caption("💡 Use video controls: ▶️ Play/Pause | Drag timeline to seek | 🔊 Volume | ⛶ Fullscreen")
        
        # Quick actions
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📂 Open in Finder", use_container_width=True, key="btn_finder"):
                os.system(f'open -R "{video_path}"')
        
        with action_col2:
            if st.button("▶️ Open in Player", use_container_width=True, key="btn_player"):
                os.system(f'open "{video_path}"')
        
        with action_col3:
            if st.button("🗑️ Clear Player", use_container_width=True, key="btn_clear_player"):
                st.session_state.last_video_path = None
                st.session_state.preview_image = None
                st.rerun()
    elif not ('preview_image' in st.session_state and st.session_state.preview_image):
        st.info("Generate a preview or video to see it here")
    
    # Show recent files
    st.divider()
    show_recent_charts()


def generate_preview(series_ticker, selected_markets, days_back, show_gridlines, custom_title):
    """Generate a preview image of the chart."""
    with st.spinner("Generating preview..."):
        try:
            client = KalshiClient()
            
            df = client.get_multi_market_history(
                selected_markets,
                series_ticker,
                days_back=days_back,
                max_markets=len(selected_markets)
            )
            
            if df.empty:
                st.error("No data available")
                return
            
            # Generate title
            if custom_title:
                title = custom_title.upper()
            else:
                from config import get_default_title
                title = get_default_title(series_ticker)
            
            # Generate preview
            preview_bytes = create_preview_image(
                df=df,
                title=title,
                max_candidates=len(selected_markets),
                show_gridlines=show_gridlines,
                frame_position=0.8  # Show near end of timeline
            )
            
            st.session_state.preview_image = preview_bytes
            st.session_state.preview_df = df
            st.session_state.preview_title = title
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")


def generate_chart(series_ticker, selected_markets, days_back, duration, fps,
                   show_gridlines, custom_title, output_filename):
    """Generate the chart with progress indicators."""
    
    # Output path
    output_path = DOWNLOADS_FOLDER / f"{output_filename}.mp4"
    
    # Progress container
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0, text="Initializing...")
        status_text = st.empty()
        
        try:
            # Check if we have cached data from preview
            if 'preview_df' in st.session_state and st.session_state.preview_df is not None:
                df = st.session_state.preview_df
                title = st.session_state.preview_title
                progress_bar.progress(40, text="Using cached data...")
            else:
                # Step 1: Initialize client
                status_text.text("🔌 Connecting to Kalshi API...")
                progress_bar.progress(10, text="Connecting to API...")
                client = KalshiClient()
                
                # Step 2: Fetch historical data for selected markets
                status_text.text("📈 Fetching historical data...")
                progress_bar.progress(30, text="Fetching historical data...")
                
                df = client.get_multi_market_history(
                    selected_markets,
                    series_ticker,
                    days_back=days_back,
                    max_markets=len(selected_markets)
                )
                
                if df.empty:
                    st.error("❌ No historical data available")
                    return
                
                # Generate title
                if custom_title:
                    title = custom_title.upper()
                else:
                    from config import get_default_title
                    title = get_default_title(series_ticker)
            
            # Step 3: Generate chart
            status_text.text("🎬 Generating animation...")
            progress_bar.progress(50, text="Generating animation...")
            
            result_path = create_multi_market_chart(
                df=df,
                title=title,
                output=str(output_path),
                fps=fps,
                duration=float(duration),
                format='square',
                max_candidates=len(selected_markets),
                show_gridlines=show_gridlines
            )
            
            progress_bar.progress(100, text="Complete!")
            status_text.text("")
            
            # Store video path for player
            st.session_state.last_video_path = result_path
            
            # Success message
            st.success(f"✅ Saved to Downloads!")
            
            # Show file info
            file_size = os.path.getsize(result_path) / (1024 * 1024)  # MB
            st.caption(f"{duration}s • {file_size:.1f} MB • {len(selected_markets)} candidates")
            
            st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            raise e


def show_recent_charts():
    """Show recently generated charts."""
    st.markdown("## 📁 Recent Charts")
    
    # Find MP4 files in Downloads
    mp4_files = list(DOWNLOADS_FOLDER.glob("*chart*.mp4"))
    mp4_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    mp4_files = mp4_files[:5]  # Show last 5
    
    if not mp4_files:
        st.info("No charts generated yet. Create your first one above!")
        return
    
    for file in mp4_files:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.text(file.name)
        
        with col2:
            file_size = file.stat().st_size / (1024 * 1024)
            st.text(f"{file_size:.1f} MB")
        
        with col3:
            if st.button("Open", key=f"open_{file.name}"):
                os.system(f'open "{file}"')


if __name__ == "__main__":
    main()
