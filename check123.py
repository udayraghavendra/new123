#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import math
import streamlit as st


# In[9]:


import streamlit as st
import plotly.graph_objects as go
import math
import pandas as pd
from io import StringIO

# Function to calculate wind angles
# Function to calculate wind angles
def calculate_wind_angle(aws, sog, awd, heading):
    awd_in_radians = math.radians(awd)
    tws = math.sqrt(sog**2 + aws**2 - 2 * sog * aws * math.cos(awd_in_radians))
    
    # Prevent division by zero if both tws and sog are zero
    if sog == 0 and tws == 0:
        return None, None, None
    
    if tws != 0 and sog != 0:
        numerator = aws**2 - tws**2 - sog**2
        denominator = 2 * tws * sog
        if denominator != 0:  # Ensure no division by zero
            ratio = numerator / denominator
            if -1 <= ratio <= 1:
                rwa = math.acos(ratio) * 180 / math.pi
                twa = heading - rwa
                return tws, rwa, twa
    return None, None, None  # Return None if the calculation cannot be performed


# Function to determine wind force (Beaufort Scale) and color
def get_gauge_properties_bf(windforce_bf):
    if windforce_bf <= 3:
        return "green"
    elif 3 < windforce_bf <= 5:
        return "orange"
    else:
        return "red"  # Out of range

# Set up the Streamlit app layout
st.set_page_config(page_title="Engine Power Layout Diagram", layout="wide")
st.title("Main Engine Power Layout Diagram")
st.write("This app allows you to analyze the power layout of the main engine for different operating conditions.")

# Collect input data from the user
perf_date = st.date_input("Performance analysis Date")
vessel = st.text_input("Enter name of Vessel", value="")
voy_from = st.text_input("Voyage from port", value="")
voy_to = st.text_input("Voyage to port", value="")
aws = st.number_input("Enter the Apparent Wind Speed (knots)", min_value=1.0, step=5.0)
awd = st.number_input("Enter the Apparent Wind Direction (degrees)", min_value=0.01, max_value=359.99, step=1.0)
heading = st.number_input("Enter the Heading (degrees)", min_value=0.01, max_value=359.99, step=1.0)
sog = st.number_input("Enter the Speed Over Ground (knots)", min_value=0.0, step=0.1)

# Test Data for Engine Power Curves
line8_speed = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 103.2, 108]
line8_power = [0, 0.08638376, 0.691070079, 2.332361516, 5.528560631, 10.79796998, 18.65889213, 29.62962963, 
               44.22848504, 62.97376093, 86.38375985, 94.94480233, 108.8186589]

# Wind force (Beaufort scale) calculation
windforce_bf = aws / 3  # Assuming the basic Beaufort formula for simplicity
gauge_color = get_gauge_properties_bf(windforce_bf)

# Calculate wind angles (TWS, RWA, TWA)
tws, rwa, twa = calculate_wind_angle(aws, sog, awd, heading)

# Display gauges for wind force
gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta", value=windforce_bf, domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Wind Force (Beaufort Scale)"}, gauge={'axis': {'range': [None, 12]}, 'bar': {'color': gauge_color}}))

# Display calculated wind force gauge
st.plotly_chart(gauge)

# Display the results for TWS, RWA, TWA
if tws is not None:
    st.write(f"True Wind Speed (TWS): {tws:.2f} knots")
    st.write(f"Relative Wind Angle (RWA): {rwa:.2f} degrees")
    st.write(f"True Wind Angle (TWA): {twa:.2f} degrees")
else:
    st.warning("Could not calculate wind angles due to invalid input values.")

# Plot the engine power curves
fig = go.Figure()
fig.add_trace(go.Scatter(x=line8_speed, y=line8_power, mode='lines', name='LRM(5%)', 
                         line=dict(color='blue', width=2, dash='solid')))
fig.update_layout(
    title="Engine Power Curves",
    xaxis_title="Speed (rpm)",
    yaxis_title="Power (kW)",
    legend_title="Engine Line",
    template="plotly_dark"
)

# Display the power curve plot
st.plotly_chart(fig)

# CSV export functionality
def generate_csv(vessel, voy_from, voy_to, perf_date, aws, awd, heading, sog, tws, rwa, twa):
    # Create a DataFrame for the manual inputs and results
    data = {
        "Vessel": [vessel],
        "Voyage From": [voy_from],
        "Voyage To": [voy_to],
        "Performance Date": [str(perf_date)],
        "Apparent Wind Speed (knots)": [aws],
        "Apparent Wind Direction (degrees)": [awd],
        "Heading (degrees)": [heading],
        "Speed Over Ground (knots)": [sog],
        "True Wind Speed (TWS)": [tws],
        "Relative Wind Angle (RWA)": [rwa],
        "True Wind Angle (TWA)": [twa]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

csv_results = generate_csv(vessel, voy_from, voy_to, perf_date, aws, awd, heading, sog, tws, rwa, twa)

# Download CSV file with the manual inputs and results
st.download_button(
    label="Download Manual Inputs and Results as CSV",
    data=csv_results,
    file_name="manual_inputs_results.csv",
    mime="text/csv"
)


# In[ ]:




