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
import joblib

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

@st.cache_resource
def load_ml_model():
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "models" / "crash_severity_model.joblib",
        Path("models/crash_severity_model.joblib"),
        Path("../models/crash_severity_model.joblib")
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return joblib.load(candidate)
            except Exception:
                pass
    return None

df_raw = load_data()
ml_model = load_ml_model()


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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🕒 Temporal Trends (24h & Weekly)",
    "🗺️ 7x24 Density Heatmap",
    "💡 Environmental & Streetlight Hazards",
    "🚗 Vehicle & Casualty Dynamics",
    "🎯 ML Crash Severity Predictor",
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


# ----------------- TAB 5: ML CRASH SEVERITY PREDICTOR -----------------
with tab5:
    st.subheader("🎯 Real-Time Crash Severity Intelligence")
    st.markdown("""
    <div class="insight-card">
        <strong>Cost-Sensitive Decision Intelligence:</strong> This predictive module uses our champion 
        <strong>Balanced Random Forest Pipeline</strong> (ROC-AUC: 0.657, PR-AUC: 0.315). It assigns a ~4.7x penalty 
        to missed fatal/serious collisions to overcome the 82.5% class imbalance. Adjust environmental, vehicular, 
        and infrastructural conditions below to estimate collision trauma risk in real time.
    </div>
    """, unsafe_allow_html=True)

    if ml_model is None:
        st.warning("⚠️ Machine learning model file (`models/crash_severity_model.joblib`) not found. Please run Notebook 06 to build the model.")
    else:
        # Scenario presets for quick testing
        preset = st.radio(
            "Quick Scenario Presets:",
            options=[
                "💡 Custom Scenario",
                "🌙 Midnight Unlit Freight Corridor (High Risk)",
                "☀️ Daytime Commuter Automobile (Low Risk)",
                "🚶 Nighttime Pedestrian Crossing Conflict"
            ],
            horizontal=True
        )

        # Default values based on preset
        if preset == "🌙 Midnight Unlit Freight Corridor (High Risk)":
            def_hour, def_dow = 23, "Saturday"
            def_light = "Darkness - lights unlit"
            def_weather = "Raining"
            def_road_cond = "Wet or damp"
            def_area = "Market areas"
            def_alignment = "Steep grade upward with mountainous terrain"
            def_veh_type = "Lorry (41-100Q)"
            def_ped = "Crossing from driver's nearside"
            def_vehicles = 1
            def_exp = "1-2yr"
        elif preset == "☀️ Daytime Commuter Automobile (Low Risk)":
            def_hour, def_dow = 17, "Friday"
            def_light = "Daylight"
            def_weather = "Normal"
            def_road_cond = "Dry"
            def_area = "Residential areas"
            def_alignment = "Tangent alignment with flat terrain"
            def_veh_type = "Automobile"
            def_ped = "Not a Pedestrian"
            def_vehicles = 2
            def_exp = "5-10yr"
        elif preset == "🚶 Nighttime Pedestrian Crossing Conflict":
            def_hour, def_dow = 21, "Friday"
            def_light = "Darkness - no lighting"
            def_weather = "Normal"
            def_road_cond = "Dry"
            def_area = "Office areas"
            def_alignment = "Tangent alignment with flat terrain"
            def_veh_type = "Automobile"
            def_ped = "Crossing from driver's nearside"
            def_vehicles = 1
            def_exp = "2-5yr"
        else:
            def_hour, def_dow = 18, "Monday"
            def_light = "Daylight"
            def_weather = "Normal"
            def_road_cond = "Dry"
            def_area = "Residential areas"
            def_alignment = "Tangent alignment with flat terrain"
            def_veh_type = "Automobile"
            def_ped = "Not a Pedestrian"
            def_vehicles = 2
            def_exp = "2-5yr"

        st.markdown("##### ⚙️ Collision Scenario Parameters")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("**1. Temporal & Environmental Context**")
            p_hour = st.slider("Hour of Day (24-Hour Clock)", 0, 23, def_hour)
            p_dow = st.selectbox("Day of Week", days_order, index=days_order.index(def_dow) if def_dow in days_order else 0)
            p_light = st.selectbox(
                "Lighting Condition",
                ["Daylight", "Darkness - lights lit", "Darkness - lights unlit", "Darkness - no lighting"],
                index=["Daylight", "Darkness - lights lit", "Darkness - lights unlit", "Darkness - no lighting"].index(def_light) if def_light in ["Daylight", "Darkness - lights lit", "Darkness - lights unlit", "Darkness - no lighting"] else 0
            )
            p_weather = st.selectbox(
                "Weather Condition",
                ["Normal", "Raining", "Raining and Windy", "Fog or mist", "Other", "Unknown"],
                index=["Normal", "Raining", "Raining and Windy", "Fog or mist", "Other", "Unknown"].index(def_weather) if def_weather in ["Normal", "Raining", "Raining and Windy", "Fog or mist", "Other", "Unknown"] else 0
            )
            p_surface = st.selectbox(
                "Road Surface Moisture",
                ["Dry", "Wet or damp", "Snow", "Flood over 3cm"],
                index=["Dry", "Wet or damp", "Snow", "Flood over 3cm"].index(def_road_cond) if def_road_cond in ["Dry", "Wet or damp", "Snow", "Flood over 3cm"] else 0
            )

        with c2:
            st.markdown("**2. Road Geometry & Location**")
            p_area = st.selectbox(
                "Area Accident Occurred",
                ["Residential areas", "Office areas", "Market areas", "School areas", "Hospital areas", "Industrial areas", "Outside rural areas", "Other"],
                index=["Residential areas", "Office areas", "Market areas", "School areas", "Hospital areas", "Industrial areas", "Outside rural areas", "Other"].index(def_area) if def_area in ["Residential areas", "Office areas", "Market areas", "School areas", "Hospital areas", "Industrial areas", "Outside rural areas", "Other"] else 0
            )
            p_alignment = st.selectbox(
                "Road Alignment & Gradient",
                ["Tangent alignment with flat terrain", "Steep grade upward with mountainous terrain", "Steep grade downward with mountainous terrain", "Sharp reverse curve", "Gentle horizontal curve"],
                index=["Tangent alignment with flat terrain", "Steep grade upward with mountainous terrain", "Steep grade downward with mountainous terrain", "Sharp reverse curve", "Gentle horizontal curve"].index(def_alignment) if def_alignment in ["Tangent alignment with flat terrain", "Steep grade upward with mountainous terrain", "Steep grade downward with mountainous terrain", "Sharp reverse curve", "Gentle horizontal curve"] else 0
            )
            p_junction = st.selectbox(
                "Junction Geometry",
                ["No junction", "Y Shape", "T Shape", "Cross shape", "Roundabout", "O Shape"],
                index=0
            )
            p_lanes = st.selectbox(
                "Lanes or Medians",
                ["Two-way (divided with broken lines road marking)", "Two-way (divided with solid lines road marking)", "Undivided two-way", "One way", "other"],
                index=0
            )
            p_road_type = st.selectbox(
                "Pavement Surface Type",
                ["Asphalt roads", "Earth roads", "Gravel roads", "other"],
                index=0
            )

        with c3:
            st.markdown("**3. Vehicle & Behavioral Profile**")
            p_veh = st.selectbox(
                "Vehicle Category",
                ["Automobile", "Lorry (41-100Q)", "Public (> 45 seats)", "Pick up upto 10Q", "Public (12-45 seats)", "Lorry (11-40Q)", "Motorcycle", "Taxi", "other"],
                index=["Automobile", "Lorry (41-100Q)", "Public (> 45 seats)", "Pick up upto 10Q", "Public (12-45 seats)", "Lorry (11-40Q)", "Motorcycle", "Taxi", "other"].index(def_veh_type) if def_veh_type in ["Automobile", "Lorry (41-100Q)", "Public (> 45 seats)", "Pick up upto 10Q", "Public (12-45 seats)", "Lorry (11-40Q)", "Motorcycle", "Taxi", "other"] else 0
            )
            p_vehicles_n = st.slider("Vehicles Involved", 1, 7, def_vehicles)
            p_ped = st.selectbox(
                "Pedestrian Movement",
                ["Not a Pedestrian", "Crossing from driver's nearside", "Crossing from driver's offside", "In carriageway, statioNot a Pedestrianry - not crossing  (standing or playing) - masked by parked or statioNot a Pedestrianry vehicle", "other"],
                index=["Not a Pedestrian", "Crossing from driver's nearside", "Crossing from driver's offside", "In carriageway, statioNot a Pedestrianry - not crossing  (standing or playing) - masked by parked or statioNot a Pedestrianry vehicle", "other"].index(def_ped) if def_ped in ["Not a Pedestrian", "Crossing from driver's nearside", "Crossing from driver's offside", "In carriageway, statioNot a Pedestrianry - not crossing  (standing or playing) - masked by parked or statioNot a Pedestrianry vehicle", "other"] else 0
            )
            p_exp = st.selectbox(
                "Driver Experience",
                ["Below 1yr", "1-2yr", "2-5yr", "5-10yr", "Above 10yr", "Unknown"],
                index=["Below 1yr", "1-2yr", "2-5yr", "5-10yr", "Above 10yr", "Unknown"].index(def_exp) if def_exp in ["Below 1yr", "1-2yr", "2-5yr", "5-10yr", "Above 10yr", "Unknown"] else 2
            )
            p_driver_age = st.selectbox("Driver Age Band", ["18-30", "31-50", "Over 51", "Under 18", "Unknown"], index=0)
            p_driver_sex = st.selectbox("Driver Gender", ["Male", "Female", "Unknown"], index=0)

        # Assemble full input DataFrame with all 24 required model features
        input_data = pd.DataFrame([{
            'Hour': p_hour,
            'Number_of_vehicles_involved': p_vehicles_n,
            'Day_of_week': p_dow,
            'Age_band_of_driver': p_driver_age,
            'Drivers_gender': p_driver_sex,
            'Educational_level': "Junior high school",
            'Vehicle_driver_relation': "Employee",
            'Driving_experience': p_exp,
            'Type_of_vehicle': p_veh,
            'Owner_of_vehicle': "Owner",
            'Service_year_of_vehicle': "Unknown",
            'Defect_of_vehicle': "No defect",
            'Area_accident_occured': p_area,
            'Lanes_or_Medians': p_lanes,
            'Road_allignment': p_alignment,
            'Types_of_Junction': p_junction,
            'Road_surface_type': p_road_type,
            'Road_surface_conditions': p_surface,
            'Light_conditions': p_light,
            'Weather_conditions': p_weather,
            'Type_of_collision': "Vehicle with vehicle collision" if p_ped == "Not a Pedestrian" else "Collision with pedestrians",
            'Vehicle_movement': "Going straight",
            'Pedestrian_movement': p_ped,
            'Cause_of_accident': "No priority to vehicle"
        }])

        st.markdown("---")
        
        # Real-time inference
        prob_dist = ml_model.predict_proba(input_data)[0]
        prob_slight = prob_dist[0]
        prob_severe = prob_dist[1]

        # Executive Prediction Card
        st.subheader("⚡ Live Collision Severity Prediction")
        
        res_col1, res_col2, res_col3 = st.columns([1.2, 1, 1])
        with res_col1:
            if prob_severe >= 0.50:
                st.error(f"### 🚨 HIGH TRAUMA RISK: {prob_severe:.1%}")
                st.markdown("**Classification:** Severe or Fatal Collision Expected.")
                risk_tier = "High"
            elif prob_severe >= 0.25:
                st.warning(f"### ⚠️ MODERATE TRAUMA RISK: {prob_severe:.1%}")
                st.markdown("**Classification:** Elevated Risk (Exceeds City Baseline of 17.5%).")
                risk_tier = "Moderate"
            else:
                st.success(f"### 🟢 LOW TRAUMA RISK: {prob_severe:.1%}")
                st.markdown("**Classification:** Minor / Slight Injury Probability.")
                risk_tier = "Low"

        with res_col2:
            diff_from_baseline = ((prob_severe - 0.1751) / 0.1751) * 100
            st.metric("Severe / Fatal Probability", f"{prob_severe:.1%}", f"{diff_from_baseline:+.1f}% vs. baseline")

        with res_col3:
            st.metric("Slight Injury Probability", f"{prob_slight:.1%}")

        # Active Risk Multipliers Analysis
        active_factors = []
        if "unlit" in p_light.lower() or "no lighting" in p_light.lower():
            active_factors.append("💡 **Unlit / Missing Streetlights:** Triggers municipal 2.5x darkness severity multiplier.")
        if p_area == "Market areas":
            active_factors.append("🏬 **Market Area:** Highly congested pedestrian conflict zone (+3.97x severity odds).")
        if "mountainous" in p_alignment.lower():
            active_factors.append("⛰️ **Mountainous Gradient:** Steep elevation adds brake fatigue and acceleration risk (+1.77x odds).")
        if p_ped != "Not a Pedestrian":
            active_factors.append("🚶 **Pedestrian Involvement:** Direct pedestrian vulnerability significantly increases fatal injury potential.")
        if "Lorry" in p_veh or "Public" in p_veh:
            active_factors.append("🚛 **Heavy Freight / High-Capacity Transit:** Large kinetic mass differential and occupant exposure.")
        if p_hour >= 21 or p_hour <= 3:
            active_factors.append("🌙 **Late-Night Window:** High travel speeds and reduced driver alertness.")

        if active_factors:
            st.info("**Key Compound Risk Multipliers Active in this Scenario:**\n- " + "\n- ".join(active_factors))

        # Model Diagnostics Expander
        with st.expander("📊 Inspect Machine Learning Diagnostics & Model Benchmark"):
            st.markdown("""
            **Multi-Model Benchmark on Holdout Evaluation Set ($N=2,613$):**
            """)
            diag_df = pd.DataFrame([
                {"Model": "Dummy Majority Baseline", "Accuracy": "82.5%", "Severe Recall": "0.0%", "Severe Precision": "0.0%", "ROC-AUC": "0.500", "PR-AUC": "0.175"},
                {"Model": "Cost-Sensitive Logistic Regression", "Accuracy": "63.6%", "Severe Recall": "52.3%", "Severe Precision": "24.6%", "ROC-AUC": "0.616", "PR-AUC": "0.276"},
                {"Model": "Balanced Random Forest (Active)", "Accuracy": "76.7%", "Severe Recall": "33.0%", "Severe Precision": "33.2%", "ROC-AUC": "0.657", "PR-AUC": "0.315"},
                {"Model": "HistGradientBoosting", "Accuracy": "71.3%", "Severe Recall": "40.3%", "Severe Precision": "27.8%", "ROC-AUC": "0.632", "PR-AUC": "0.286"}
            ])
            st.table(diag_df)

            curve_img = Path("reports/figures/10_model_evaluation_curves.png")
            if not curve_img.exists():
                curve_img = Path("../reports/figures/10_model_evaluation_curves.png")
            if curve_img.exists():
                st.image(str(curve_img), caption="Figure 10: Multi-Panel Model Diagnostic Curves (ROC, Precision-Recall, and Normalized Confusion Matrix)", use_container_width=True)


# ----------------- TAB 6: DATA EXPLORER & POLICY -----------------
with tab6:
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

