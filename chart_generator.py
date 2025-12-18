"""
Bar race chart generator for Kalshi market data.
Novig branded animated charts - clean, professional style.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle, FancyBboxPatch
from PIL import Image
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import io
import subprocess
import tempfile

from config import CHART_CONFIG, VIDEO_CONFIG, DHARMA_FONT_PATH, LOGO_SVG_PATH


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values."""
    return a + (b - a) * t


def load_font() -> FontProperties:
    """Load Dharma Gothic font."""
    if DHARMA_FONT_PATH.exists():
        return FontProperties(fname=str(DHARMA_FONT_PATH))
    return FontProperties(family='sans-serif', weight='bold')


def load_logo(target_height: int = 108) -> Optional[np.ndarray]:
    """Load Novig logo from SVG at HIGH RESOLUTION for crisp display."""
    if LOGO_SVG_PATH.exists():
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Render at 4x target size for maximum quality, then scale down
            render_height = target_height * 4
            
            try:
                result = subprocess.run(
                    ['rsvg-convert', 
                     f'--height={render_height}',
                     '--background-color=transparent',
                     str(LOGO_SVG_PATH), 
                     '-o', tmp_path],
                    capture_output=True, check=True
                )
                img = Image.open(tmp_path).convert('RGBA')
                Path(tmp_path).unlink()  # Clean up
                
                # Scale down to target size using high-quality LANCZOS resampling
                aspect = img.width / img.height
                target_width = int(target_height * aspect)
                img = img.resize((target_width, target_height), Image.LANCZOS)
                
                img_array = np.array(img)
                
                # Force pure white RGB, threshold alpha for crisp edges
                alpha = img_array[:, :, 3]
                # Use a higher threshold to get sharper edges
                mask = alpha > 100
                
                # Pure white RGB
                img_array[:, :, 0] = 255
                img_array[:, :, 1] = 255
                img_array[:, :, 2] = 255
                
                # Binary alpha - fully opaque or fully transparent
                img_array[:, :, 3] = np.where(mask, 255, 0)
                
                return img_array
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            print("SVG converter not available, using fallback logo")
            return _create_fallback_logo()
            
        except Exception as e:
            print(f"Error loading SVG logo: {e}")
            return _create_fallback_logo()
    return None


