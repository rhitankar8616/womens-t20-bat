import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.tables import render_stats_table
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand, get_matches_for_batter_and_filters
from utils.calculations import (
    calculate_progression_data,
    calculate_stats_by_group,
    calculate_basic_stats
)

def render_batter_info(selected_batter, batter_hand, filtered_df):
    """Render batter info box with raw stats"""
    stats = calculate_basic_stats(filtered_df)
    
    avg_display = f"{stats['average']:.2f}" if stats['average'] is not None else "-"
    
    st.markdown(f"""
        <div class="batter-info">
            <h2>{selected_batter}</h2>
            <p>Batting Style: <strong>{"Right-Handed" if batter_hand == "Right" else "Left-Handed"}</strong></p>
            <div class="stats-row">
                <div class="stat-item">
                    <span class="stat-label">Runs</span>
                    <span class="stat-value">{stats['runs']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Balls</span>
                    <span class="stat-value">{stats['balls']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average</span>
                    <span class="stat-value">{avg_display}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Strike Rate</span>
                    <span class="stat-value">{stats['sr']:.2f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Boundary %</span>
                    <span class="stat-value">{stats['boundary_pct']:.2f}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Dot Ball %</span>
                    <span class="stat-value">{stats['dot_pct']:.2f}%</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_progression_plot(data, y_column, title, y_label, color="#4ade80"):
    """Create a line plot for progression data"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Ball'],
        y=data[y_column],
        mode='lines+markers',
        name=y_label,
        line=dict(color=color, width=2),
        marker=dict(size=6),
        hovertemplate=f"Ball %{{x}}<br>{y_label}: %{{y:.2f}}<extra></extra>"
    ))
    
    # Update layout with simpler syntax for plotly compatibility
    fig.update_layout(
        title_text=title,
        title_font_color="white",
        title_font_size=14,
        title_x=0.5,
        xaxis_title="Rolling window for Balls faced",
        xaxis_title_font_color="white",
        xaxis_tickfont_color="white",
        xaxis_gridcolor='rgba(255,255,255,0.1)',
        xaxis_showgrid=True,
        yaxis_title=y_label,
        yaxis_title_font_color="white",
        yaxis_tickfont_color="white",
        yaxis_gridcolor='rgba(255,255,255,0.1)',
        yaxis_showgrid=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=50, b=50),
        height=300,
        showlegend=False
    )
    
    return fig

def render_innings_progression_page(df):
    """Render the Innings Progression analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="innings_progression", key_prefix="ip")
    
    # Main content
    if not selected_batter:
        st.info("Please select a batter from the sidebar to view analysis.")
        render_footer()
        return
    
    # Apply filters (without overs for this page)
    filtered_df = apply_filters(df, selected_batter, filters)
    
    if filtered_df is None or len(filtered_df) == 0:
        st.warning("No data available for the selected batter and filters.")
        render_footer()
        return
    
    # Get match IDs for average metrics calculation
    match_ids = get_matches_for_batter_and_filters(df, selected_batter, filters)
    
    # Get batter hand for display
    batter_hand = get_batter_hand(df, selected_batter)
    
    # Display batter info with raw stats
    render_batter_info(selected_batter, batter_hand, filtered_df)
    
    # Get rolling window from filters
    rolling_min, rolling_max = filters.get('rolling_window', (0, 20))
    
    # Section 1: Progression Plots
    st.markdown("## Innings Progression Plots")
    st.markdown("""
        <div class="info-note">
            <em>Adjust the rolling window (for balls faced) on the left sidepanel to view a batter's general progression in an innings.</em>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate progression data
    progression_df = calculate_progression_data(filtered_df, selected_batter, filters, rolling_min, rolling_max)
    
    if progression_df is not None and len(progression_df) > 0:
        # Create 2x2 grid of plots
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sr = create_progression_plot(
                progression_df, 'SR', 
                'Strike Rate per Rolling Window', 
                'Strike Rate Progression',
                color="#4ade80"
            )
            st.plotly_chart(fig_sr, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            fig_boundary = create_progression_plot(
                progression_df, 'Boundary %', 
                'Boundary % per Rolling Window', 
                'Boundary % Progression',
                color="#60a5fa"
            )
            st.plotly_chart(fig_boundary, use_container_width=True, config={'displayModeBar': False})
        
        col3, col4 = st.columns(2)
        
        with col3:
            fig_dot = create_progression_plot(
                progression_df, 'Dot %', 
                'Dot Balls % per Rolling Window', 
                'Dot Balls % Progression',
                color="#f87171"
            )
            st.plotly_chart(fig_dot, use_container_width=True, config={'displayModeBar': False})
        
        with col4:
            fig_aerial = create_progression_plot(
                progression_df, 'Aerial %', 
                'Aerial Shots % per Rolling Window', 
                'Aerial Shots % Progression',
                color="#fbbf24"
            )
            st.plotly_chart(fig_aerial, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No progression data available for the selected rolling window.")
    
    st.markdown("---")
    
    # Section 2: Over-by-over progression table
    all_matches_df = df[df['fixtureId'].isin(match_ids)]
    over_stats = calculate_stats_by_group(filtered_df, all_matches_df, match_ids, 'over')
    
    if len(over_stats) > 0:
        over_stats = over_stats.rename(columns={'over': 'Over'})
        over_stats = over_stats.sort_values('Over')
        render_stats_table(over_stats, "Over-by-over Progression in an Innings", has_effective_metrics=True)
    
    st.markdown("---")
    
    # Section 3: Ball-by-ball progression in an over
    ball_stats = calculate_stats_by_group(filtered_df, all_matches_df, match_ids, 'ball')
    
    if len(ball_stats) > 0:
        ball_stats = ball_stats.rename(columns={'ball': 'Ball'})
        ball_stats = ball_stats[ball_stats['Ball'].isin([1, 2, 3, 4, 5, 6])]
        ball_stats = ball_stats.sort_values('Ball')
        render_stats_table(ball_stats, "Ball-by-ball Progression in an Over", has_effective_metrics=True)
    
    # Footer
    render_footer()
    