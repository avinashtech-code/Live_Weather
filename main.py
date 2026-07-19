import streamlit as st
import requests
from datetime import datetime

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌦",
    layout="wide"
)

st.title("🌦 Live Weather Dashboard")
st.markdown("Search any city in the world and get live weather updates.")

st.divider()

# ==========================================================
# Weather Code Mapping
# ==========================================================

WEATHER_CODES = {
    0: " Clear Sky",
    1: " Mainly Clear",
    2: " Partly Cloudy",
    3: " Overcast",
    45: " Fog",
    48: " Depositing Fog",

    51: " Light Drizzle",
    53: " Moderate Drizzle",
    55: " Dense Drizzle",

    61: " Slight Rain",
    63: " Moderate Rain",
    65: " Heavy Rain",

    71: " Slight Snow",
    73: " Moderate Snow",
    75: " Heavy Snow",

    80: " Rain Showers",
    81: " Heavy Showers",
    82: " Violent Showers",

    95: " Thunderstorm",
    96: " Thunderstorm + Hail",
    99: " Severe Thunderstorm"
}

# ==========================================================
# Helper Functions
# ==========================================================

def get_location(city):

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    if "results" not in data:
        return None

    return data["results"][0]


def get_weather(latitude, longitude):

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}"
        f"&longitude={longitude}"
        "&current="
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "is_day,"
        "precipitation,"
        "weather_code,"
        "surface_pressure,"
        "wind_speed_10m,"
        "wind_direction_10m"
        "&daily="
        "sunrise,"
        "sunset"
        "&timezone=auto"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()


# ==========================================================
# Search Section
# ==========================================================

city = st.text_input(
    " Enter City Name",
    placeholder="Example: Delhi"
)

search = st.button(
    "Search Weather",
    use_container_width=True
)

# ==========================================================
# Main Logic
# ==========================================================

if search:

    if city.strip() == "":
        st.warning("Please enter a city name.")
        st.stop()

    with st.spinner("Fetching weather..."):

        location = get_location(city)

        if location is None:
            st.error("City not found.")
            st.stop()

        latitude = location["latitude"]
        longitude = location["longitude"]

        country = location.get("country", "Unknown")
        state = location.get("admin1", "Unknown")

        weather = get_weather(latitude, longitude)

        if weather is None:
            st.error("Unable to fetch weather.")
            st.stop()

        current = weather["current"]
        daily = weather["daily"]

        weather_text = WEATHER_CODES.get(
            current["weather_code"],
            "Unknown"
        )

        st.success("Weather fetched successfully!")

        st.divider()

        st.subheader(" Location")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("City", city.title())

        with col2:
            st.metric("State", state)

        with col3:
            st.metric("Country", country)

        with col4:
            st.metric(
                "Coordinates",
                f"{latitude:.2f}, {longitude:.2f}"
            )

        st.divider()

        st.subheader("🌤 Current Weather")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Temperature",
                f"{current['temperature_2m']} °C"
            )

        with c2:
            st.metric(
                "Feels Like",
                f"{current['apparent_temperature']} °C"
            )

        with c3:
            st.metric(
                "Humidity",
                f"{current['relative_humidity_2m']} %"
            )

        with c4:
            st.metric(
                "Wind Speed",
                f"{current['wind_speed_10m']} km/h"
            )

        c5, c6, c7, c8 = st.columns(4)

        with c5:
            st.metric(
                "Pressure",
                f"{current['surface_pressure']} hPa"
            )

        with c6:
            st.metric(
                "Wind Direction",
                f"{current['wind_direction_10m']}°"
            )

        with c7:
            st.metric(
                "Rain",
                f"{current['precipitation']} mm"
            )

        with c8:
            st.metric(
                "Condition",
                weather_text
            )

        st.divider()

    # ==========================================================
# Sunrise & Sunset
# ==========================================================

st.subheader(" Sunrise & Sunset")

sun1, sun2 = st.columns(2)

sunrise = daily["sunrise"][0]
sunset = daily["sunset"][0]

sunrise = datetime.fromisoformat(sunrise).strftime("%I:%M %p")
sunset = datetime.fromisoformat(sunset).strftime("%I:%M %p")

with sun1:
    st.metric(" Sunrise", sunrise)

with sun2:
    st.metric(" Sunset", sunset)

st.divider()

# ==========================================================
# 7-Day Forecast
# ==========================================================

st.subheader(" 7-Day Weather Forecast")

forecast = {
    "Date": weather["daily"]["time"],
    "Min Temp (°C)": weather["daily"]["temperature_2m_min"],
    "Max Temp (°C)": weather["daily"]["temperature_2m_max"],
    "Weather Code": weather["daily"]["weather_code"]
}

import pandas as pd

forecast_df = pd.DataFrame(forecast)

forecast_df["Condition"] = forecast_df["Weather Code"].map(
    lambda x: WEATHER_CODES.get(x, "Unknown")
)

forecast_df = forecast_df.drop(columns=["Weather Code"])

st.dataframe(
    forecast_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# Temperature Chart
# ==========================================================

st.subheader("🌡 Temperature Trend")

temp_df = pd.DataFrame({
    "Date": weather["daily"]["time"],
    "Maximum": weather["daily"]["temperature_2m_max"],
    "Minimum": weather["daily"]["temperature_2m_min"]
})

st.line_chart(
    temp_df.set_index("Date")
)

st.divider()

# ==========================================================
# Weather Summary
# ==========================================================

st.subheader("📋 Weather Summary")

summary = f"""
 Location : {city.title()}, {country}

 Condition : {weather_text}

 Temperature : {current['temperature_2m']} °C

 Feels Like : {current['apparent_temperature']} °C

 Humidity : {current['relative_humidity_2m']} %

 Wind Speed : {current['wind_speed_10m']} km/h

 Wind Direction : {current['wind_direction_10m']}°

 Sunrise : {sunrise}

 Sunset : {sunset}
"""

st.text(summary)

st.divider()

# ==========================================================
# Download Report
# ==========================================================

st.download_button(
    label=" Download Forecast CSV",
    data=forecast_df.to_csv(index=False),
    file_name=f"{city}_forecast.csv",
    mime="text/csv",
    use_container_width=True
)