def _create_fallback_logo() -> np.ndarray:
    """Create a simple white Novig N logo as fallback."""
    # Create a 300x300 transparent image with white N
    size = 300
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Draw a simple stylized N using PIL
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw a simple N shape in white
    margin = 30
    width = 60
    
    # Left vertical bar
    draw.rectangle([margin, margin, margin + width, size - margin], fill=(255, 255, 255, 255))
    # Right vertical bar  
    draw.rectangle([size - margin - width, margin, size - margin, size - margin], fill=(255, 255, 255, 255))
    # Diagonal
    points = [
        (margin, margin),
        (margin + width, margin),
        (size - margin, size - margin),
        (size - margin - width, size - margin)
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    return np.array(img)


def interpolate_dataframe(df: pd.DataFrame, n_frames: int) -> Tuple[List[Dict], List]:
    """Create smooth frame interpolation from DataFrame."""
    if df.empty or len(df) < 2:
        return [], []

    candidates = [col for col in df.columns if col != 'timestamp']
    n_rows = len(df)
    frame_indices = np.linspace(0, n_rows - 1, n_frames)

    frames, timestamps = [], []

    for idx in frame_indices:
        lower_idx = int(np.floor(idx))
        upper_idx = min(int(np.ceil(idx)), n_rows - 1)
        t = idx - lower_idx

        frame_data = {}
        for candidate in candidates:
            lv = df.iloc[lower_idx][candidate]
            uv = df.iloc[upper_idx][candidate]
            lv = 0 if pd.isna(lv) else float(lv)
            uv = 0 if pd.isna(uv) else float(uv)
            frame_data[candidate] = lerp(lv, uv, t)

        lower_ts = df.iloc[lower_idx]['timestamp']
        upper_ts = df.iloc[upper_idx]['timestamp']
        ts = lower_ts if lower_idx == upper_idx else lower_ts + (upper_ts - lower_ts) * t

        frames.append(frame_data)
        timestamps.append(ts)

    return frames, timestamps


# Clean Novig color palette
COLORS = {
    'background': '#0a1929',
    'bar_color': '#5ac8fa',
    'text_white': '#ffffff',
    'text_cyan': '#5ac8fa',
    'text_gray': '#6b8299',
    'gridline': '#1a3a5c',
}


class BarRaceAnimator:
    """Animated bar race chart generator - clean Novig style."""
    
    def __init__(
        self,
        df: pd.DataFrame,
        title: str,
        max_candidates: int = 8,
        fps: int = 30,
        duration: float = 8.0,
        format: str = 'square',
        show_gridlines: bool = True
    ):
        self.df = df
        self.title = title.upper()
        self.fps = fps
        self.duration = duration
        self.n_frames = int(fps * duration)
        self.show_gridlines = show_gridlines

        config = CHART_CONFIG.get(format, CHART_CONFIG['square'])
        self.width = config['width']
        self.height = config['height']
        self.dpi = config['dpi']

        self.candidates = [col for col in df.columns if col != 'timestamp'][:max_candidates]
        self.frames, self.timestamps = interpolate_dataframe(df, self.n_frames)
        self.prev_positions = {c: i for i, c in enumerate(self.candidates)}

        self.font_prop = load_font()
        # Load logo at higher resolution for crisp rendering
        # Use 12% of chart height for good visibility
        logo_target_height = int(self.height * 0.12)
        self.logo = load_logo(target_height=logo_target_height)

    def _get_sorted_candidates(self, frame_data: Dict[str, float]) -> List[Tuple[str, float]]:
        """Sort candidates by value (descending)."""
        items = [(c, frame_data.get(c, 0)) for c in self.candidates]
        return sorted(items, key=lambda x: x[1], reverse=True)

    def _create_frame(self, frame_idx: int, ax: plt.Axes, fig: plt.Figure):
        """Render a single frame - clean Novig style."""
        ax.clear()

        # Solid background
        fig.patch.set_facecolor(COLORS['background'])
        ax.set_facecolor(COLORS['background'])
        
        for spine in ax.spines.values():
            spine.set_visible(False)

        if not self.frames:
            return

        frame_data = self.frames[frame_idx]
        timestamp = self.timestamps[frame_idx]

        sorted_candidates = self._get_sorted_candidates(frame_data)
        target_positions = {c: i for i, (c, _) in enumerate(sorted_candidates)}

        # Smooth position transitions
        current_positions = {}
        for candidate in self.candidates:
            prev_pos = self.prev_positions.get(candidate, target_positions.get(candidate, 0))
            target_pos = target_positions.get(candidate, 0)
            current_positions[candidate] = lerp(prev_pos, target_pos, 0.15)
        self.prev_positions = current_positions.copy()

        n_bars = len(self.candidates)

        # Layout - clean spacing with better name alignment
        name_end_x = 0.26  # Right edge for name text (right-aligned)
        bar_start_x = 0.28
        bar_end_x = 0.82
        pct_x = 0.84
        
        chart_top = 0.80
        chart_bottom = 0.15
        chart_height = chart_top - chart_bottom
        bar_height = min(0.06, chart_height / n_bars * 0.8)
        bar_spacing = chart_height / max(n_bars, 1)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])

        # Title - CENTERED, BOLD
        ax.text(0.5, 0.92, self.title,
               ha='center', va='center',
               color=COLORS['text_white'],
               fontsize=32, fontweight='bold',
               fontproperties=self.font_prop,
               transform=ax.transAxes, zorder=10)

        # Calculate max value for scaling
        all_values = [v for v in frame_data.values() if v > 0]
        max_val = max(all_values) if all_values else 0.1
        
        # Add some headroom
        max_val = max_val * 1.1

        # Smart gridline spacing
        if max_val <= 0.1:
            grid_step = 0.02
        elif max_val <= 0.25:
            grid_step = 0.05
        elif max_val <= 0.5:
            grid_step = 0.1
        else:
            grid_step = 0.2

        # Draw gridlines
        if self.show_gridlines:
            grid_val = grid_step
            while grid_val <= max_val:
                x_pos = bar_start_x + (grid_val / max_val) * (bar_end_x - bar_start_x)
                if x_pos <= bar_end_x:
                    ax.axvline(x=x_pos, ymin=chart_bottom, ymax=chart_top,
                              color=COLORS['gridline'], linewidth=1, alpha=0.5, zorder=0)
                    label = f"{int(grid_val * 100)}%"
                    ax.text(x_pos, chart_top + 0.02, label,
                           ha='center', va='bottom',
                           color=COLORS['text_gray'],
                           fontsize=11, fontproperties=self.font_prop,
                           transform=ax.transAxes, zorder=10)
                grid_val += grid_step

        # Draw bars
        for candidate in self.candidates:
            value = frame_data.get(candidate, 0)
            pos = current_positions.get(candidate, 0)
            y_center = chart_top - (pos + 0.5) * bar_spacing
            
            # Bar width
            if max_val > 0 and value > 0:
                bar_width = (value / max_val) * (bar_end_x - bar_start_x)
            else:
                bar_width = 0.01  # Minimum visibility

            # Draw bar
            bar = FancyBboxPatch(
                (bar_start_x, y_center - bar_height/2),
                max(bar_width, 0.01), bar_height,
                boxstyle="round,pad=0,rounding_size=0.008",
                facecolor=COLORS['bar_color'],
                edgecolor='none',
                transform=ax.transAxes,
                zorder=3
            )
            ax.add_patch(bar)

            # Highlight on bar
            if bar_width > 0.02:
                highlight = Rectangle(
                    (bar_start_x, y_center + bar_height * 0.25),
                    bar_width, bar_height * 0.15,
                    facecolor='#ffffff',
                    edgecolor='none',
                    alpha=0.2,
                    transform=ax.transAxes,
                    zorder=4
                )
                ax.add_patch(highlight)

            # Candidate name - BOLD, centered vertically
            name = candidate.upper()[:20]
            ax.text(name_end_x, y_center, name,
                   ha='right', va='center',
                   color=COLORS['text_white'],
                   fontsize=16, fontweight='bold',
                   fontproperties=self.font_prop,
                   transform=ax.transAxes, zorder=5)

            # Percentage - cyan, BOLD, positioned right after the bar
            pct_str = f"{value * 100:.1f}%"
            pct_x_pos = bar_start_x + bar_width + 0.02  # Right after bar with small padding
            ax.text(pct_x_pos, y_center, pct_str,
                   ha='left', va='center',
                   color=COLORS['text_cyan'],
                   fontsize=14, fontweight='bold',
                   fontproperties=self.font_prop,
                   transform=ax.transAxes, zorder=5)

        # Timestamp - BIGGER, BOLD, centered at bottom
        if isinstance(timestamp, pd.Timestamp):
            ts_str = timestamp.strftime("%B %d, %Y").upper()
        else:
            ts_str = str(timestamp).upper()

        ax.text(0.5, 0.04, ts_str,
               ha='center', va='center',
               color=COLORS['text_gray'],
               fontsize=16, fontweight='bold',
               fontproperties=self.font_prop,
               transform=ax.transAxes, zorder=10)

        # Attribution text - bottom center below date
        ax.text(0.5, 0.015, "PER NOVIG MARKET DATA",
               ha='center', va='center',
               color=COLORS['text_gray'],
               fontsize=10, fontweight='normal',
               fontproperties=self.font_prop,
               alpha=0.7,
               transform=ax.transAxes, zorder=10)

        # Novig logo - bottom left corner, CRISP with no blur
        if self.logo is not None:
            # Use nearest-neighbor interpolation to keep edges sharp
            logo_img = OffsetImage(self.logo, zoom=1.0, interpolation='nearest')
            # Position with proper padding from edges
            ab = AnnotationBbox(
                logo_img, (0.04, 0.04),
                xycoords='axes fraction',
                frameon=False,
                box_alignment=(0, 0),  # Anchor from bottom-left
                zorder=10
            )
            ax.add_artist(ab)

    def render_preview_frame(self, frame_idx: int = None) -> bytes:
        """Render a single frame and return as PNG bytes for preview."""
        if frame_idx is None:
            frame_idx = min(len(self.frames) - 1, len(self.frames) * 4 // 5)
        
        if not self.frames:
            # Return a placeholder if no frames
            fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
            fig.patch.set_facecolor(COLORS['background'])
            ax.set_facecolor(COLORS['background'])
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', 
                   color='white', fontsize=20)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            buf = io.BytesIO()
            fig.savefig(buf, format='png', facecolor=fig.get_facecolor(), 
                       edgecolor='none', bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            buf.seek(0)
            return buf.getvalue()
        
        fig, ax = plt.subplots(
            figsize=(self.width / self.dpi, self.height / self.dpi),
            dpi=self.dpi
        )
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        self._create_frame(frame_idx, ax, fig)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor=fig.get_facecolor(), 
                   edgecolor='none', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def animate(self, output_path: str) -> str:
        """Generate and save animation to file."""
        fig, ax = plt.subplots(
            figsize=(self.width / self.dpi, self.height / self.dpi),
            dpi=self.dpi
        )
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        def update(frame_idx):
            self._create_frame(frame_idx, ax, fig)
            return []

        anim = animation.FuncAnimation(
            fig, update, frames=self.n_frames,
            interval=1000 / self.fps, blit=False
        )

        output_path = Path(output_path)
        writer = animation.FFMpegWriter(
            fps=self.fps,
            codec=VIDEO_CONFIG['codec'],
            bitrate=VIDEO_CONFIG['bitrate'],
            extra_args=['-pix_fmt', VIDEO_CONFIG['pix_fmt']]
        )

        anim.save(str(output_path), writer=writer)
        plt.close(fig)
        return str(output_path)


def create_preview_image(
    df: pd.DataFrame,
    title: str,
    max_candidates: int = 8,
    show_gridlines: bool = True,
    frame_position: float = 0.8
) -> bytes:
    """Create a static preview image."""
    animator = BarRaceAnimator(
        df=df,
        title=title,
        max_candidates=max_candidates,
        fps=30,
        duration=8.0,
        format='square',
        show_gridlines=show_gridlines
    )
    frame_idx = int(len(animator.frames) * frame_position) if animator.frames else 0
    return animator.render_preview_frame(frame_idx)


def create_multi_market_chart(
    df: pd.DataFrame,
    title: str,
    output: str,
    fps: int = 30,
    duration: float = 8.0,
    format: str = 'square',
    max_candidates: int = 8,
    show_gridlines: bool = True
) -> str:
    """Create animated bar race chart from market data."""
    animator = BarRaceAnimator(
        df=df,
        title=title,
        max_candidates=max_candidates,
        fps=fps,
        duration=duration,
        format=format,
        show_gridlines=show_gridlines
    )
    return animator.animate(output)
