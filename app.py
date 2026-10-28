"""
Addis Ababa Road Traffic Safety Intelligence Dashboard
Interactive Data Science Portfolio Web Application
Author: YonInsights (yo2120018@gmail.com)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Addis Ababa Road Safety Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive polish
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #1b3a4b;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        text-transform: uppercase;
        color: #586069;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .metric-container {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .insight-card {
        background-color: #f8f9fa;
        border-left: 4px solid #006494;
        padding: 14px 18px;
        border-radius: 4px;
        margin: 12px 0 20px 0;
        font-size: 14px;
        line-height: 1.5;
    }
    .badge-pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. DATA LOADING & CACHING
# ---------------------------------------------------------
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "Data" / "Addis_Ababa_city_RTA.csv",
        base_dir / "data" / "Addis_Ababa_city_RTA.csv",
        Path("Data/Addis_Ababa_city_RTA.csv"),
        Path("data/Addis_Ababa_city_RTA.csv"),
        Path("../Data/Addis_Ababa_city_RTA.csv"),
        Path("../data/Addis_Ababa_city_RTA.csv")
    ]
    
    found_path = None
    for candidate in candidates:
        if candidate.exists():
            found_path = candidate
            break
            
    if not found_path:
        raise FileNotFoundError(f"Could not locate Addis_Ababa_city_RTA.csv in any of: {[str(c) for c in candidates]}")
    
    df = pd.read_csv(found_path)
    # Parse hour of day
    df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
    
    # Severe/Fatal Flag for analytical convenience
    df['Is_Severe_or_Fatal'] = df['Accident_severity'].isin(['Serious Injury', 'Fatal injury'])
    return df

df_raw = load_data()


# ---------------------------------------------------------
# 3. SIDEBAR CONTROLS & DYNAMIC FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/traffic-light.png", width=64)
    st.title("Navigation & Filters")
    st.caption("Addis Ababa RTA Analysis | ALX Portfolio")
    st.divider()

    # 1. Severity Filter
    severity_options = ['Slight Injury', 'Serious Injury', 'Fatal injury']
    selected_severity = st.multiselect(
        "Accident Severity Level",
        options=severity_options,
        default=severity_options,
        help="Filter by police-recorded injury severity outcome."
    )

    # 2. Day of Week Filter
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    selected_days = st.multiselect(
        "Day of Week",
        options=days_order,
        default=days_order
    )

    # 3. Hour of Day Range Slider
    selected_hours = st.slider(
        "Hour of Day (24-Hour Clock)",
        min_value=0,
        max_value=23,
        value=(0, 23),
        help="Filter collisions by time of occurrence."
    )

    # 4. Light Conditions Filter
    light_options = list(df_raw['Light_conditions'].dropna().unique())
    selected_light = st.multiselect(
        "Lighting Conditions",
        options=light_options,
        default=light_options
    )

    # 5. Vehicle Type Filter
    top_vehicles = list(df_raw['Type_of_vehicle'].value_counts().head(8).index)
    selected_vehicles = st.multiselect(
        "Primary Vehicle Type (Top 8)",
        options=top_vehicles,
        default=top_vehicles
    )

    st.divider()
    st.caption("Developed by **YonInsights**")
    st.caption("GitHub: [YonInsights/Addis-Ababa-Road-Safety](https://github.com/YonInsights/Addis-Ababa-Road-Safety-Analysis)")


# ---------------------------------------------------------
# 4. DYNAMIC FILTER APPLICATION
# ---------------------------------------------------------
filtered_df = df_raw[
    (df_raw['Accident_severity'].isin(selected_severity)) &
    (df_raw['Day_of_week'].isin(selected_days)) &
    (df_raw['Hour'] >= selected_hours[0]) &
    (df_raw['Hour'] <= selected_hours[1]) &
    (df_raw['Light_conditions'].isin(selected_light)) &
    (df_raw['Type_of_vehicle'].isin(selected_vehicles))
]


# ---------------------------------------------------------
# 5. HEADER & TOP EXECUTIVE KPIS
# ---------------------------------------------------------
st.title("🚦 Addis Ababa Road Traffic Safety Intelligence")
st.markdown(
    "An interactive, evidence-based exploratory dashboard evaluating **13,063 police-recorded traffic collisions** "
    "across Addis Ababa sub-city divisions (2017–2020)."
)

# Summary Cards Grid
col1, col2, col3, col4, col5 = st.columns(5)

total_crashes = len(filtered_df)
pct_of_total = (total_crashes / len(df_raw) * 100) if len(df_raw) > 0 else 0
severe_crashes = int(filtered_df['Is_Severe_or_Fatal'].sum())
severe_rate = (severe_crashes / total_crashes * 100) if total_crashes > 0 else 0
total_casualties = int(filtered_df['Number_of_casualties'].sum())
avg_vehicles = float(filtered_df['Number_of_vehicles_involved'].mean()) if total_crashes > 0 else 0

with col1:
    st.metric("Total Collisions", f"{total_crashes:,}", f"{pct_of_total:.1f}% of dataset")
with col2:
    st.metric("Severe / Fatal Events", f"{severe_crashes:,}", f"{severe_rate:.1f}% lethality rate", delta_color="inverse")
with col3:
    st.metric("Severe Injury Rate", f"{severe_rate:.1f}%", "Target Outcome")
with col4:
    st.metric("Total Casualties", f"{total_casualties:,}", f"{total_casualties/max(1, total_crashes):.2f} / crash")
with col5:
    st.metric("Avg Vehicles / Crash", f"{avg_vehicles:.2f}", "Traffic scale")

st.divider()


# ---------------------------------------------------------
# 6. TAB NAVIGATION & INTERACTIVE VISUALIZATIONS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🕒 Temporal Trends (24h & Weekly)",
    "🗺️ 7x24 Density Heatmap",
    "💡 Environmental & Streetlight Hazards",
    "🚗 Vehicle & Casualty Dynamics",
    "📋 Data Explorer & Policy Summary"
])

# ----------------- TAB 1: TEMPORAL DYNAMICS -----------------
with tab1:
    st.subheader("Hourly Collision Volume vs. Severe Injury Rate")
    st.markdown("""
    <div class="insight-card">
        <strong>The Volume-Severity Inversion:</strong> Total collision volume peaks during the late afternoon 
        commute (<strong>17:00–18:00</strong>), but the <em>severe injury rate</em> is at its lowest daily level (14.4%). 
        In contrast, between <strong>21:00 and 02:00</strong>, the severe injury rate surges above <strong>21.7%</strong>.
    </div>
    """, unsafe_allow_html=True)

    if total_crashes > 0:
        hourly_grp = filtered_df.groupby('Hour').size()
        crosstab_h = pd.crosstab(filtered_df['Hour'], filtered_df['Accident_severity'])
        
        # Calculate rate safely
        severe_counts_h = 0
        if 'Serious Injury' in crosstab_h.columns:
            severe_counts_h += crosstab_h['Serious Injury']
        if 'Fatal injury' in crosstab_h.columns:
            severe_counts_h += crosstab_h['Fatal injury']
        rate_h = (severe_counts_h / hourly_grp * 100).round(2)

        fig_h = make_subplots(specs=[[{"secondary_y": True}]])
        fig_h.add_trace(
            go.Bar(
                x=hourly_grp.index,
                y=hourly_grp.values,
                name="Collision Volume",
                marker_color="#2b5c8f",
                opacity=0.85,
                hovertemplate="<b>Hour %{x}:00</b><br>Total Crashes: %{y:,}<extra></extra>"
            ),
            secondary_y=False
        )
        fig_h.add_trace(
            go.Scatter(
                x=rate_h.index,
                y=rate_h.values,
                name="Severe/Fatal Rate (%)",
                mode="lines+markers",
                line=dict(color="#c0392b", width=3),
                marker=dict(size=7, color="#c0392b"),
                hovertemplate="<b>Hour %{x}:00</b><br>Severe/Fatal Rate: %{y:.1f}%<extra></extra>"
            ),
            secondary_y=True
        )
        fig_h.update_layout(
            title="Hourly Volume vs. Severe Injury Rate across Selected Subset",
            xaxis=dict(title="Hour of Day (24-Hour Clock)", tickmode="linear", tick0=0, dtick=1),
            yaxis=dict(title="Total Collisions", showgrid=True),
            yaxis2=dict(title="Severe/Fatal Injury Rate (%)", showgrid=False, range=[0, max(35, float(rate_h.max() * 1.2 if len(rate_h)>0 else 35))]),
            template="plotly_white",
            hovermode="x unified",
            height=450
        )
        st.plotly_chart(fig_h, use_container_width=True)

        # Weekly trend sub-plot
        st.subheader("Weekly Collision & Fatality Trajectory")
        dow_crosstab = pd.crosstab(filtered_df['Day_of_week'], filtered_df['Accident_severity']).reindex(days_order).fillna(0)
        dow_crosstab['Total'] = dow_crosstab.sum(axis=1)

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            fig_w1 = px.line(
                x=dow_crosstab.index,
                y=dow_crosstab['Total'],
                markers=True,
                title="Weekly Collision Volume (Mon to Sun)",
                labels={"x": "Day of Week", "y": "Total Crashes"}
            )
            fig_w1.update_traces(line_color="#2b5c8f", line_width=3)
            fig_w1.update_layout(template="plotly_white", height=320)
            st.plotly_chart(fig_w1, use_container_width=True)

        with col_w2:
            fatal_series = dow_crosstab['Fatal injury'] if 'Fatal injury' in dow_crosstab.columns else pd.Series(0, index=dow_crosstab.index)
            fig_w2 = px.bar(
                x=dow_crosstab.index,
                y=fatal_series,
                title="Raw Fatal Crashes by Day of Week",
                labels={"x": "Day of Week", "y": "Fatal Crashes"},
                color_discrete_sequence=["#c0392b"]
            )
            fig_w2.update_layout(template="plotly_white", height=320)
            st.plotly_chart(fig_w2, use_container_width=True)
    else:
        st.warning("No records match the current filter selection.")


# ----------------- TAB 2: DENSITY HEATMAP -----------------
with tab2:
    st.subheader("7x24 Temporal Density Matrix")
    st.caption("Visualizing collision frequency across all 168 hours of the week.")
    
    if total_crashes > 0:
        heatmap_matrix = pd.crosstab(filtered_df['Day_of_week'], filtered_df['Hour']).reindex(days_order).fillna(0)
        
        fig_hm = px.imshow(
            heatmap_matrix,
            labels=dict(x="Hour of Day", y="Day of Week", color="Collisions"),
            x=heatmap_matrix.columns,
            y=heatmap_matrix.index,
            color_continuous_scale="YlOrRd",
            aspect="auto"
        )
        fig_hm.update_layout(
            title="Collision Intensity Heatmap (Day of Week vs. Hour of Day)",
            template="plotly_white",
            height=420
        )
        st.plotly_chart(fig_hm, use_container_width=True)
        st.info("💡 **Hotspot Insight:** Notice how Friday 16:00–19:00 displays deep crimson intensity, representing the maximum confluence of end-of-week commercial delivery and commuter departures.")
    else:
        st.warning("No records to plot.")


# ----------------- TAB 3: ENVIRONMENTAL & LIGHTING -----------------
with tab3:
    st.subheader("The Infrastructure Hazard: Street Lighting Impact")
    st.markdown("""
    <div class="insight-card">
        <strong>The 2.5x Street Lighting Hazard:</strong> When street lighting is dark or absent, the combined 
        severe/fatal injury rate jumps from <strong>16.8%</strong> (Daylight) to over <strong>41.7%</strong>! 
        Functional municipal lighting directly correlates with survivability.
    </div>
    """, unsafe_allow_html=True)

    if total_crashes > 0:
        light_rates = pd.crosstab(filtered_df['Light_conditions'], filtered_df['Accident_severity'], normalize='index') * 100
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            fig_light = px.bar(
                light_rates,
                barmode='stack',
                title="Severity Proportions across Lighting Conditions (%)",
                color_discrete_map={'Slight Injury': '#2b5c8f', 'Serious Injury': '#e67e22', 'Fatal injury': '#c0392b'},
                labels={"value": "Proportion (%)", "Light_conditions": "Lighting State"}
            )
            fig_light.update_layout(template="plotly_white", height=380, legend_title_text="Outcome")
            st.plotly_chart(fig_light, use_container_width=True)

        with col_l2:
            road_surface_counts = filtered_df['Road_surface_conditions'].value_counts().head(5)
            fig_surface = px.pie(
                values=road_surface_counts.values,
                names=road_surface_counts.index,
                title="Road Surface Moisture Breakdown",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.45
            )
            fig_surface.update_layout(template="plotly_white", height=380)
            st.plotly_chart(fig_surface, use_container_width=True)
    else:
        st.warning("No records to plot.")


# ----------------- TAB 4: VEHICLES & CASUALTIES -----------------
with tab4:
    st.subheader("Vehicle Classifications & Casualty Dispersion")

    if total_crashes > 0:
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            fig_box = px.box(
                filtered_df,
                x="Type_of_vehicle",
                y="Number_of_casualties",
                color="Type_of_vehicle",
                title="Casualty Dispersion by Primary Vehicle Category",
                labels={"Type_of_vehicle": "Vehicle Class", "Number_of_casualties": "Casualties"}
            )
            fig_box.update_layout(template="plotly_white", showlegend=False, height=400)
            st.plotly_chart(fig_box, use_container_width=True)
            st.caption("Buses and heavy trucks exhibit wider casualty whiskers due to occupant density and vehicle mass differentials.")

        with col_v2:
            # Jittered scatter
            np.random.seed(42)
            sample_n = min(2000, len(filtered_df))
            sample_df = filtered_df.sample(sample_n, random_state=42)
            jitter_x = sample_df['Number_of_vehicles_involved'] + np.random.uniform(-0.15, 0.15, sample_n)
            jitter_y = sample_df['Number_of_casualties'] + np.random.uniform(-0.15, 0.15, sample_n)

            fig_sc = px.scatter(
                x=jitter_x,
                y=jitter_y,
                color=sample_df['Accident_severity'],
                color_discrete_map={'Slight Injury': '#2b5c8f', 'Serious Injury': '#e67e22', 'Fatal injury': '#c0392b'},
                title=f"Vehicles vs. Casualties Scatter with Jitter (Sample of {sample_n:,} records)",
                labels={"x": "Vehicles Involved (Jittered)", "y": "Casualties (Jittered)"},
                opacity=0.4
            )
            fig_sc.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_sc, use_container_width=True)
            st.caption("Weak correlation (r = 0.21): single-vehicle crashes (pedestrian strikes, roll-overs) can produce multiple fatalities.")
    else:
        st.warning("No records to plot.")


# ----------------- TAB 5: DATA EXPLORER & POLICY -----------------
with tab5:
    st.subheader("Filtered Collision Records Explorer")
    st.caption(f"Displaying {len(filtered_df):,} matching rows across selected filter parameters.")

    display_cols = st.multiselect(
        "Select Attributes to Display",
        options=list(filtered_df.columns),
        default=['Time', 'Day_of_week', 'Type_of_vehicle', 'Light_conditions', 'Number_of_vehicles_involved', 'Number_of_casualties', 'Cause_of_accident', 'Accident_severity']
    )
    st.dataframe(filtered_df[display_cols].head(100), use_container_width=True)

    # Download button
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="addis_ababa_filtered_crashes.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Key Municipal Policy Interventions for Addis Ababa")
    st.markdown("""
    1. **Rapid Streetlight Maintenance Along High-Speed Corridors:**
       - Repairing dark and unlit street lamps directly targets the **2.5x mortality multiplier**.
    2. **Weekend & Late-Night Enforcement (21:00–03:00):**
       - Shift traffic police checkpoints and automated radar cameras to Friday, Saturday, and Sunday nights when fatal outcomes surge despite lower congestion.
    3. **Standardized Digital Docketing:**
       - Upgrade police reporting from paper logs to digital entry to eliminate unrecorded text placeholders (`'na'`) in casualty demographic fields.
    """)

