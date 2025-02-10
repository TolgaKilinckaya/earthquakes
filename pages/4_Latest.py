import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from branca.colormap import linear

# CSV output filename
CSV_FILENAME = "filtered_earthquakes.csv"


def get_earthquakes_data(start_date, end_date, min_magnitude, max_magnitude, min_depth, max_depth):
    base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    parameters = {
        "format": "geojson",
        "starttime": start_date,
        "endtime": end_date,
        "minmagnitude": min_magnitude,
        "maxmagnitude": max_magnitude,
        "mindepth": min_depth,
        "maxdepth": max_depth,
    }
    response = requests.get(base_url, params=parameters)
    return response.json()


def main():
    st.title("Earthquakes Data Export and Visualization")

    # Sidebar with interactive tools
    st.sidebar.title("Filter Options")

    # Magnitude slider
    min_magnitude = st.sidebar.slider("Minimum Magnitude", 0.0, 10.0, 4.0)
    max_magnitude = st.sidebar.slider("Maximum Magnitude", 0.0, 10.0, 10.0)

    # Hypocenter depth slider
    min_depth = st.sidebar.slider("Minimum Hypocenter Depth (km)", 0.0, 700.0, 0.0)
    max_depth = st.sidebar.slider("Maximum Hypocenter Depth (km)", 0.0, 700.0, 700.0)

    # Calculate start and end dates for the last 10 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)

    # Fetch earthquake data based on user-selected parameters
    earthquakes_data = get_earthquakes_data(
        start_date.isoformat(),
        end_date.isoformat(),
        min_magnitude,
        max_magnitude,
        min_depth,
        max_depth
    )

    if "features" in earthquakes_data.keys():
        # Extract latitude, longitude, magnitude, and depth
        data = [
            (
                feature['geometry']['coordinates'][1],
                feature['geometry']['coordinates'][0],
                feature['properties']['mag'],
                feature['geometry']['coordinates'][2]
            )
            for feature in earthquakes_data['features']
        ]

        # Create a DataFrame with 'LATITUDE', 'LONGITUDE', 'MAGNITUDE', and 'DEPTH' columns
        df = pd.DataFrame(data, columns=['LATITUDE', 'LONGITUDE', 'MAGNITUDE', 'DEPTH'])

        # Filter data based on specified latitude and longitude range
        filtered_data = df[
            (df['LATITUDE'] >= 0) & (df['LATITUDE'] <= 1000) &
            (df['LONGITUDE'] >= 0) & (df['LONGITUDE'] <= 1000)
        ]

        # Save filtered data to CSV
        filtered_data.to_csv(CSV_FILENAME, index=False)
        st.success(f"Filtered data saved as {CSV_FILENAME}")

        # Create a folium map centered on median coordinates if filtered data exists
        if not filtered_data.empty:
            folium_map = folium.Map(location=[np.median(filtered_data['LATITUDE']), np.median(filtered_data['LONGITUDE'])], zoom_start=7)

            # Create a color scale for magnitude
            colormap = linear.YlOrRd_09.scale(filtered_data['MAGNITUDE'].min(), filtered_data['MAGNITUDE'].max())

            # Add markers to the map with color based on magnitude
            for _, row in filtered_data.iterrows():
                folium.CircleMarker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    radius=5,
                    color=colormap(row['MAGNITUDE']),
                    fill=True,
                    fill_color=colormap(row['MAGNITUDE']),
                    fill_opacity=0.7,
                    popup=f"Magnitude: {row['MAGNITUDE']}, Depth: {row['DEPTH']} km",
                ).add_to(folium_map)

            # Display the folium map using Streamlit
            folium_static(folium_map)
        else:
            st.warning("No data available for the selected parameters and location range.")
    else:
        st.warning("No earthquake data available for the selected parameters.")


if __name__ == "__main__":
    main()