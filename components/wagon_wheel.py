import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Wedge
import math

def get_adjusted_angle(shot_angle, is_rhb):
    """
    Adjust shot angle for matplotlib polar plot based on batter handedness.
    Used for Boundaries and Caught Out wheels.
    
    Uses same formula for both RHB and LHB since shot_angle represents
    absolute field direction.
    """
    if shot_angle is None or pd.isna(shot_angle):
        return None
    
    matplotlib_angle = (90 - shot_angle) % 360
    return matplotlib_angle


def get_scoring_area_display_angle(shot_angle, is_rhb):
    """
    Get display angle specifically for Scoring Areas wheel.
    
    For LHB, we need to shift the display position by 90° (2 sectors) 
    anti-clockwise to correctly align the sector stats with field positions.
    """
    if shot_angle is None or pd.isna(shot_angle):
        return None
    
    base_angle = (90 - shot_angle) % 360
    
    if not is_rhb:
        # For LHB, shift 90° anti-clockwise (add 90° to matplotlib angle)
        base_angle = (base_angle + 90) % 360
    
    return base_angle


def render_boundaries_wheel(df, is_rhb):
    """
    Render the Boundaries wagon wheel.
    Shows 4s and 6s as lines from center to boundary.
    """
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    # Filter for boundaries
    fours_df = df[df['runs_scored'] == 4].copy()
    sixes_df = df[df['runs_scored'] == 6].copy()
    
    # Draw the boundary circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(theta, [1]*100, 'k-', linewidth=2)
    ax.fill(theta, [1]*100, color='#e8f5e9', alpha=0.3)
    
    # Draw 4s (blue lines)
    for _, row in fours_df.iterrows():
        if pd.notna(row.get('shot_angle')):
            angle_deg = get_adjusted_angle(row['shot_angle'], is_rhb)
            if angle_deg is not None:
                angle_rad = np.deg2rad(angle_deg)
                ax.plot([angle_rad, angle_rad], [0, 1], color='#2196F3', linewidth=1.5, alpha=0.7)
    
    # Draw 6s (red lines)
    for _, row in sixes_df.iterrows():
        if pd.notna(row.get('shot_angle')):
            angle_deg = get_adjusted_angle(row['shot_angle'], is_rhb)
            if angle_deg is not None:
                angle_rad = np.deg2rad(angle_deg)
                ax.plot([angle_rad, angle_rad], [0, 1], color='#f44336', linewidth=2, alpha=0.8)
    
    # Clean up the plot
    ax.set_ylim(0, 1.1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)
    ax.set_facecolor('white')
    
    # Add legend
    four_patch = mpatches.Patch(color='#2196F3', label=f'4s ({len(fours_df)})')
    six_patch = mpatches.Patch(color='#f44336', label=f'6s ({len(sixes_df)})')
    ax.legend(handles=[four_patch, six_patch], loc='upper right', bbox_to_anchor=(1.15, 1.1), fontsize=9)
    
    plt.tight_layout()
    return fig


def render_caught_out_wheel(df, is_rhb):
    """
    Render the Caught Out dismissals wagon wheel.
    Shows caught dismissals with distance (shot_magnitude) and direction (shot_angle).
    """
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    # Filter for caught out dismissals
    caught_df = df[df['dismissalType'].isin(['Caught', 'CaughtSub', 'Caught Out'])].copy()
    
    # Draw the boundary circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(theta, [1]*100, 'k-', linewidth=2)
    ax.fill(theta, [1]*100, color='#ffebee', alpha=0.3)
    
    # Normalize shot_magnitude: 167+ maps to boundary (1.0)
    max_magnitude = 167
    
    # Draw caught out lines
    for _, row in caught_df.iterrows():
        if pd.notna(row.get('shot_angle')) and pd.notna(row.get('shot_magnitude')):
            angle_deg = get_adjusted_angle(row['shot_angle'], is_rhb)
            if angle_deg is not None:
                angle_rad = np.deg2rad(angle_deg)
                
                # Normalize magnitude
                magnitude = row['shot_magnitude']
                if magnitude >= max_magnitude:
                    normalized_mag = 1.0
                else:
                    normalized_mag = magnitude / max_magnitude
                
                ax.plot([angle_rad, angle_rad], [0, normalized_mag], color='#d32f2f', linewidth=1.5, alpha=0.7)
    
    # Clean up the plot
    ax.set_ylim(0, 1.1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)
    ax.set_facecolor('white')
    
    # Add count label
    ax.set_title(f'Total: {len(caught_df)} dismissals', fontsize=10, pad=10)
    
    plt.tight_layout()
    return fig


def render_scoring_areas_wheel(df, is_rhb):
    """
    Render the Scoring Areas wagon wheel.
    Divides the ground into 8 equal sectors and shows stats in each.
    Each sector is 45 degrees, divided at 0, 45, 90, 135, 180, 225, 270, 315.
    
    For LHB, display positions are shifted 90° to correctly align with field positions.
    """
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    
    # Draw boundary circle
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(theta, [1]*100, 'k-', linewidth=2)
    ax.fill(theta, [1]*100, color='#e3f2fd', alpha=0.2)
    
    # Define 8 sectors (each 45 degrees in cricket angles)
    # Sectors divided at 0, 45, 90, 135, 180, 225, 270, 315 as per PDF
    sector_ranges = [
        (0, 45),
        (45, 90),
        (90, 135),
        (135, 180),
        (180, 225),
        (225, 270),
        (270, 315),
        (315, 360),
    ]
    
    # Calculate total runs for % of runs calculation
    total_runs_all = df['runs_scored'].sum() if 'runs_scored' in df.columns else 0
    
    # Process each sector
    for i, (start_angle, end_angle) in enumerate(sector_ranges):
        # Filter balls in this sector
        if end_angle == 360:
            # Last sector: >= 315 and <= 360
            sector_df = df[
                (df['shot_angle'] >= start_angle) & (df['shot_angle'] <= 360)
            ].copy()
        else:
            sector_df = df[
                (df['shot_angle'] >= start_angle) & (df['shot_angle'] < end_angle)
            ].copy()
        
        # Calculate stats
        balls = len(sector_df)
        runs = int(sector_df['runs_scored'].sum()) if balls > 0 else 0
        
        # Calculate outs
        outs = 0
        if balls > 0:
            if 'is_out' in sector_df.columns:
                outs = int(sector_df['is_out'].sum())
            elif 'dismissalType' in sector_df.columns:
                outs = int(sector_df['dismissalType'].notna().sum() - (sector_df['dismissalType'] == '').sum())
        
        average = runs / outs if outs > 0 else None
        sr = (runs / balls * 100) if balls > 0 else 0
        pct_runs = (runs / total_runs_all * 100) if total_runs_all > 0 else 0
        
        # Calculate sector center angle in cricket coordinates
        mid_angle = (start_angle + end_angle) / 2
        
        # Draw sector boundaries using the scoring area display function
        for angle in [start_angle, end_angle]:
            # Handle 360 as 0
            draw_angle = angle if angle < 360 else 0
            adj_angle = get_scoring_area_display_angle(draw_angle, is_rhb)
            if adj_angle is not None:
                angle_rad = np.deg2rad(adj_angle)
                ax.plot([angle_rad, angle_rad], [0, 1], color='#666', linewidth=1, alpha=0.8)
        
        # Calculate text position (middle of sector) using scoring area display function
        adj_mid_angle = get_scoring_area_display_angle(mid_angle, is_rhb)
        if adj_mid_angle is not None:
            text_angle_rad = np.deg2rad(adj_mid_angle)
            text_r = 0.55  # Position text at 55% of radius
            
            # Format stats text
            avg_str = f"{average:.2f}" if average is not None else "-"
            sr_str = f"{sr:.2f}"
            pct_str = f"{pct_runs:.1f}"
            
            # Multi-line text for sector stats
            stats_text = f"{balls} balls\n{runs} runs\nAvg {avg_str}\nSR {sr_str}\n{pct_str}% of runs"
            
            # Add text with font size 10
            ax.annotate(
                stats_text,
                xy=(text_angle_rad, text_r),
                ha='center',
                va='center',
                fontsize=10,
                fontweight='normal',
                color='#333',
                linespacing=1.2
            )
    
    # Clean up the plot
    ax.set_ylim(0, 1.15)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)
    ax.set_facecolor('white')
    
    plt.tight_layout()
    return fig


def render_wagon_wheels_section(df, is_rhb):
    """
    Render all three wagon wheels in the specified layout.
    First two horizontally, third one below and larger.
    """
    if df is None or len(df) == 0:
        st.warning("No data available for wagon wheel visualization.")
        return
    
    # Ensure required columns exist and have valid data
    if 'shot_angle' not in df.columns:
        st.warning("Shot angle data not available for wagon wheel visualization.")
        return
    
    # Filter out rows with missing shot_angle
    valid_df = df[df['shot_angle'].notna()].copy()
    
    if len(valid_df) == 0:
        st.warning("No valid shot angle data for visualization.")
        return
    
    # First row: Boundaries and Caught Out wheels side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Boundaries")
        boundaries_fig = render_boundaries_wheel(valid_df, is_rhb)
        st.pyplot(boundaries_fig)
        plt.close(boundaries_fig)
    
    with col2:
        st.markdown("#### Caught Out Dismissals")
        caught_fig = render_caught_out_wheel(valid_df, is_rhb)
        st.pyplot(caught_fig)
        plt.close(caught_fig)
    
    # Second row: Scoring Areas wheel (larger, centered)
    st.markdown("---")
    st.markdown("#### Scoring Areas")
    
    # Center the larger wheel
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        scoring_fig = render_scoring_areas_wheel(valid_df, is_rhb)
        st.pyplot(scoring_fig)
        plt.close(scoring_fig)