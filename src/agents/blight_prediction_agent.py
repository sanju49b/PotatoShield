"""
Blight Prediction Agent with Comprehensive Weather Data Collection

This module provides:
1. ComprehensiveBlightDataCollector - Collects comprehensive weather and air quality data
2. BlightPredictionAgent - Analyzes weather data to predict Late Blight and Early Blight risks

Both classes work together seamlessly for end-to-end blight prediction.
"""

import requests
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Generator, List
from collections import defaultdict

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from src.state.agent_state import AgentState

# Import Tavily for enhanced recommendations
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("[WARNING] Tavily not installed. Install with: pip install tavily-python")


class ComprehensiveBlightDataCollector:
    """
    Complete weather data collector for blight prediction with ALL available features.
    Aggregates hourly data into daily summaries for each 24-hour period.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the data collector.
        
        Args:
            api_key: Optional API key for Open-Meteo customer endpoints.
                    If None, uses free public endpoints.
        """
        self.api_key = api_key

        if not api_key:
            self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            self.forecast_url = "https://api.open-meteo.com/v1/forecast"
            self.historical_url = "https://archive-api.open-meteo.com/v1/archive"
            self.air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        else:
            self.geocoding_url = "https://customer-geocoding-api.open-meteo.com/v1/search"
            self.forecast_url = "https://customer-api.open-meteo.com/v1/forecast"
            self.historical_url = "https://customer-archive-api.open-meteo.com/v1/archive"
            self.air_quality_url = "https://customer-air-quality-api.open-meteo.com/v1/air-quality"

    def get_location_coordinates(self, location_name: str, country_code: Optional[str] = None) -> Dict:
        """
        Auto-detect location from name using geocoding API.
        
        Args:
            location_name: Name of the location (e.g., "Hyderabad")
            country_code: Optional country code (e.g., "IN" for India)
            
        Returns:
            Dict with location details including latitude, longitude, elevation, etc.
            
        Raises:
            ValueError: If location is not found
        """
        params = {
            "name": location_name.strip(),
            "count": 10,
            "language": "en",
            "format": "json"
        }

        if country_code:
            params["country_code"] = country_code

        try:
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "results" in data and len(data["results"]) > 0:
                result = self._select_best_location_match(location_name, data["results"])
                if result:
                    return result
            else:
                # Try without country code if first attempt failed
                if country_code:
                    print(f"[INFO] Retrying geocoding without country code for: {location_name}")
                    params_no_country = {
                        "name": location_name.strip(),
                        "count": 10,
                        "language": "en",
                        "format": "json"
                    }
                    response = requests.get(self.geocoding_url, params=params_no_country, timeout=10)
                    data = response.json()
                    
                    if "results" in data and len(data["results"]) > 0:
                        result = self._select_best_location_match(location_name, data["results"], country_code)
                        if result:
                            return result
                
                raise ValueError(f"Location '{location_name}' not found. Please double-check the spelling.")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Geocoding API error for '{location_name}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing location '{location_name}': {str(e)}")
    
    def _clean_location_name(self, location_name: str, country_code: Optional[str] = None) -> str:
        """
        Preserve the exact user-supplied location. No normalization permitted.
        """
        if not location_name:
            return location_name
        return location_name.strip()

    def _select_best_location_match(self, original_query: str, results: list, preferred_country_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Choose the geocoding result that best matches the original query string.
        """
        if not results:
            return None

        normalized_query = original_query.lower().strip()
        query_tokens = [token.strip() for token in normalized_query.replace(",", " ").split() if token.strip()]

        best_match = None
        best_score = -1

        for result in results:
            candidate_str = " ".join([
                result.get("name", ""),
                result.get("admin1", "") or "",
                result.get("country", "") or ""
            ]).lower()

            score = 0

            if preferred_country_code and result.get("country_code", "").lower() == preferred_country_code.lower():
                score += 5

            # Token overlap
            for token in query_tokens:
                if token and token in candidate_str:
                    score += 1

            # Exact substring match bonus
            if normalized_query in candidate_str:
                score += 3

            if score > best_score:
                best_score = score
                best_match = result

        if best_match:
            return {
                "latitude": best_match["latitude"],
                "longitude": best_match["longitude"],
                "elevation": best_match.get("elevation", 0),
                "timezone": best_match.get("timezone", "UTC"),
                "city": best_match.get("name", original_query),
                "country": best_match.get("country", ""),
                "admin1": best_match.get("admin1", "")
            }

        return None

    def get_comprehensive_weather_data(
        self,
        latitude: float,
        longitude: float,
        target_date: str,
        timezone: str = "auto",
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Get ALL available weather data for blight prediction.
        Fetches both historical and forecast data as needed.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            target_date: Target date in YYYY-MM-DD format
            timezone: Timezone string (default: "auto")
            
        Returns:
            Dict containing historical and forecast weather data
        """
        target = datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.now().date()
        target_date_obj = target.date()

        # Calculate window dates (8-day window: 4 days before + 3 days after)
        start_date = (target - timedelta(days=4)).strftime("%Y-%m-%d")
        end_date = (target + timedelta(days=3)).strftime("%Y-%m-%d")

        # Helper function to send progress updates
        def send_progress(message: str):
            if progress_callback:
                progress_callback(message)
            else:
                print(message)
        
        send_progress(f"\n{'='*70}")
        send_progress(f"COMPREHENSIVE DATA COLLECTION FOR BLIGHT PREDICTION")
        send_progress(f"{'='*70}")
        send_progress(f"Target Date: {target_date}")
        send_progress(f"Window: {start_date} to {end_date} (8 days)")
        send_progress(f"Today's Date: {today}")

        # ===== HOURLY WEATHER VARIABLES (Ground Level Focus) =====
        hourly_vars = [
            "temperature_2m", "apparent_temperature", "dew_point_2m",
            "relative_humidity_2m", "precipitation", "rain", "showers", "snowfall",
            "precipitation_probability", "wind_speed_10m", "wind_direction_10m",
            "wind_gusts_10m", "surface_pressure", "pressure_msl", "cloud_cover",
            "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
            "soil_temperature_0cm", "soil_temperature_0_to_7cm",
            "soil_temperature_7_to_28cm", "soil_temperature_28_to_100cm",
            "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm",
            "soil_moisture_28_to_100cm", "snow_depth", "surface_temperature",
            "shortwave_radiation", "direct_radiation", "diffuse_radiation",
            "vapour_pressure_deficit", "evapotranspiration",
            "et0_fao_evapotranspiration", "visibility", "weather_code",
            "is_day", "sunshine_duration", "freezing_level_height", "cape"
        ]

        # ===== DAILY AGGREGATIONS =====
        daily_vars = [
            "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
            "apparent_temperature_max", "apparent_temperature_min",
            "apparent_temperature_mean", "precipitation_sum", "rain_sum",
            "snowfall_sum", "precipitation_hours", "precipitation_probability_max",
            "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
            "weather_code", "sunrise", "sunset", "sunshine_duration",
            "daylight_duration", "uv_index_max", "uv_index_clear_sky_max",
            "shortwave_radiation_sum", "et0_fao_evapotranspiration"
        ]

        weather_data = {}

        # Check if we need historical data
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()

        if start_date_obj <= today:
            hist_end = min(target_date_obj, today - timedelta(days=1))

            send_progress(f"Fetching historical weather data (up to {hist_end})...")
            hist_params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": hist_end.strftime("%Y-%m-%d"),
                "hourly": ",".join(hourly_vars),
                "daily": ",".join(daily_vars),
                "timezone": timezone
            }

            try:
                hist_response = requests.get(self.historical_url, params=hist_params)
                if hist_response.status_code == 200:
                    weather_data['historical'] = hist_response.json()
                    send_progress(f"[OK] Historical data fetched successfully")
                else:
                    send_progress(f"[WARNING] Historical API returned status {hist_response.status_code}")
            except Exception as e:
                send_progress(f"[WARNING] Error fetching historical data: {e}")

        # Fetch forecast data
        send_progress("Fetching forecast weather data...")

        days_before_today = (today - start_date_obj).days
        days_after_today = (datetime.strptime(end_date, "%Y-%m-%d").date() - today).days

        forecast_params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(hourly_vars),
            "daily": ",".join(daily_vars),
            "timezone": timezone,
            "forecast_days": max(7, days_after_today + 1),
            "past_days": max(5, days_before_today)
        }

        try:
            forecast_response = requests.get(self.forecast_url, params=forecast_params)
            if forecast_response.status_code == 200:
                weather_data['forecast'] = forecast_response.json()
                send_progress(f"[OK] Forecast data fetched successfully")
            else:
                send_progress(f"[WARNING] Forecast API returned status {forecast_response.status_code}")
        except Exception as e:
            send_progress(f"[WARNING] Error fetching forecast data: {e}")

        return weather_data

    def get_air_quality_data(
        self,
        latitude: float,
        longitude: float,
        target_date: str,
        timezone: str = "auto",
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Get air quality data for the location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            target_date: Target date in YYYY-MM-DD format
            timezone: Timezone string (default: "auto")
            progress_callback: Optional callback function to send progress updates
            
        Returns:
            Dict containing air quality data
        """
        def send_progress(message: str):
            if progress_callback:
                progress_callback(message)
            else:
                print(message)
        
        send_progress("Fetching air quality data...")

        air_quality_vars = [
            "pm10", "pm2_5", "ozone", "nitrogen_dioxide", "sulphur_dioxide",
            "aerosol_optical_depth", "dust", "uv_index", "uv_index_clear_sky",
            "ammonia", "european_aqi", "us_aqi"
        ]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(air_quality_vars),
            "timezone": timezone,
            "forecast_days": 7,
            "past_days": 5
        }

        try:
            response = requests.get(self.air_quality_url, params=params)
            if response.status_code == 200:
                send_progress(f"[OK] Air quality data fetched successfully")
                return response.json()
            else:
                print(f"[WARNING] Air Quality API returned status {response.status_code}")
                return {}
        except Exception as e:
            print(f"[WARNING] Could not fetch air quality data: {e}")
            return {}

    def _aggregate_hourly_to_daily(self, hourly_data: Dict) -> Dict:
        """
        Aggregate hourly data into daily 24-hour summaries.
        Returns one record per day with aggregated statistics.
        
        Args:
            hourly_data: Dict with hourly time series data
            
        Returns:
            Dict with daily aggregated data (min, max, mean, sum for each variable)
        """
        if not hourly_data or 'time' not in hourly_data:
            return {}

        # Group data by date
        daily_groups = defaultdict(lambda: defaultdict(list))

        for i, time_str in enumerate(hourly_data['time']):
            try:
                dt = datetime.fromisoformat(time_str.replace('Z', ''))
                date_key = dt.date().strftime("%Y-%m-%d")

                for key, values in hourly_data.items():
                    if key != 'time' and i < len(values):
                        value = values[i]
                        if value is not None:
                            daily_groups[date_key][key].append(value)
            except:
                continue

        # Aggregate each day's data
        aggregated = {'date': []}

        for date in sorted(daily_groups.keys()):
            aggregated['date'].append(date)
            day_data = daily_groups[date]

            for key, values in day_data.items():
                if not values:
                    continue

                # Initialize dict if needed
                if f'{key}_min' not in aggregated:
                    aggregated[f'{key}_min'] = []
                if f'{key}_max' not in aggregated:
                    aggregated[f'{key}_max'] = []
                if f'{key}_mean' not in aggregated:
                    aggregated[f'{key}_mean'] = []
                if f'{key}_sum' not in aggregated:
                    aggregated[f'{key}_sum'] = []

                # Calculate statistics
                aggregated[f'{key}_min'].append(min(values))
                aggregated[f'{key}_max'].append(max(values))
                aggregated[f'{key}_mean'].append(sum(values) / len(values))
                aggregated[f'{key}_sum'].append(sum(values))

        return aggregated

    def _merge_time_series(self, *sources: Dict[str, List]) -> Dict[str, List]:
        """
        Merge multiple hourly/daily series with aligned timestamps.
        Keeps order sorted by timestamp and fills missing variables with None.
        
        Args:
            *sources: Variable number of time series dictionaries
            
        Returns:
            Merged time series with all timestamps and variables
        """
        all_times = set()
        for src in sources:
            if src and "time" in src:
                all_times.update(src["time"])
        if not all_times:
            return {}

        # Sort times
        sorted_times = sorted(all_times)

        # Collect all variable names
        all_vars = set()
        for src in sources:
            if src:
                all_vars.update(k for k in src.keys() if k != "time")

        merged = {"time": sorted_times}
        for var in all_vars:
            merged[var] = [None] * len(sorted_times)

        # Fill in available values
        time_to_idx = {t: i for i, t in enumerate(sorted_times)}
        for src in sources:
            if not src or "time" not in src:
                continue
            for i, t in enumerate(src["time"]):
                if t not in time_to_idx:
                    continue
                idx = time_to_idx[t]
                for var in src:
                    if var == "time":
                        continue
                    vals = src.get(var, [])
                    if i < len(vals) and vals[i] is not None:
                        merged[var][idx] = vals[i]

        return merged

    def _extract_window(self, weather_data: Dict, target_date: str, progress_callback: Optional[callable] = None) -> Dict:
        """
        Extract 8-day window from weather data.
        
        Args:
            weather_data: Combined historical and forecast data
            target_date: Target date in YYYY-MM-DD format
            progress_callback: Optional callback function to send progress updates
            
        Returns:
            Dict with hourly and daily data filtered to 8-day window
        """
        def send_progress(message: str):
            if progress_callback:
                progress_callback(message)
            else:
                print(message)
        
        target = datetime.strptime(target_date, "%Y-%m-%d")
        window_start = target - timedelta(days=4)
        window_end = target + timedelta(days=3)

        send_progress(f"\nExtracting 8-day window: {window_start.date()} to {window_end.date()}")

        # Merge hourly historical + forecast
        hist_hourly = weather_data.get("historical", {}).get("hourly", {})
        fcst_hourly = weather_data.get("forecast", {}).get("hourly", {})
        merged_hourly = self._merge_time_series(hist_hourly, fcst_hourly)

        # Filter hourly to window
        filtered_hourly = {"time": []}
        if merged_hourly:
            for i, t in enumerate(merged_hourly["time"]):
                try:
                    dt = datetime.fromisoformat(t.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    continue
                if window_start <= dt <= window_end + timedelta(hours=23, minutes=59):
                    filtered_hourly["time"].append(t)
                    for var, vals in merged_hourly.items():
                        if var == "time":
                            continue
                        filtered_hourly.setdefault(var, []).append(
                            vals[i] if i < len(vals) else None
                        )

        # Merge daily historical + forecast
        hist_daily = weather_data.get("historical", {}).get("daily", {})
        fcst_daily = weather_data.get("forecast", {}).get("daily", {})
        merged_daily = self._merge_time_series(hist_daily, fcst_daily)

        # Filter daily to window
        filtered_daily = {"time": []}
        if merged_daily:
            for i, d in enumerate(merged_daily["time"]):
                try:
                    dt = datetime.strptime(d, "%Y-%m-%d")
                except Exception:
                    continue
                if window_start.date() <= dt.date() <= window_end.date():
                    filtered_daily["time"].append(d)
                    for var, vals in merged_daily.items():
                        if var == "time":
                            continue
                        filtered_daily.setdefault(var, []).append(
                            vals[i] if i < len(vals) else None
                        )

        print(f"[OK] Extracted {len(filtered_hourly.get('time', []))} hourly points")
        print(f"[OK] Extracted {len(filtered_daily.get('time', []))} daily points")

        return {"hourly": filtered_hourly, "daily": filtered_daily}

    def _extract_air_quality_window(self, air_quality_data: Dict, target_date: str) -> Dict:
        """
        Extract 8-day window from air quality data.
        
        Args:
            air_quality_data: Air quality data from API
            target_date: Target date in YYYY-MM-DD format
            
        Returns:
            Dict with air quality data filtered to 8-day window
        """
        if not air_quality_data or 'hourly' not in air_quality_data:
            return {}

        target = datetime.strptime(target_date, "%Y-%m-%d")
        window_start = target - timedelta(days=4)
        window_end = target + timedelta(days=3)

        filtered = {'time': []}

        for i, time_str in enumerate(air_quality_data['hourly'].get('time', [])):
            try:
                time_dt = datetime.fromisoformat(time_str.replace('Z', '+00:00')).replace(tzinfo=None)

                if window_start <= time_dt <= window_end + timedelta(hours=23, minutes=59):
                    filtered['time'].append(time_str)

                    for key, values in air_quality_data['hourly'].items():
                        if key != 'time':
                            if key not in filtered:
                                filtered[key] = []
                            filtered[key].append(values[i] if i < len(values) else None)
            except:
                continue

        return {'hourly': filtered}

    def collect_complete_dataset(
        self,
        location_name: str,
        target_date: str,
        country_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Complete data collection pipeline with daily aggregation.
        This is the main method to call for collecting all required data.
        
        Args:
            location_name: Name of the location (e.g., "Hyderabad")
            target_date: Target date in YYYY-MM-DD format
            country_code: Optional country code (e.g., "IN" for India)
            latitude: Optional latitude coordinate (if provided, skips geocoding)
            longitude: Optional longitude coordinate (if provided, skips geocoding)
            
        Returns:
            Dict with complete dataset ready for blight prediction:
            {
                "location": {...},
                "target_date": "2025-11-10",
                "daily_weather": {...},  # 24-hour aggregated data
                "daily_air_quality": {...},  # 24-hour aggregated data
                "raw_daily": {...},  # Original API daily data
                "metadata": {...}
            }
        """
        # Helper function to send progress updates
        def send_progress(message: str):
            if progress_callback:
                progress_callback(message)
            else:
                print(message)
        
        # Step 1: Get coordinates - use provided coordinates if available, otherwise geocode
        if latitude is not None and longitude is not None:
            # Use provided coordinates directly - no geocoding needed
            send_progress(f"\nUsing provided coordinates for {location_name}...")
            send_progress(f"Coordinates: {latitude}, {longitude}")
            
            # Get timezone and elevation from coordinates (reverse geocode for metadata only)
            # For now, use "auto" timezone and 0 elevation - Open-Meteo will handle timezone
            location = {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "elevation": 0,  # Will be fetched from weather API if needed
                "timezone": "auto",  # Open-Meteo will auto-detect
                "city": location_name.split(',')[0].strip() if location_name else "Unknown",
                "country": "",
                "admin1": ""
            }
            
            # Try to get timezone, elevation, and country from coordinates (reverse geocode for metadata)
            try:
                # Use Open-Meteo geocoding to get location metadata
                import requests
                reverse_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                }
                reverse_response = requests.get(self.geocoding_url, params=reverse_params, timeout=5)
                if reverse_response.status_code == 200:
                    reverse_data = reverse_response.json()
                    if "results" in reverse_data and len(reverse_data["results"]) > 0:
                        result = reverse_data["results"][0]
                        location["timezone"] = result.get("timezone", "auto")
                        location["elevation"] = result.get("elevation", 0)
                        location["city"] = result.get("name", location["city"])
                        location["country"] = result.get("country", "")
                        location["admin1"] = result.get("admin1", "")
                        print(f"[INFO] Reverse geocoded: {location['city']}, {location['country']}")
            except Exception as e:
                # If reverse geocoding fails, that's okay - we have coordinates
                print(f"[INFO] Could not reverse geocode for metadata: {e}")
                # Try to infer country from coordinates as fallback
                # UK: latitude 49-61°N, longitude -8 to 2°E (note: negative = West)
                if 49 <= latitude <= 61 and -8 <= longitude <= 2:
                    location["country"] = "United Kingdom"
                # India: latitude 6-37°N, longitude 68-97°E
                elif 6 <= latitude <= 37 and 68 <= longitude <= 97:
                    location["country"] = "India"
                # Default fallback - don't assume any country
                else:
                    print(f"[INFO] Coordinates ({latitude}, {longitude}) don't match known regions")
            
            send_progress(f"Location: {location['city']}, {location['country']}")
            send_progress(f"Timezone: {location['timezone']}")
            if location['elevation']:
                send_progress(f"Elevation: {location['elevation']}m")
        else:
            # Geocode location name to get coordinates
            send_progress(f"\nGetting coordinates for {location_name}...")
            location = self.get_location_coordinates(location_name, country_code)
            send_progress(f"Found: {location['city']}, {location['country']}")
            send_progress(f"Coordinates: {location['latitude']}, {location['longitude']}")
            send_progress(f"Elevation: {location['elevation']}m")
            send_progress(f"Timezone: {location['timezone']}")

        # Step 2: Get comprehensive weather data
        weather_data = self.get_comprehensive_weather_data(
            location['latitude'],
            location['longitude'],
            target_date,
            location['timezone'],
            progress_callback=progress_callback
        )

        # Step 3: Get air quality data
        air_quality_data = self.get_air_quality_data(
            location['latitude'],
            location['longitude'],
            target_date,
            location['timezone']
        )

        # Step 4: Extract sliding window
        window_data = self._extract_window(weather_data, target_date)
        air_quality_window = self._extract_air_quality_window(air_quality_data, target_date)

        # Step 5: Aggregate hourly to daily (24-hour periods)
        send_progress("\nAggregating hourly data into daily 24-hour summaries...")
        daily_aggregated_weather = self._aggregate_hourly_to_daily(window_data.get('hourly', {}))
        daily_aggregated_air = self._aggregate_hourly_to_daily(air_quality_window.get('hourly', {}))

        send_progress(f"[OK] Created {len(daily_aggregated_weather.get('date', []))} daily weather summaries")
        send_progress(f"[OK] Created {len(daily_aggregated_air.get('date', []))} daily air quality summaries")

        return {
            "location": location,
            "target_date": target_date,
            "daily_weather": daily_aggregated_weather,  # 24-hour aggregated data
            "daily_air_quality": daily_aggregated_air,  # 24-hour aggregated data
            "raw_daily": window_data.get('daily', {}),  # Original API daily data
            "metadata": {
                "collection_time": datetime.now().isoformat(),
                "total_days": len(daily_aggregated_weather.get('date', [])),
                "expected_days": 8
            }
        }

    def print_summary(self, dataset: Dict):
        """
        Print comprehensive summary showing ONLY daily data (one entry per day).
        
        Args:
            dataset: Dataset returned from collect_complete_dataset()
        """
        print(f"\n{'='*70}")
        print(f"BLIGHT PREDICTION DATA - DAILY SUMMARIES (24-Hour Periods)")
        print(f"{'='*70}")
        print(f"Location: {dataset['location']['city']}, {dataset['location']['country']}")
        print(f"Target Date: {dataset['target_date']}")
        print(f"Elevation: {dataset['location']['elevation']}m")
        print(f"Total Days: {dataset['metadata']['total_days']}")

        daily_weather = dataset['daily_weather']
        daily_air = dataset['daily_air_quality']

        print(f"\n{'='*70}")
        print("DAILY WEATHER DATA (8-Day Window)")
        print(f"{'='*70}")

        def safe_get(data_dict, key, index, default="N/A"):
            """Safely get value from dict at index, return default if missing"""
            if key in data_dict and index < len(data_dict[key]):
                val = data_dict[key][index]
                return val if val is not None else default
            return default

        for i, date in enumerate(daily_weather.get('date', [])):
            marker = " [TARGET DAY]" if date == dataset['target_date'] else ""
            print(f"\n[Date] {date}{marker}")
            print("-" * 70)

            # Temperature
            temp_mean = safe_get(daily_weather, 'temperature_2m_mean', i)
            temp_min = safe_get(daily_weather, 'temperature_2m_min', i)
            temp_max = safe_get(daily_weather, 'temperature_2m_max', i)
            if temp_mean != "N/A":
                print(f"  [Temp] Temperature: {temp_min:.1f}C - {temp_max:.1f}C (avg: {temp_mean:.1f}C)")

            # Humidity
            hum_mean = safe_get(daily_weather, 'relative_humidity_2m_mean', i)
            hum_min = safe_get(daily_weather, 'relative_humidity_2m_min', i)
            hum_max = safe_get(daily_weather, 'relative_humidity_2m_max', i)
            if hum_mean != "N/A":
                print(f"  [Humidity] Humidity: {hum_min:.0f}% - {hum_max:.0f}% (avg: {hum_mean:.0f}%)")

            # Precipitation
            precip = safe_get(daily_weather, 'precipitation_sum', i)
            if precip != "N/A":
                print(f"  [Rain] Total Precipitation: {precip:.1f} mm")

            # Wind
            wind_mean = safe_get(daily_weather, 'wind_speed_10m_mean', i)
            wind_max = safe_get(daily_weather, 'wind_speed_10m_max', i)
            if wind_mean != "N/A":
                print(f"  [Wind] Wind Speed: avg {wind_mean:.1f} km/h, max {wind_max:.1f} km/h")

            # Soil Temperature
            soil_temp = safe_get(daily_weather, 'soil_temperature_0_to_7cm_mean', i)
            if soil_temp != "N/A":
                print(f"  [Soil] Soil Temp (0-7cm): {soil_temp:.1f}C")

            # Soil Moisture
            soil_moist = safe_get(daily_weather, 'soil_moisture_0_to_7cm_mean', i)
            if soil_moist != "N/A":
                print(f"  [Moisture] Soil Moisture (0-7cm): {soil_moist:.3f} m3/m3")

            # Cloud Cover
            clouds = safe_get(daily_weather, 'cloud_cover_mean', i)
            if clouds != "N/A":
                print(f"  [Clouds] Cloud Cover: {clouds:.0f}%")

            # Solar Radiation
            solar = safe_get(daily_weather, 'shortwave_radiation_sum', i)
            if solar != "N/A":
                print(f"  [Solar] Solar Radiation: {solar:.0f} Wh/m2")

            # Air Quality (if available for this day)
            if i < len(daily_air.get('date', [])):
                pm25 = safe_get(daily_air, 'pm2_5_mean', i)
                if pm25 != "N/A":
                    print(f"  [PM2.5] PM2.5: {pm25:.1f} ug/m3")

                o3 = safe_get(daily_air, 'ozone_mean', i)
                if o3 != "N/A":
                    print(f"  [Ozone] Ozone: {o3:.1f} ug/m3")

                uv = safe_get(daily_air, 'uv_index_max', i)
                if uv != "N/A":
                    print(f"  [UV] Max UV Index: {uv:.1f}")

        print(f"\n{'='*70}")
        print("[OK] Data collection complete - ready for blight prediction!")
        print(f"{'='*70}\n")


class BlightPredictionAgent:
    """
    Enhanced weather-based blight prediction agent for potato crops.
    Supports both India and UK with climate-specific configurations.
    Uses OpenAI to analyze weather data against crop management guidelines.
    Integrates seamlessly with ComprehensiveBlightDataCollector output.
    Automatically extracts location and sowing date from user profile.
    """
    
    def __init__(self):
        """Initialize the blight prediction agent with OpenAI LLM."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1500
        )
        self.llm_judge = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            max_tokens=2000
        )
        self.translation_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )  # For translations
        # Initialize climate-specific configurations
        self._init_climate_configs()
        # Store system prompts for reuse
        self._system_prompts = {}

    def _init_climate_configs(self):
        """Initialize climate-specific growth stage and disease configurations."""
        # India configuration (existing)
        self.INDIA_CONFIG = {
            'growth_stages': {
                'sowing_germination': {'dap_range': (0, 15), 'calendar': 'Late Nov-Early Dec (Weeks 46-49)',
                    'ideal': {'temp_max': (25, 30), 'temp_min': (11, 15), 'rh': (60, 70), 'rain': '<10mm'},
                    'risks': ['Heavy rain → seed rot', 'Temp >30°C → poor sprouting', 'Prolonged dryness → poor emergence'],
                    'advisory': ['Prepare raised beds for drainage', 'Use certified treated seed', 'Apply light irrigation post-planting']},
                'vegetative': {'dap_range': (15, 45), 'calendar': 'Dec-Early Jan (Weeks 50-2)',
                    'ideal': {'temp_max': (24, 26), 'temp_min': (7, 9), 'rh': (70, 80), 'rain': '25-35mm/week'},
                    'risks': ['Cloudy + high humidity (>85%) → Late Blight', 'Low temp (<8°C) → frost', 'Dry + warm → aphids'],
                    'advisory': ['Regular irrigation at 7-10-day intervals', 'Monitor RH and dew periods', 'Apply first preventive fungicide if prolonged humidity']},
                'tuber_initiation': {'dap_range': (45, 60), 'calendar': 'Jan (Weeks 3-5)',
                    'ideal': {'temp_max': (20, 22), 'temp_min': (8, 10), 'rh': (75, 85), 'rain': '<25mm/week'},
                    'risks': ['Fog + high humidity + min temp 8-10°C → HIGH Late Blight risk', 'Prolonged cloudy → low photosynthesis', 'Overwatering → tuber rot'],
                    'advisory': ['Maintain soil moisture at 70-80% field capacity', 'Use contact fungicides (Mancozeb)', 'Ensure drainage']},
                'tuber_bulking': {'dap_range': (60, 90), 'calendar': 'Late Jan-Feb (Weeks 6-8)',
                    'ideal': {'temp_max': (18, 22), 'temp_min': (7, 9), 'rh': (70, 80), 'rain': '<15mm/week'},
                    'risks': ['Foggy + cloudy + humidity >85% → Late Blight spread', 'High pH (>6.5) → Common Scab', 'High winds (>30 km/h) → spore spread'],
                    'advisory': ['Continue systemic fungicide if conditions persist', 'Maintain balanced irrigation', 'Apply potassium-rich fertilizer']},
                'maturity': {'dap_range': (90, 110), 'calendar': 'Mid-Late Feb (Weeks 9-10)',
                    'ideal': {'temp_max': (25, 27), 'temp_min': (10, 12), 'rh': '<70%', 'rain': '<10mm'},
                    'risks': ['High humidity/dew nights → Early Blight', 'Late rainfall → delayed maturity', 'Hailstorm → foliage damage'],
                    'advisory': ['Reduce irrigation gradually', 'Spray protective fungicide before haulm cutting', 'Plan harvest 10-12 days post-haulm cutting']},
                'harvest': {'dap_range': (110, 130), 'calendar': 'Late Feb-March (Weeks 11-12)',
                    'ideal': {'temp_max': '<25', 'temp_min': None, 'rh': 'Low', 'rain': 'Nil'},
                    'risks': ['Wet harvest → storage rot', 'High PM2.5 → airborne fungal spores', 'Excess heat in storage (>10°C) → sprouting'],
                    'advisory': ['Harvest on clear, dry days', 'Cure tubers at 15-20°C for 10 days', 'Store at 4°C & RH 90-95%']}
            },
            'hutton_criteria': None,  # Not used for India
            'fungicides': ['Mancozeb', 'Metalaxyl', 'Copper oxychloride', 'Cymoxanil']
        }

        # UK configuration (based on research)
        self.UK_CONFIG = {
            'growth_stages': {
                'sowing_germination': {'dap_range': (0, 20), 'calendar': 'Mid-Apr to Early May (Weeks 15-18)',
                    'ideal': {'temp_max': (18, 22), 'temp_min': (8, 12), 'rh': (65, 75), 'rain': '10-20mm/week'},
                    'risks': ['Cold soil (<8°C) → poor emergence', 'Heavy rain → seed rot', 'Frost → crop damage'],
                    'advisory': ['Plant when soil temp >8°C', 'Use certified seed', 'Protect from late frosts']},
                'vegetative': {'dap_range': (21, 50), 'calendar': 'May-Early Jun (Weeks 19-22)',
                    'ideal': {'temp_max': (20, 24), 'temp_min': (10, 14), 'rh': (70, 80), 'rain': '20-30mm/week'},
                    'risks': ['Hutton Criteria met → Late Blight risk', 'Cool + wet → disease pressure', 'High humidity (>90%) → blight initiation'],
                    'advisory': ['Monitor Hutton Criteria daily', 'Apply preventive fungicide if criteria met', 'Maintain good field drainage']},
                'flowering': {'dap_range': (51, 75), 'calendar': 'Jun-Early Jul (Weeks 23-26)',
                    'ideal': {'temp_max': (18, 22), 'temp_min': (12, 16), 'rh': (70, 80), 'rain': '15-25mm/week'},
                    'risks': ['Hutton Criteria → HIGH Late Blight risk', 'Warm + humid → disease spread', 'Wind + rain → spore dispersal'],
                    'advisory': ['Intensive fungicide program if Hutton Criteria active', 'Systemic fungicides (fluazinam, propamocarb)', 'Monitor weather forecasts']},
                'tuber_formation': {'dap_range': (76, 105), 'calendar': 'Jul-Aug (Weeks 27-30)',
                    'ideal': {'temp_max': (20, 24), 'temp_min': (14, 18), 'rh': (70, 80), 'rain': '15-25mm/week'},
                    'risks': ['Hutton Criteria → Late Blight on tubers', 'High humidity → tuber blight', 'Wet conditions → secondary infections'],
                    'advisory': ['Continue fungicide protection', 'Ensure good soil drainage', 'Monitor for tuber blight symptoms']},
                'maturity': {'dap_range': (106, 140), 'calendar': 'Aug-Sep (Weeks 31-34)',
                    'ideal': {'temp_max': (18, 22), 'temp_min': (12, 16), 'rh': '<75%', 'rain': '<15mm/week'},
                    'risks': ['Late blight → tuber infection', 'Wet harvest → storage diseases', 'Early blight in warm periods'],
                    'advisory': ['Desiccate haulms before harvest', 'Harvest in dry conditions', 'Cure properly before storage']},
                'harvest': {'dap_range': (140, 180), 'calendar': 'Sep-Oct (Weeks 35-40)',
                    'ideal': {'temp_max': '<20', 'temp_min': None, 'rh': '<70%', 'rain': 'Minimal'},
                    'risks': ['Wet harvest → storage rot', 'Bruising → disease entry', 'Poor curing → storage losses'],
                    'advisory': ['Harvest in dry weather', 'Handle carefully to avoid bruising', 'Cure at 10-15°C, RH 85-90%', 'Store at 3-4°C, RH 90-95%']}
            },
            'hutton_criteria': {
                'description': 'Two consecutive days with min temp >=10°C AND at least 6 hours RH >=90%',
                'risk_level': 'high',
                'action': 'Immediate fungicide application recommended'
            },
            'fungicides': ['Fluazinam', 'Propamocarb', 'Mandipropamid', 'Cymoxanil', 'Fenamidone']
        }

    def _extract_user_data(self, state: AgentState) -> Dict[str, Any]:
        """
        Extract location and sowing date from user profile in state.
        This ensures data flows from first page through all layers.
        
        Args:
            state: AgentState with user_profile
            
        Returns:
            Dict with location, sowing_date, country, latitude, longitude, and calculated DAP
        """
        user_profile = state.get("user_profile", {})
        fields = user_profile.get("fields", [])
        
        # Get current field (first field or current_field_id)
        current_field_id = state.get("conversation", {}).get("current_field_id")
        current_field = None
        
        if current_field_id:
            current_field = next((f for f in fields if f.get("field_id") == current_field_id), None)
        
        if not current_field and fields:
            current_field = fields[0]
        
        location = current_field.get("location", "") if current_field else ""
        sowing_date_str = current_field.get("sowing_date", "") if current_field else ""
        
        # Extract latitude and longitude if available
        latitude = current_field.get("latitude") if current_field else None
        longitude = current_field.get("longitude") if current_field else None
        
        # Validate coordinates
        if latitude is not None:
            try:
                latitude = float(latitude)
                if not (-90 <= latitude <= 90):
                    latitude = None
            except (ValueError, TypeError):
                latitude = None
        
        if longitude is not None:
            try:
                longitude = float(longitude)
                if not (-180 <= longitude <= 180):
                    longitude = None
            except (ValueError, TypeError):
                longitude = None
        
        # Calculate DAP
        days_after_planting = None
        if sowing_date_str:
            try:
                sowing_date = datetime.strptime(sowing_date_str, "%Y-%m-%d")
                days_after_planting = (datetime.now() - sowing_date).days
            except:
                pass
        
        # Detect country from location, coordinates, or use default
        country = self._detect_country(location, state, latitude, longitude)
        
        return {
            "location": location,
            "sowing_date": sowing_date_str,
            "days_after_planting": days_after_planting,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "field_data": current_field
        }

    def _detect_country(self, location: str, state: AgentState, latitude: Optional[float] = None, longitude: Optional[float] = None) -> str:
        """
        Detect country from location string, coordinates, or weather dataset.
        
        Args:
            location: Location string
            state: AgentState
            latitude: Optional latitude coordinate
            longitude: Optional longitude coordinate
            
        Returns:
            "UK" or "India" (default)
        """
        location_lower = location.lower() if location else ""
        
        # Priority 1: Check weather dataset for country (most reliable)
        weather_dataset = state.get("weather_dataset")
        if weather_dataset:
            location_data = weather_dataset.get("location", {})
            country = location_data.get("country", "").lower()
            if "united kingdom" in country or "uk" in country or "britain" in country or "england" in country:
                return "UK"
            if "india" in country:
                return "India"
        
        # Priority 2: Use coordinates to detect country (UK is roughly 49-61°N, 8°W-2°E)
        if latitude is not None and longitude is not None:
            # UK coordinates: roughly 49-61°N, 8°W-2°E
            if 49 <= latitude <= 61 and -8 <= longitude <= 2:
                return "UK"
            # India coordinates: roughly 6-37°N, 68-97°E
            elif 6 <= latitude <= 37 and 68 <= longitude <= 97:
                return "India"
        
        # Priority 3: Check location string for UK indicators
        uk_indicators = ["uk", "united kingdom", "britain", "england", "scotland", "wales", "northern ireland",
                        "london", "edinburgh", "manchester", "birmingham", "glasgow", "liverpool", "coventry",
                        "bristol", "leeds", "sheffield", "leicester", "nottingham", "newcastle"]
        if any(indicator in location_lower for indicator in uk_indicators):
            return "UK"
        
        # Priority 4: Check for India indicators
        india_indicators = ["india", "delhi", "mumbai", "bangalore", "hyderabad", "chennai", "kolkata",
                           "pune", "ahmedabad", "jaipur", "lucknow", "kanpur", "nagpur", "indore"]
        if any(indicator in location_lower for indicator in india_indicators):
            return "India"
        
        # No default - return None and let geocoding API determine it
        return None

    def _check_hutton_criteria(self, weather_dataset: Dict) -> Dict:
        """
        Check UK Hutton Criteria for Late Blight risk.
        Criteria: Two consecutive days with min temp >=10°C AND at least 6 hours RH >=90%
        
        Args:
            weather_dataset: Weather dataset from collector
            
        Returns:
            Dict with hutton_criteria status and details
        """
        daily_weather = weather_dataset.get("daily_weather", {})
        dates = daily_weather.get("date", [])
        
        if not dates or len(dates) < 2:
            return {"met": False, "consecutive_days": 0, "details": []}
        
        consecutive_days = 0
        criteria_details = []
        
        for i in range(len(dates) - 1):
            # Get min temp and humidity data for day i and i+1
            temp_min_i = self._safe_get_value(daily_weather, "temperature_2m_min", i)
            temp_min_next = self._safe_get_value(daily_weather, "temperature_2m_min", i + 1)
            hum_mean_i = self._safe_get_value(daily_weather, "relative_humidity_2m_mean", i)
            hum_mean_next = self._safe_get_value(daily_weather, "relative_humidity_2m_mean", i + 1)
            
            # Simplified check: if both days have min temp >=10 and high humidity
            # Note: We'd need hourly data for exact 6-hour check, but daily mean >90% is a good proxy
            if (temp_min_i is not None and temp_min_i >= 10 and 
                temp_min_next is not None and temp_min_next >= 10 and
                hum_mean_i is not None and hum_mean_i >= 90 and
                hum_mean_next is not None and hum_mean_next >= 90):
                
                consecutive_days += 1
                criteria_details.append({
                    "date_pair": [dates[i], dates[i + 1]],
                    "day1": {"temp_min": temp_min_i, "humidity": hum_mean_i},
                    "day2": {"temp_min": temp_min_next, "humidity": hum_mean_next}
                })
        
        met = consecutive_days >= 1  # At least one pair of consecutive days
        
        return {
            "met": met,
            "consecutive_days": consecutive_days,
            "details": criteria_details,
            "risk_level": "high" if met else "low",
            "action_required": met
        }

    def _safe_get_value(self, data_dict: Dict, key: str, index: int):
        """Safely get numeric value from dict at index."""
        if key in data_dict and index < len(data_dict[key]):
            val = data_dict[key][index]
            return float(val) if val is not None else None
        return None

    def _get_system_prompt(self, country: str = "India") -> str:
        """Get climate-specific system prompt for blight prediction."""
        if country in self._system_prompts:
            return self._system_prompts[country]
        
        if country == "UK":
            prompt = self._get_uk_system_prompt()
        else:
            prompt = self._get_india_system_prompt()
        
        self._system_prompts[country] = prompt
        return prompt

    def _get_india_system_prompt(self) -> str:
        """Get system prompt for Indian growing conditions with streaming behavior."""
        return """You are an expert agricultural meteorologist and plant pathologist specializing in potato blight prediction for Indian growing conditions.

STREAMING BEHAVIOR:
Analyze weather data step-by-step and communicate what you're doing naturally. Do not mention progress, loading, or percentages. Instead, describe what you're analyzing in conversational language like "Analyzing current weather conditions..." or "Evaluating disease risk patterns...". Stream your outputs in stages as you complete each subtask, with each section being complete and self-contained.

**POTATO CROP GROWTH STAGES & BLIGHT RISK ASSESSMENT:**

**GROWTH STAGES:**
1. **Sowing & Germination (0-15 DAP)**: Late Nov-Early Dec
   - Ideal: Max 25-30°C, Min 11-15°C, RH 60-70%, <10mm rain
   - Risk: Heavy rain → seed rot, Temp >30°C → poor sprouting

2. **Vegetative Growth (15-45 DAP)**: Dec-Early Jan  
   - Ideal: Max 24-26°C, Min 7-9°C, RH 70-80%, 25-35mm/week rain
   - **LATE BLIGHT RISK**: Cloudy + high humidity (>85%) → Late Blight initiation
   - Risk: Low temp (<8°C) → frost, Dry+warm → aphids

3. **Tuber Initiation (45-60 DAP)**: January
   - Ideal: Max 20-22°C, Min 8-10°C, RH 75-85%, <25mm/week rain
   - **HIGH LATE BLIGHT RISK**: Fog + high humidity + min temp 8-10°C → CRITICAL PERIOD
   - Risk: Overwatering → tuber rot

4. **Tuber Bulking (60-90 DAP)**: Late Jan-Feb
   - Ideal: Max 18-22°C, Min 7-9°C, RH 70-80%, <15mm/week rain
   - **LATE BLIGHT SPREAD**: Foggy + cloudy + humidity >85% → rapid spread
   - Risk: High winds >30 km/h → spore spread

5. **Maturity (90-110 DAP)**: Mid-Late Feb
   - Ideal: Max 25-27°C, Min 10-12°C, RH <70%, <10mm rain
   - **EARLY BLIGHT RISK**: High humidity/dew nights → Early Blight

6. **Harvest (110-130 DAP)**: Late Feb-March
   - Ideal: <25°C, no rain, low RH
   - Risk: Wet harvest → storage rot

**BLIGHT DISEASE CRITERIA:**

**LATE BLIGHT (Phytophthora infestans)** - Most Critical:
- **HIGH RISK Triggers:**
  * Min temp 8-12°C + Max temp 18-22°C + RH >85% for extended periods
  * Fog/mist + cloud cover >70% + RH >80%
  * High PM2.5 (>50 µg/m³) + humidity >85% (spore dispersal)
  * Wind speed 5-15 km/h (optimal spore spread)
  * Soil moisture >0.120 m³/m³ + high humidity
- **MEDIUM RISK:**
  * RH 75-85% + cloudy weather (>50% cloud cover) + temps 18-25°C
  * Light rain (<5mm/day) + overcast conditions
  * PM2.5 30-50 µg/m³ with moderate humidity
- **LOW RISK:**
  * RH <70%, sunny (cloud cover <30%), dry conditions
  * Temp >28°C or <7°C
  * Very low humidity + high solar radiation

**EARLY BLIGHT (Alternaria solani)**:
- **HIGH RISK Triggers:**
  * Warm days (25-30°C) + cool nights (10-15°C) + RH 70-90%
  * Dew formation (check dew point close to min temp)
  * Older leaves + water stress periods
  * Later growth stages (90+ DAP)
  * High UV index (>7) + moderate humidity
- **MEDIUM RISK:**
  * RH 60-70% + warm temperatures (23-28°C)
  * Intermittent dry/wet periods
  * Moderate UV exposure
- **LOW RISK:**
  * Consistent humidity, very dry (<50% RH) or very wet conditions
  * Cool temperatures throughout day

**YOUR ANALYSIS TASK (STREAM IN STAGES):**

Work through your analysis step-by-step and communicate naturally:

1. **Stage 1 - Weather & Field Information**: 
   - Examine the 8-day weather window carefully - analyze EACH day's conditions
   - Summarize current weather conditions, location, elevation, and forecast window
   - Communicate: "Analyzing current weather conditions for your field..."

2. **Stage 2 - Risk Assessment**:
   - Identify the growth stage based on DAP and match against critical periods
   - Assess Late Blight risk (primary concern for Indian conditions)
   - Assess Early Blight risk (secondary concern)
   - Communicate: "Evaluating disease risk patterns based on temperature and humidity..."

3. **Stage 3 - Environmental Analysis**:
   - Evaluate air quality impact (PM2.5, ozone on spore dispersal)
   - Consider soil conditions (moisture, temperature for pathogen activity)
   - Communicate: "Reviewing environmental factors that influence disease development..."

4. **Stage 4 - Recommendations**:
   - Provide actionable recommendations specific to Indian farming practices
   - Include specific fungicides, dosages, and timing
   - Communicate: "Generating preventive and curative recommendations..."

5. **Stage 5 - Historical Context** (if available):
   - Compare current conditions with historical outbreaks
   - Communicate: "Comparing historical outbreaks with current conditions..."

**CRITICAL: Analyze ACTUAL VALUES from the data. Do not make generic statements.**
**IMPORTANT: Do NOT mention progress percentages, loading states, or step counters. Use natural language to describe what you're analyzing.**

**Respond in this EXACT JSON format:**

{
    "growth_stage": "Stage name",
    "days_after_planting": 30,
    "location": "Location name",
    "analysis_date": "2025-11-10",
    
    "late_blight_risk": {
        "risk_level": "high" | "medium" | "low" | "none",
        "risk_percentage": 85,
        "peak_risk_days": ["2025-11-10", "2025-11-11"],
        "key_risk_factors": [
            "Specific weather condition 1 with actual values",
            "Specific weather condition 2 with actual values"
        ],
        "weather_summary": "Summary of conditions favoring Late Blight with specific data points"
    },
    
    "early_blight_risk": {
        "risk_level": "high" | "medium" | "low" | "none",
        "risk_percentage": 40,
        "peak_risk_days": ["2025-11-12"],
        "key_risk_factors": ["Factor 1 with values", "Factor 2 with values"],
        "weather_summary": "Summary of conditions favoring Early Blight with specific data"
    },
    
    "overall_disease_pressure": "critical" | "high" | "moderate" | "low" | "minimal",
    
    "critical_weather_observations": [
        "Nov 10: Specific observation with exact values (temp, humidity, etc.)",
        "Nov 11: Specific observation with exact values"
    ],
    
    "air_quality_impact": {
        "pm25_concern": "high" | "moderate" | "low",
        "pm25_values": "Range of PM2.5 values observed",
        "impact_on_disease": "How air quality affects disease spread with specific mechanism"
    },
    
    "soil_conditions_analysis": {
        "moisture_status": "optimal | too_wet | too_dry",
        "soil_temp_range": "Temperature range observed",
        "impact_on_disease": "How soil conditions affect pathogen"
    },
    
    "immediate_actions": [
        "Urgent action 1 with specific timing (if high risk)",
        "Urgent action 2 with specific product/method"
    ],
    
    "preventive_recommendations": [
        "Fungicide recommendation with timing and application method",
        "Irrigation management with specific schedule",
        "Field monitoring advice with what to look for"
    ],
    
    "weekly_outlook": "Summary of disease risk for next 7 days with specific dates",
    
    "confidence_level": "high" | "medium" | "low",
    "confidence_explanation": "Why this confidence level based on data quality and weather pattern clarity",
    
    "visualization_data": {
        "risk_matrix": {
            "probability": 85,
            "impact": "high",
            "risk_score": 85
        },
        "risk_factor_contributions": {
            "temperature": {"value": 25, "weight": 0.3, "contribution": 7.5},
            "humidity": {"value": 90, "weight": 0.4, "contribution": 36.0},
            "precipitation": {"value": 15, "weight": 0.15, "contribution": 2.25},
            "wind": {"value": 8, "weight": 0.1, "contribution": 0.8},
            "cloud_cover": {"value": 75, "weight": 0.05, "contribution": 3.75}
        },
        "calculation_methodology": "Risk score calculated as weighted sum of normalized factors. Temperature optimal range 10-25°C (risk increases outside), Humidity critical above 85% (weighted 0.4), Precipitation adds risk above 5mm (weighted 0.15), Low wind (<10 km/h) increases spore retention (weighted 0.1), High cloud cover (>70%) indicates prolonged humidity (weighted 0.05)."
    }
}

**IMPORTANT:**
- Base predictions on SPECIFIC weather values from the data
- Reference actual dates and measurements (e.g., "Nov 10: RH 91%, Temp 15.1°C")
- Consider the phenological stage - risks vary by growth stage
- Provide ACTIONABLE advice suitable for Indian farming context
- Mention specific fungicides used in India (Mancozeb, Metalaxyl, Copper oxychloride, Cymoxanil)
- Consider fog, dew, and monsoon patterns common in India
- Be honest about uncertainty - weather prediction has limits
- **GENERATE DYNAMIC VISUALIZATION DATA**: Include risk_matrix, risk_factor_contributions, and calculation_methodology in your response
- Each visualization should reflect the SPECIFIC risk factors identified for this prediction
- Make the methodology transparent so users understand how risk scores are calculated"""

    def _get_uk_system_prompt(self) -> str:
        """Get system prompt for UK growing conditions with Hutton Criteria and streaming behavior."""
        return """You are an expert agricultural meteorologist and plant pathologist specializing in potato blight prediction for UK growing conditions.

STREAMING BEHAVIOR:
Analyze weather data step-by-step and communicate what you're doing naturally. Do not mention progress, loading, or percentages. Instead, describe what you're analyzing in conversational language like "Checking Hutton Criteria..." or "Evaluating disease risk patterns...". Stream your outputs in stages as you complete each subtask, with each section being complete and self-contained.

**POTATO CROP GROWTH STAGES & BLIGHT RISK ASSESSMENT (UK):**

**GROWTH STAGES:**
1. **Sowing & Germination (0-20 DAP)**: Mid-Apr to Early May (Weeks 15-18)
   - Ideal: Max 18-22°C, Min 8-12°C, RH 65-75%, 10-20mm/week rain
   - Risk: Cold soil (<8°C) → poor emergence, Heavy rain → seed rot, Frost → crop damage

2. **Vegetative Growth (21-50 DAP)**: May-Early Jun (Weeks 19-22)
   - Ideal: Max 20-24°C, Min 10-14°C, RH 70-80%, 20-30mm/week rain
   - **LATE BLIGHT RISK**: Hutton Criteria met → Late Blight risk, Cool + wet → disease pressure
   - Risk: High humidity (>90%) → blight initiation

3. **Flowering (51-75 DAP)**: Jun-Early Jul (Weeks 23-26)
   - Ideal: Max 18-22°C, Min 12-16°C, RH 70-80%, 15-25mm/week rain
   - **HIGH LATE BLIGHT RISK**: Hutton Criteria → HIGH Late Blight risk, Warm + humid → disease spread
   - Risk: Wind + rain → spore dispersal

4. **Tuber Formation (76-105 DAP)**: Jul-Aug (Weeks 27-30)
   - Ideal: Max 20-24°C, Min 14-18°C, RH 70-80%, 15-25mm/week rain
   - **LATE BLIGHT ON TUBERS**: Hutton Criteria → Late Blight on tubers, High humidity → tuber blight
   - Risk: Wet conditions → secondary infections

5. **Maturity (106-140 DAP)**: Aug-Sep (Weeks 31-34)
   - Ideal: Max 18-22°C, Min 12-16°C, RH <75%, <15mm/week rain
   - **LATE BLIGHT RISK**: Late blight → tuber infection, Wet harvest → storage diseases
   - Risk: Early blight in warm periods

6. **Harvest (140-180 DAP)**: Sep-Oct (Weeks 35-40)
   - Ideal: <20°C, Low RH, Minimal rain
   - Risk: Wet harvest → storage rot, Bruising → disease entry

**HUTTON CRITERIA FOR LATE BLIGHT (UK Standard):**
- **CRITICAL RISK**: Two consecutive days with:
  * Minimum temperature >= 10°C
  * At least 6 hours of relative humidity >= 90%
- When Hutton Criteria are met, immediate fungicide application is recommended
- This is the UK's official blight warning system

**LATE BLIGHT (Phytophthora infestans)** - Primary Concern:
- **HIGH RISK Triggers:**
  * Hutton Criteria met (two consecutive days: min temp >=10°C + 6+ hours RH >=90%)
  * Cool temperatures (10-20°C) + high humidity (>90%)
  * Prolonged leaf wetness (>10 hours)
  * Wind speed 5-15 km/h (spore dispersal)
  * Rainfall + high humidity combination
- **MEDIUM RISK:**
  * Single day meeting Hutton Criteria
  * RH 85-90% + cool temps (12-18°C)
  * Moderate rainfall + overcast conditions
- **LOW RISK:**
  * RH <85%, sunny conditions
  * Temp <8°C or >25°C
  * Dry conditions with low humidity

**EARLY BLIGHT (Alternaria solani)**:
- **HIGH RISK Triggers:**
  * Warm days (20-25°C) + cool nights (10-15°C) + RH 70-90%
  * Dew formation periods
  * Later growth stages (100+ DAP)
  * Moderate humidity + warm spells
- **MEDIUM RISK:**
  * RH 65-75% + warm temperatures (18-22°C)
  * Intermittent wet/dry periods
- **LOW RISK:**
  * Cool, consistent conditions
  * Very dry or very wet conditions

**YOUR ANALYSIS TASK (STREAM IN STAGES):**

Work through your analysis step-by-step and communicate naturally:

1. **Stage 1 - Weather & Field Information**: 
   - Check Hutton Criteria FIRST - This is critical for UK predictions
   - Examine the 8-day weather window - analyze EACH day's conditions
   - Summarize current weather conditions, location, elevation, and forecast window
   - Communicate: "Checking Hutton Criteria and analyzing current weather conditions..."

2. **Stage 2 - Risk Assessment**:
   - Identify the growth stage based on DAP and match against critical periods
   - Assess Late Blight risk (primary concern, especially if Hutton Criteria met)
   - Assess Early Blight risk (secondary concern)
   - Communicate: "Evaluating disease risk patterns based on Hutton Criteria and weather conditions..."

3. **Stage 3 - Environmental Analysis**:
   - Evaluate environmental factors (temperature, humidity, rainfall, wind)
   - Consider soil conditions (moisture, temperature)
   - Communicate: "Reviewing environmental factors that influence disease development..."

4. **Stage 4 - Recommendations**:
   - Provide actionable recommendations specific to UK farming practices
   - Include specific fungicides, dosages, and timing
   - Communicate: "Generating preventive and curative recommendations..."

5. **Stage 5 - Historical Context** (if available):
   - Compare current conditions with historical outbreaks
   - Communicate: "Comparing historical outbreaks with current conditions..."

**CRITICAL: Analyze ACTUAL VALUES from the data. Do not make generic statements.**
**IMPORTANT: Do NOT mention progress percentages, loading states, or step counters. Use natural language to describe what you're analyzing.**

**Respond in this EXACT JSON format:**

{
    "growth_stage": "Stage name",
    "days_after_planting": 30,
    "location": "Location name",
    "analysis_date": "2025-11-10",
    "hutton_criteria_met": true | false,
    "hutton_criteria_details": "Description if met",
    
    "late_blight_risk": {
        "risk_level": "high" | "medium" | "low" | "none",
        "risk_percentage": 85,
        "peak_risk_days": ["2025-11-10", "2025-11-11"],
        "key_risk_factors": [
            "Hutton Criteria met on Nov 10-11: min temp 11°C, RH 92% for 8 hours",
            "Specific weather condition 2 with actual values"
        ],
        "weather_summary": "Summary of conditions favoring Late Blight with specific data points"
    },
    
    "early_blight_risk": {
        "risk_level": "high" | "medium" | "low" | "none",
        "risk_percentage": 40,
        "peak_risk_days": ["2025-11-12"],
        "key_risk_factors": ["Factor 1 with values", "Factor 2 with values"],
        "weather_summary": "Summary of conditions favoring Early Blight with specific data"
    },
    
    "overall_disease_pressure": "critical" | "high" | "moderate" | "low" | "minimal",
    
    "critical_weather_observations": [
        "Nov 10: Specific observation with exact values (temp, humidity, etc.)",
        "Nov 11: Specific observation with exact values"
    ],
    
    "air_quality_impact": {
        "pm25_concern": "high" | "moderate" | "low",
        "pm25_values": "Range of PM2.5 values observed",
        "impact_on_disease": "How air quality affects disease spread with specific mechanism"
    },
    
    "soil_conditions_analysis": {
        "moisture_status": "optimal | too_wet | too_dry",
        "soil_temp_range": "Temperature range observed",
        "impact_on_disease": "How soil conditions affect pathogen"
    },
    
    "immediate_actions": [
        "Urgent action 1 with specific timing (if high risk)",
        "Urgent action 2 with specific product/method"
    ],
    
    "preventive_recommendations": [
        "Fungicide recommendation with timing and application method",
        "Irrigation management with specific schedule",
        "Field monitoring advice with what to look for"
    ],
    
    "weekly_outlook": "Summary of disease risk for next 7 days with specific dates",
    
    "confidence_level": "high" | "medium" | "low",
    "confidence_explanation": "Why this confidence level based on data quality and weather pattern clarity",
    
    "visualization_data": {
        "risk_matrix": {
            "probability": 85,
            "impact": "high",
            "risk_score": 85
        },
        "risk_factor_contributions": {
            "temperature": {"value": 12, "weight": 0.3, "contribution": 3.6},
            "humidity": {"value": 92, "weight": 0.4, "contribution": 36.8},
            "precipitation": {"value": 8, "weight": 0.15, "contribution": 1.2},
            "wind": {"value": 7, "weight": 0.1, "contribution": 0.7},
            "cloud_cover": {"value": 85, "weight": 0.05, "contribution": 4.25},
            "hutton_criteria": {"met": true, "weight": 0.2, "contribution": 20.0}
        },
        "calculation_methodology": "Risk score calculated as weighted sum of normalized factors. Hutton Criteria (if met) adds significant weight (0.2). Temperature optimal range 10-20°C for Late Blight (weighted 0.3), Humidity critical above 90% for 6+ hours (weighted 0.4), Precipitation adds risk (weighted 0.15), Low wind (<10 km/h) increases spore retention (weighted 0.1), High cloud cover (>70%) indicates prolonged humidity (weighted 0.05)."
    }
}

**IMPORTANT:**
- Base predictions on SPECIFIC weather values from the data
- Reference actual dates and measurements (e.g., "Nov 10: RH 92%, Temp 11°C")
- **ALWAYS check Hutton Criteria first for UK predictions**
- Consider the phenological stage - risks vary by growth stage
- Provide ACTIONABLE advice suitable for UK farming context
- Mention specific fungicides used in UK (Fluazinam, Propamocarb, Mandipropamid, Cymoxanil, Fenamidone)
- Consider UK weather patterns: cool, wet summers; variable conditions
- Be honest about uncertainty - weather prediction has limits
- **GENERATE DYNAMIC VISUALIZATION DATA**: Include risk_matrix, risk_factor_contributions, and calculation_methodology in your response
- Each visualization should reflect the SPECIFIC risk factors identified for this prediction, including Hutton Criteria status
- Make the methodology transparent so users understand how risk scores are calculated"""

    def predict_blight_risk(self, state: AgentState) -> AgentState:
        """
        Enhanced blight risk prediction with automatic user data extraction.
        Automatically extracts location and sowing date from user_profile.
        Supports both India and UK with climate-specific configurations.
        
        Args:
            state: AgentState containing:
                - user_profile: with fields containing location and sowing_date
                - weather_dataset: from ComprehensiveBlightDataCollector (optional, will collect if missing)
                - days_after_planting: (optional, will calculate from sowing_date)
            
        Returns:
            Updated AgentState with blight_prediction and final_report
        """
        # Initialize progress tracking
        if "progress_updates" not in state:
            state["progress_updates"] = []
        if "current_progress" not in state:
            state["current_progress"] = {"step": 0, "total_steps": 12, "progress": 0, "message": "Starting..."}
        
        def update_progress(step: int, message: str, stage: str, progress: int = None):
            """Update progress in state for streaming"""
            if progress is None:
                progress = int((step / 12) * 100)
            state["current_progress"] = {
                "step": step,
                "total_steps": 12,
                "progress": progress,
                "message": message,
                "stage": stage
            }
            if "progress_updates" in state:
                state["progress_updates"].append(state["current_progress"].copy())
        
        # Step 1: Extract user data from profile (location, sowing_date, country, coordinates)
        update_progress(1, "Extracting field information...", "extract_data", 8)
        user_data = self._extract_user_data(state)
        location = user_data.get("location")
        sowing_date = user_data.get("sowing_date")
        country = user_data.get("country", "India")
        days_after_planting = user_data.get("days_after_planting")
        latitude = user_data.get("latitude")
        longitude = user_data.get("longitude")
        
        # Step 2: Get or use existing weather dataset
        update_progress(2, f"Fetching weather data for {location}...", "collect_weather", 15)
        weather_dataset = state.get("weather_dataset")
        
        # If no weather dataset but we have location, collect it
        if not weather_dataset and location:
            print(f"[INFO] Collecting weather data for {location}...")
            if latitude is not None and longitude is not None:
                print(f"[INFO] Using provided coordinates: {latitude}, {longitude}")
            else:
                print(f"[INFO] Geocoding location name: {location}")
            
            collector = ComprehensiveBlightDataCollector()
            target_date = datetime.now().strftime("%Y-%m-%d")
            country_code = "GB" if country == "UK" else "IN"
            
            # Clean location name before attempting geocoding (only if coordinates not provided)
            cleaned_location = collector._clean_location_name(location, country_code)
            if cleaned_location != location:
                print(f"[INFO] Cleaned location name: '{location}' -> '{cleaned_location}'")
            
            try:
                weather_dataset = collector.collect_complete_dataset(
                    location_name=cleaned_location,  # Use cleaned location
                    target_date=target_date,
                    country_code=country_code,
                    latitude=latitude,  # Pass coordinates if available
                    longitude=longitude  # Pass coordinates if available
                )
                state["weather_dataset"] = weather_dataset
            except ValueError as e:
                # Location not found - provide helpful error message
                error_msg = str(e)
                print(f"[WARNING] Geocoding error: {error_msg}")
                
                # Provide helpful suggestion
                if cleaned_location != location:
                    suggestion = f"I tried cleaning your location to '{cleaned_location}', but it still wasn't found. Please try entering just the city name (e.g., 'Coventry' or 'London')."
                else:
                    suggestion = f"Please try entering just the city name (e.g., '{cleaned_location.split(',')[0].strip()}' if that's your city)."
                
                state["blight_prediction"] = {
                    "error": "Location not found",
                    "user_message": f"Could not find location '{location}'. {suggestion}",
                    "suggestion": suggestion
                }
                state["final_report"] = f"Unable to find location '{location}'. {suggestion}"
                return state
            except Exception as e:
                print(f"[WARNING] Could not collect weather data: {e}")
                import traceback
                traceback.print_exc()
                state["blight_prediction"] = {
                    "error": "Weather data collection failed",
                    "user_message": f"Could not collect weather data for {location}. Error: {str(e)}"
                }
                state["final_report"] = f"Unable to collect weather data for {location}. Please verify the location name or try again later. Error: {str(e)}"
                return state
        
        if not weather_dataset:
            state["blight_prediction"] = {
                "error": "No weather dataset provided",
                "user_message": "Please provide weather data for blight prediction."
            }
            state["final_report"] = "I need weather data to predict blight risk. Please provide the weather information."
            return state

        # Step 3: Use DAP from state or calculated from sowing_date
        if days_after_planting is None:
            days_after_planting = state.get("days_after_planting", 30)
        
        # Step 4: Extract location info from weather dataset
        location_data = weather_dataset.get("location", {})
        location_name = f"{location_data.get('city', location or 'Unknown')}, {location_data.get('country', country)}"
        target_date = weather_dataset.get("target_date", datetime.now().strftime("%Y-%m-%d"))

        # Step 5: Check Hutton Criteria for UK
        hutton_criteria = None
        if country == "UK":
            hutton_criteria = self._check_hutton_criteria(weather_dataset)
            if hutton_criteria.get("met"):
                print(f"[WARNING] Hutton Criteria MET - High Late Blight Risk!")
                print(f"  Consecutive days: {hutton_criteria.get('consecutive_days')}")

        # Step 6: Determine growth stage based on DAP and country
        growth_stage = self._determine_growth_stage(days_after_planting, country)

        print(f"[INFO] Analyzing weather data for {location_name}...")
        print(f"[INFO] Country: {country}")
        print(f"[INFO] Days After Planting: {days_after_planting} ({growth_stage})")
        print(f"[INFO] Target Date: {target_date}")
        if hutton_criteria and hutton_criteria.get("met"):
            print(f"[WARNING] Hutton Criteria: MET - Immediate action recommended")

        # Step 7: Format weather data for AI analysis
        formatted_weather = self._format_weather_for_analysis(weather_dataset)

        # Step 7.5: Tavily recommendations will be fetched AFTER risk prediction
        # This is now handled in the streaming method after we know the actual risk levels
        # We don't search Tavily here anymore - wait for actual prediction results
        update_progress(7, "Preparing for risk assessment...", "analyze_weather", 50)
        tavily_data = {}  # Will be populated after risk prediction
        location_for_tavily = location_data.get('city', location or 'Unknown')
        
        # Format Tavily data for LLM
        tavily_context = ""
        if any(tavily_data.values()):
            tavily_context = "\n\nLOCATION-SPECIFIC RESEARCH DATA (Tavily Search):\n"
            for disease, data in tavily_data.items():
                if any(data.values()):
                    tavily_context += f"\n{disease} Research:\n"
                    
                    # Historical context
                    if data.get("historical_context"):
                        tavily_context += "Historical Occurrences:\n"
                        for hist in data["historical_context"][:2]:  # Limit to 2 most relevant
                            title = hist.get("title", "Historical Data")
                            content = hist.get("content", "")[:300]  # Truncate for prompt
                            tavily_context += f"- {title}: {content}...\n"
                    
                    # Recommendations
                    if data.get("recommendations"):
                        tavily_context += "Location-Specific Recommendations:\n"
                        for rec in data["recommendations"][:2]:
                            title = rec.get("title", "Recommendation")
                            content = rec.get("content", "")[:300]
                            tavily_context += f"- {title}: {content}...\n"
                    
                    # Preventive measures
                    if data.get("preventive_measures"):
                        tavily_context += "Preventive Measures:\n"
                        for prev in data["preventive_measures"][:2]:
                            title = prev.get("title", "Prevention")
                            content = prev.get("content", "")[:300]
                            tavily_context += f"- {title}: {content}...\n"
        
        # Step 8: Prepare user prompt with climate-specific context
        hutton_info = ""
        if country == "UK" and hutton_criteria:
            if hutton_criteria.get("met"):
                hutton_info = f"\nHUTTON CRITERIA STATUS: MET\n"
                hutton_info += f"Consecutive days meeting criteria: {hutton_criteria.get('consecutive_days')}\n"
                hutton_info += f"Details: {json.dumps(hutton_criteria.get('details', []), indent=2)}\n"
                hutton_info += f"IMMEDIATE FUNGICIDE APPLICATION RECOMMENDED\n"
            else:
                hutton_info = f"\nHUTTON CRITERIA STATUS: NOT MET\n"
        
        user_prompt = f"""Analyze the following weather data for potato blight risk prediction:

Location: {location_name}
Country: {country}
Elevation: {location_data.get('elevation', 'Unknown')}m
Days After Planting: {days_after_planting}
Sowing Date: {sowing_date or 'Not provided'}
Current Growth Stage: {growth_stage}
Target Date: {target_date}
Total Days in Window: {weather_dataset.get('metadata', {}).get('total_days', 8)}
{hutton_info}
DAILY WEATHER DATA (8-Day Window):
{formatted_weather}
{tavily_context}

INSTRUCTIONS:
- Analyze EACH day's conditions carefully
- Reference specific dates and values in your analysis
- Consider the growth stage and critical risk periods
- {"CHECK HUTTON CRITERIA FIRST - This is critical for UK predictions" if country == "UK" else ""}
- INTEGRATE Tavily research data into your recommendations - reference historical occurrences when relevant
- Frame recommendations with historical context: "Based on the last occurrence in {location_for_tavily}..." when historical data is available
- Provide actionable recommendations with specific timing
- Be specific about fungicide types and application methods
- Use climate-appropriate recommendations for {country}
- Include clear reasoning for your risk assessments
- Generate dynamic risk assessment visualization data:
  * Risk matrix showing probability vs. impact
  * Key factors and their weighted contribution to the risk score
  * Transparent display of calculation methodology

Respond ONLY with valid JSON in the exact format specified - no additional text."""

        # Step 9: Get climate-specific system prompt
        system_prompt = self._get_system_prompt(country)

        # Step 10: Prepare API messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        
        # Step 11: Analyzing weather patterns with AI
        update_progress(9, "Analyzing weather patterns and disease risk factors...", "analyze_weather", 60)
        
        # Call OpenAI API
        try:
            print("[INFO] Analyzing weather patterns with AI...")
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            print(f"[OK] Analysis complete")
            
            # Step 12: Processing AI analysis results
            update_progress(10, "Processing disease risk assessment...", "process_results", 70)
            
            # Parse JSON response
            try:
                # Clean up response (remove markdown if present)
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(result_text)
                
                # Add enhanced metadata
                result["analysis_timestamp"] = datetime.now().isoformat()
                result["model_version"] = "gpt-4o-mini"
                result["data_source"] = "Open-Meteo API"
                result["elevation"] = location_data.get('elevation', 'Unknown')
                result["country"] = country
                result["sowing_date"] = sowing_date
                result["location_from_profile"] = location
                
                # Store Tavily data for report generation
                result["tavily_data"] = tavily_data
                
                # Add Hutton Criteria for UK
                if country == "UK" and hutton_criteria:
                    result["hutton_criteria"] = hutton_criteria
                    if not result.get("hutton_criteria_met"):
                        result["hutton_criteria_met"] = hutton_criteria.get("met", False)
                
                # Add climate configuration used
                config = self.UK_CONFIG if country == "UK" else self.INDIA_CONFIG
                result["climate_config"] = {
                    "country": country,
                    "growth_stage_config": config["growth_stages"].get(growth_stage.lower().replace(" ", "_").replace("&", ""), {}),
                    "fungicides": config["fungicides"]
                }
                
                # Step 12.5: Get Tavily recommendations based on ACTUAL risk prediction results
                late_blight_risk = result.get("late_blight_risk", {})
                early_blight_risk = result.get("early_blight_risk", {})
                
                late_blight_risk_level = late_blight_risk.get("risk_level", "none").lower()
                late_blight_risk_pct = late_blight_risk.get("risk_percentage", 0)
                early_blight_risk_level = early_blight_risk.get("risk_level", "none").lower()
                early_blight_risk_pct = early_blight_risk.get("risk_percentage", 0)
                
                print(f"[TAVILY_LOGIC] Non-streaming: Late Blight: risk_level={late_blight_risk_level}, risk_pct={late_blight_risk_pct}")
                print(f"[TAVILY_LOGIC] Non-streaming: Early Blight: risk_level={early_blight_risk_level}, risk_pct={early_blight_risk_pct}")
                
                # Check if there's any actual risk (not "none" and > 0%)
                has_late_blight_risk = late_blight_risk_level != "none" and late_blight_risk_pct > 0
                has_early_blight_risk = early_blight_risk_level != "none" and early_blight_risk_pct > 0
                
                tavily_data = {}
                location_for_tavily = location_data.get('city', location or 'Unknown')
                
                if has_late_blight_risk or has_early_blight_risk:
                    # Search for specific diseases that have risk - location-specific
                    print(f"[TAVILY_LOGIC] Non-streaming: Searching for diseases with risk: Late Blight={has_late_blight_risk}, Early Blight={has_early_blight_risk}")
                    
                    if has_late_blight_risk:
                        print(f"[TAVILY_LOGIC] Non-streaming: Searching Tavily for Late Blight recommendations in {location_for_tavily}, {country}")
                        tavily_late = self._get_tavily_recommendations("Late Blight", location, country, weather_dataset)
                        if any(tavily_late.values()):
                            tavily_data["Late Blight"] = tavily_late
                    
                    if has_early_blight_risk:
                        print(f"[TAVILY_LOGIC] Non-streaming: Searching Tavily for Early Blight recommendations in {location_for_tavily}, {country}")
                        tavily_early = self._get_tavily_recommendations("Early Blight", location, country, weather_dataset)
                        if any(tavily_early.values()):
                            tavily_data["Early Blight"] = tavily_early
                else:
                    # No risk detected - provide general potato disease prevention recommendations
                    print(f"[TAVILY_LOGIC] Non-streaming: No specific disease risk detected - searching for general recommendations")
                    general_query = f"potato disease prevention general recommendations best practices {location_for_tavily} {country}"
                    general_results = self._search_tavily(general_query, max_results=3)
                    
                    if general_results:
                        general_refined = self._refine_tavily_results(general_results, "general_recommendations")
                        if general_refined:
                            tavily_data["General Prevention"] = {
                                "recommendations": general_refined,
                                "historical_context": [],
                                "preventive_measures": []
                            }
                
                # Store Tavily data in result
                result["tavily_data"] = tavily_data
                
                # Step 13: Calculate deterministic risk percentages using sliding window
                # This ensures consistent results instead of relying solely on AI
                update_progress(11, "Calculating deterministic risk scores...", "calculate_risk", 80)
                
                daily_weather = weather_dataset.get("daily_weather", {})
                dates = daily_weather.get("date", [])
                
                # Calculate deterministic risk percentages using sliding window approach
                if dates and len(dates) > 0:
                    # Calculate risk for each day using sliding window
                    late_blight_risks = []
                    early_blight_risks = []
                    window_size = 3
                    
                    for i in range(len(dates)):
                        window_start = max(0, i - window_size)
                        window_end = min(len(dates) - 1, i + window_size)
                        
                        # Get current day weather
                        temp_mean = self._safe_get_value(daily_weather, "temperature_2m_mean", i)
                        temp_min = self._safe_get_value(daily_weather, "temperature_2m_min", i)
                        temp_max = self._safe_get_value(daily_weather, "temperature_2m_max", i)
                        humidity_mean = self._safe_get_value(daily_weather, "relative_humidity_2m_mean", i)
                        humidity_min = self._safe_get_value(daily_weather, "relative_humidity_2m_min", i)
                        humidity_max = self._safe_get_value(daily_weather, "relative_humidity_2m_max", i)
                        precip = self._safe_get_value(daily_weather, "precipitation_sum", i)
                        wind = self._safe_get_value(daily_weather, "wind_speed_10m_mean", i)
                        cloud = self._safe_get_value(daily_weather, "cloud_cover_mean", i)
                        
                        # Calculate window averages for context
                        window_temp_means = [self._safe_get_value(daily_weather, "temperature_2m_mean", j) 
                                           for j in range(window_start, window_end + 1) 
                                           if self._safe_get_value(daily_weather, "temperature_2m_mean", j) is not None]
                        window_humidity_means = [self._safe_get_value(daily_weather, "relative_humidity_2m_mean", j) 
                                                for j in range(window_start, window_end + 1) 
                                                if self._safe_get_value(daily_weather, "relative_humidity_2m_mean", j) is not None]
                        
                        # Use current day with window context
                        effective_temp_mean = temp_mean if temp_mean is not None else (sum(window_temp_means) / len(window_temp_means) if window_temp_means else None)
                        effective_humidity_mean = humidity_mean if humidity_mean is not None else (sum(window_humidity_means) / len(window_humidity_means) if window_humidity_means else None)
                        
                        # Calculate risks
                        lb_risk = self._calculate_daily_late_blight_risk(
                            effective_temp_mean or temp_mean, temp_min, temp_max,
                            effective_humidity_mean or humidity_mean, humidity_min, humidity_max,
                            precip, wind, cloud
                        )
                        eb_risk = self._calculate_daily_early_blight_risk(
                            effective_temp_mean or temp_mean, temp_min, temp_max,
                            effective_humidity_mean or humidity_mean, humidity_min, humidity_max,
                            precip, wind, cloud
                        )
                        
                        late_blight_risks.append(lb_risk)
                        early_blight_risks.append(eb_risk)
                    
                    # Calculate overall risk percentages (average across all days, weighted by recency)
                    if late_blight_risks:
                        # Weight recent days more heavily
                        weights = [0.5 + (i / len(late_blight_risks)) * 0.5 for i in range(len(late_blight_risks))]
                        weighted_lb = sum(lb * w for lb, w in zip(late_blight_risks, weights)) / sum(weights)
                        weighted_eb = sum(eb * w for eb, w in zip(early_blight_risks, weights)) / sum(weights)
                        
                        # Update result with deterministic values (but keep AI analysis for context)
                        if "late_blight_risk" not in result:
                            result["late_blight_risk"] = {}
                        if "early_blight_risk" not in result:
                            result["early_blight_risk"] = {}
                        
                        # Use deterministic percentage, but keep AI's risk_level and other analysis
                        result["late_blight_risk"]["risk_percentage"] = round(weighted_lb, 1)
                        result["early_blight_risk"]["risk_percentage"] = round(weighted_eb, 1)
                        
                        # Update risk_level based on deterministic percentage
                        if weighted_lb >= 70:
                            result["late_blight_risk"]["risk_level"] = "high"
                        elif weighted_lb >= 40:
                            result["late_blight_risk"]["risk_level"] = "medium"
                        elif weighted_lb >= 20:
                            result["late_blight_risk"]["risk_level"] = "low"
                        else:
                            result["late_blight_risk"]["risk_level"] = "none"
                        
                        if weighted_eb >= 70:
                            result["early_blight_risk"]["risk_level"] = "high"
                        elif weighted_eb >= 40:
                            result["early_blight_risk"]["risk_level"] = "medium"
                        elif weighted_eb >= 20:
                            result["early_blight_risk"]["risk_level"] = "low"
                        else:
                            result["early_blight_risk"]["risk_level"] = "none"
                        
                        print(f"[DETERMINISTIC] Late Blight Risk: {round(weighted_lb, 1)}% ({result['late_blight_risk']['risk_level']})")
                        print(f"[DETERMINISTIC] Early Blight Risk: {round(weighted_eb, 1)}% ({result['early_blight_risk']['risk_level']})")
                
                # Ensure growth_stage and days_after_planting are in result
                if "growth_stage" not in result:
                    result["growth_stage"] = growth_stage
                if "days_after_planting" not in result:
                    result["days_after_planting"] = days_after_planting
                
                # Step 14: Generating charts
                update_progress(12, "Generating risk assessment visualizations...", "generate_charts", 85)
                
                # Generate chart data if not provided
                if "chart_data" not in result:
                    result["chart_data"] = self._generate_chart_data(result, weather_dataset)
                
                # Step 15: Compiling final report
                update_progress(13, "Compiling comprehensive disease risk report...", "final_report", 95)
                
                # Store in state
                state["blight_prediction"] = result
                
                # Generate clean user-friendly report
                report = self._generate_report(result, weather_dataset)
                state["final_report"] = report
                
                # Mark complete
                update_progress(12, "Analysis complete!", "complete", 100)
                
                return state
                
            except json.JSONDecodeError as e:
                print(f"[WARNING] JSON parsing error: {e}")
                print(f"Raw response: {result_text[:200]}...")
                
                # Graceful fallback
                state["blight_prediction"] = {
                    "error": "Response format error",
                    "summary": result_text,
                    "user_message": "Analysis completed but formatting issue occurred.",
                    "raw_response": result_text[:1000]
                }
                state["final_report"] = f"Blight Risk Analysis:\n\n{result_text[:1000]}"
                return state
                
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] API Error: {error_msg}")
            
            # User-friendly error messages
            if "rate_limit" in error_msg.lower():
                user_message = "Too many requests. Please wait a moment and try again."
            elif "invalid_api_key" in error_msg.lower():
                user_message = "Service configuration error. Please contact support."
            elif "timeout" in error_msg.lower():
                user_message = "Analysis timed out. Please try again."
            else:
                user_message = "Unable to complete analysis. Please try again."
            
            state["blight_prediction"] = {
                "error": error_msg,
                "user_message": user_message,
                "retry_allowed": True
            }
            state["final_report"] = user_message
            return state
    
    def predict_blight_risk_streaming(self, state: AgentState) -> Generator[Dict[str, Any], None, None]:
        """
        Stream blight prediction progress updates with enhanced features.
        Yields detailed step-by-step progress for engaging UI.
        
        Args:
            state: AgentState containing user_profile and optionally weather_dataset
            
        Yields:
            Dict with type, message, stage, progress, and optionally data or error
        """
        def yield_step(message: str, stage: str):
            """Yield a status update without progress percentages or step counters."""
            return {
                "type": "status",
                "message": message,
                "stage": stage
            }
        
        # Step 1: Initialization - YIELD IMMEDIATELY
        print("[BLIGHT_AGENT] Yielding first status update...")
        first_update = yield_step("Analyzing current weather conditions for your field...", "initialization")
        print(f"[BLIGHT_AGENT] First update: {first_update}")
        yield first_update
        
        # Step 2: Extract user data
        yield yield_step("Gathering field information and location data...", "extract_data")
        user_data = self._extract_user_data(state)
        location = user_data.get("location", "")
        country = user_data.get("country", None)  # Don't assume India as default
        days_after_planting = user_data.get("days_after_planting") or state.get("days_after_planting", 30)
        latitude = user_data.get("latitude")
        longitude = user_data.get("longitude")

        # Step 3: Check if weather data needs collection
        weather_dataset = state.get("weather_dataset")
        if not weather_dataset and location:
            if latitude is not None and longitude is not None:
                yield yield_step(f"Fetching weather and soil data using coordinates ({latitude}, {longitude})...", "collect_weather")
            else:
                yield yield_step(f"Fetching weather and soil data for {location}...", "collect_weather")
            collector = ComprehensiveBlightDataCollector()
            target_date = datetime.now().strftime("%Y-%m-%d")
            # Determine country code - don't default to IN if unknown
            country_code = None
            if country == "UK":
                country_code = "GB"
            elif country == "India":
                country_code = "IN"
            
            cleaned_location = collector._clean_location_name(location, country_code)
            try:
                # Collect progress messages in a list (serverless-compatible)
                # Note: For serverless (Vercel), threading doesn't work reliably,
                # so we collect all messages first, then yield them
                progress_messages = []
                
                def progress_callback(message: str):
                    """Callback that collects progress messages"""
                    if message and message.strip():
                        progress_messages.append(message.strip())
                
                # Collect data (this will populate progress_messages via callback)
                weather_dataset = collector.collect_complete_dataset(
                    location_name=cleaned_location,
                    target_date=target_date,
                    country_code=country_code,
                    latitude=latitude,  # Pass coordinates if available
                    longitude=longitude,  # Pass coordinates if available
                    progress_callback=progress_callback
                )
                
                # Yield all collected progress messages
                # Note: This yields all at once, not in real-time, but works on serverless
                for msg in progress_messages:
                    yield {
                        "type": "data_collection_progress",
                        "message": msg,
                        "stage": "collect_weather"
                    }
                
                state["weather_dataset"] = weather_dataset
                
                # Stream weather data summary immediately
                location_data = weather_dataset.get("location", {})
                daily_weather = weather_dataset.get("daily_weather", {})
                dates = daily_weather.get("date", [])
                
                # Get country from weather dataset (most accurate after geocoding)
                weather_country = location_data.get('country', country or 'Unknown')
                
                if dates:
                    first_date = dates[0] if dates else "N/A"
                    temp_mean = daily_weather.get("temperature_2m_mean", [])
                    hum_mean = daily_weather.get("relative_humidity_2m_mean", [])
                    
                    weather_summary = f"""## 🌦 Field & Weather Information

- **Location:** {location_data.get('city', location)}, {weather_country}
- **Elevation:** {location_data.get('elevation', 'N/A')}m
- **Analysis Date:** {first_date}
- **Forecast Window:** {len(dates)} days

**Current Conditions:**
- Temperature: {temp_mean[0] if temp_mean else 'N/A'}°C (avg)
- Humidity: {hum_mean[0] if hum_mean else 'N/A'}% (avg)

"""
                    yield {
                        "type": "content_chunk",
                        "stage": "weather_data",
                        "content": weather_summary,
                        "message": "Weather data received"
                    }
                
            except Exception as e:
                yield {"type": "error", "message": f"Could not collect weather data: {str(e)}"}
                return
        
        if not weather_dataset:
            yield {"type": "error", "message": "No weather dataset provided"}
            return
        
        # Step 4: Analyze temperature patterns
        yield yield_step("Analyzing temperature and soil parameters...", "analyze_temperature")
        
        # Stream engaging message during temperature analysis (non-streaming operation)
        from src.utils.streaming_helpers import stream_engaging_message
        location_data = weather_dataset.get("location", {})
        location_name = f"{location_data.get('city', 'Unknown')}, {location_data.get('country', country)}"
        target_date = weather_dataset.get("target_date", "Unknown")
        
        # Stream engaging NLP message for temperature analysis
        for msg_event in stream_engaging_message(
            "temperature_analysis",
            "analyzing temperature patterns",
            {"location": location_name},
            delay=0.015
        ):
            yield msg_event
        
        # Step 5: Analyzing humidity levels
        yield yield_step("Analyzing humidity and moisture levels...", "analyze_humidity")
        
        # Stream engaging message during humidity analysis
        for msg_event in stream_engaging_message(
            "humidity_analysis",
            "analyzing humidity patterns",
            {"location": location_name},
            delay=0.015
        ):
            yield msg_event
        
        # Step 6: Check Hutton Criteria for UK
        hutton_criteria = None
        if country == "UK":
            yield yield_step("Checking Hutton Criteria for Late Blight...", "hutton_check")
            hutton_criteria = self._check_hutton_criteria(weather_dataset)
            if hutton_criteria.get("met"):
                yield {"type": "warning", "message": "HUTTON CRITERIA MET - High Risk Period Detected!", "stage": "hutton_check"}

        # Step 7: Determine growth stage
        yield yield_step("Determining crop growth stage and phenology...", "growth_stage")
        growth_stage = self._determine_growth_stage(days_after_planting, country)

        # Step 8: Analyzing precipitation patterns
        yield yield_step("Analyzing precipitation and rainfall patterns...", "analyze_precipitation")
        
        # Stream engaging message during precipitation analysis
        for msg_event in stream_engaging_message(
            "precipitation_analysis",
            "analyzing precipitation patterns",
            {"location": location_name},
            delay=0.015
        ):
            yield msg_event
        
        # Step 9: Analyzing wind and air quality
        yield yield_step("Analyzing wind patterns and air quality parameters...", "analyze_wind_air")
        
        formatted_weather = self._format_weather_for_analysis(weather_dataset)
        
        # Prepare user prompt with climate-specific context
        hutton_info = ""
        if country == "UK" and hutton_criteria and hutton_criteria.get("met"):
            hutton_info = f"\nHUTTON CRITERIA: MET - Immediate action required\n"

        user_prompt = f"""Analyze the following weather data for potato blight risk prediction:

Location: {location_name}
Country: {country}
Elevation: {location_data.get('elevation', 'Unknown')}m
Days After Planting: {days_after_planting}
Current Growth Stage: {growth_stage}
Target Date: {target_date}
Total Days in Window: {weather_dataset.get('metadata', {}).get('total_days', 8)}
{hutton_info}
DAILY WEATHER DATA (8-Day Window):
{formatted_weather}

INSTRUCTIONS:
- Analyze EACH day's conditions carefully
- Reference specific dates and values in your analysis
- Consider the growth stage and critical risk periods
- {"CHECK HUTTON CRITERIA FIRST - Critical for UK" if country == "UK" else ""}
- Provide actionable recommendations with specific timing
- Be specific about fungicide types and application methods
- Calculate risk factor contributions for bar charts:
  * Temperature contribution (0-100): Based on optimal range (10-25°C ideal, outside = higher risk)
  * Humidity contribution (0-100): Based on RH levels (>90% = high risk, 60-80% = moderate)
  * Precipitation contribution (0-100): Based on rainfall amounts (>5mm = high risk)
  * Wind contribution (0-100): Based on wind speed (low wind = higher risk for spore spread)
  * Cloud Cover contribution (0-100): Based on cloud cover (high clouds = higher humidity risk)
- Include detailed chart_data with risk_factor_contributions for beautiful bar graphs
- Provide final risk percentage clearly

Respond ONLY with valid JSON in the exact format specified - no additional text."""

        system_prompt = self._get_system_prompt(country)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Step 10: Analyzing with AI
        yield yield_step("Evaluating disease risk patterns based on temperature and humidity...", "analyze_weather")
        
        try:
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            # Step 11: Processing AI analysis
            yield yield_step("Processing disease risk assessment...", "process_results")
            
            # Parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # Stream risk assessment results immediately
            late_blight_risk = result.get("late_blight_risk", {})
            early_blight_risk = result.get("early_blight_risk", {})
            
            risk_summary = "## 🧬 Risk Assessment\n\n"
            risk_summary += "| Disease | Risk Level | Confidence | Peak Days |\n"
            risk_summary += "|---------|------------|------------|-----------|\n"
            
            if late_blight_risk:
                risk_level = late_blight_risk.get("risk_level", "Unknown")
                risk_pct = late_blight_risk.get("risk_percentage", 0)
                confidence = late_blight_risk.get("confidence", "Medium")
                peak_days = late_blight_risk.get("peak_risk_days", "N/A")
                risk_summary += f"| Late Blight | **{risk_level.upper()} ({risk_pct}%)** | {confidence} | {peak_days} |\n"
            
            if early_blight_risk:
                risk_level = early_blight_risk.get("risk_level", "Unknown")
                risk_pct = early_blight_risk.get("risk_percentage", 0)
                confidence = early_blight_risk.get("confidence", "Medium")
                peak_days = early_blight_risk.get("peak_risk_days", "N/A")
                risk_summary += f"| Early Blight | **{risk_level.upper()} ({risk_pct}%)** | {confidence} | {peak_days} |\n"
            
            risk_summary += "\n"
            
            overall_summary = result.get("overall_summary", "")
            if overall_summary:
                risk_summary += f"**Summary:**\n{overall_summary}\n\n"
            
            risk_summary += "---\n\n"
            
            yield {
                "type": "content_chunk",
                "stage": "risk_assessment",
                "content": risk_summary,
                "message": "Risk analysis complete"
            }
            
            # Step 12: Calculate deterministic risk percentages using sliding window
            yield yield_step("Calculating deterministic risk scores with sliding window...", "calculate_risk")
            
            daily_weather = weather_dataset.get("daily_weather", {})
            dates = daily_weather.get("date", [])
            
            # Calculate deterministic risk percentages using sliding window approach
            if dates and len(dates) > 0:
                late_blight_risks = []
                early_blight_risks = []
                window_size = 3
                
                for i in range(len(dates)):
                    window_start = max(0, i - window_size)
                    window_end = min(len(dates) - 1, i + window_size)
                    
                    temp_mean = self._safe_get_value(daily_weather, "temperature_2m_mean", i)
                    temp_min = self._safe_get_value(daily_weather, "temperature_2m_min", i)
                    temp_max = self._safe_get_value(daily_weather, "temperature_2m_max", i)
                    humidity_mean = self._safe_get_value(daily_weather, "relative_humidity_2m_mean", i)
                    humidity_min = self._safe_get_value(daily_weather, "relative_humidity_2m_min", i)
                    humidity_max = self._safe_get_value(daily_weather, "relative_humidity_2m_max", i)
                    precip = self._safe_get_value(daily_weather, "precipitation_sum", i)
                    wind = self._safe_get_value(daily_weather, "wind_speed_10m_mean", i)
                    cloud = self._safe_get_value(daily_weather, "cloud_cover_mean", i)
                    
                    window_temp_means = [self._safe_get_value(daily_weather, "temperature_2m_mean", j) 
                                       for j in range(window_start, window_end + 1) 
                                       if self._safe_get_value(daily_weather, "temperature_2m_mean", j) is not None]
                    window_humidity_means = [self._safe_get_value(daily_weather, "relative_humidity_2m_mean", j) 
                                            for j in range(window_start, window_end + 1) 
                                            if self._safe_get_value(daily_weather, "relative_humidity_2m_mean", j) is not None]
                    
                    effective_temp_mean = temp_mean if temp_mean is not None else (sum(window_temp_means) / len(window_temp_means) if window_temp_means else None)
                    effective_humidity_mean = humidity_mean if humidity_mean is not None else (sum(window_humidity_means) / len(window_humidity_means) if window_humidity_means else None)
                    
                    lb_risk = self._calculate_daily_late_blight_risk(
                        effective_temp_mean or temp_mean, temp_min, temp_max,
                        effective_humidity_mean or humidity_mean, humidity_min, humidity_max,
                        precip, wind, cloud
                    )
                    eb_risk = self._calculate_daily_early_blight_risk(
                        effective_temp_mean or temp_mean, temp_min, temp_max,
                        effective_humidity_mean or humidity_mean, humidity_min, humidity_max,
                        precip, wind, cloud
                    )
                    
                    late_blight_risks.append(lb_risk)
                    early_blight_risks.append(eb_risk)
                
                if late_blight_risks:
                    weights = [0.5 + (i / len(late_blight_risks)) * 0.5 for i in range(len(late_blight_risks))]
                    weighted_lb = sum(lb * w for lb, w in zip(late_blight_risks, weights)) / sum(weights)
                    weighted_eb = sum(eb * w for eb, w in zip(early_blight_risks, weights)) / sum(weights)
                    
                    if "late_blight_risk" not in result:
                        result["late_blight_risk"] = {}
                    if "early_blight_risk" not in result:
                        result["early_blight_risk"] = {}
                    
                    result["late_blight_risk"]["risk_percentage"] = round(weighted_lb, 1)
                    result["early_blight_risk"]["risk_percentage"] = round(weighted_eb, 1)
                    
                    if weighted_lb >= 70:
                        result["late_blight_risk"]["risk_level"] = "high"
                    elif weighted_lb >= 40:
                        result["late_blight_risk"]["risk_level"] = "medium"
                    elif weighted_lb >= 20:
                        result["late_blight_risk"]["risk_level"] = "low"
                    else:
                        result["late_blight_risk"]["risk_level"] = "none"
                    
                    if weighted_eb >= 70:
                        result["early_blight_risk"]["risk_level"] = "high"
                    elif weighted_eb >= 40:
                        result["early_blight_risk"]["risk_level"] = "medium"
                    elif weighted_eb >= 20:
                        result["early_blight_risk"]["risk_level"] = "low"
                    else:
                        result["early_blight_risk"]["risk_level"] = "none"
            
            # Step 12.5: ML Classifier Validation (Secondary Validation Layer)
            # Use binary classification model as a fallback/validator for consistent predictions
            yield yield_step("Validating predictions with ML classifier...", "ml_validation")
            try:
                from src.models.disease_classifier import get_disease_classifier
                
                classifier = get_disease_classifier()
                if classifier:
                    # Prepare current weather data for ML validation
                    # Use average of first 3 days for more stable predictions
                    daily_weather = weather_dataset.get("daily_weather", {})
                    
                    if daily_weather and daily_weather.get("date"):
                        # Calculate averages across first 3 days (or available days)
                        num_days = min(3, len(daily_weather.get("date", [])))
                        temps = []
                        hums = []
                        winds = []
                        wind_dirs = []
                        pressures = []
                        
                        for idx in range(num_days):
                            temp = self._safe_get_value(daily_weather, "temperature_2m_mean", idx)
                            hum = self._safe_get_value(daily_weather, "relative_humidity_2m_mean", idx)
                            wind = self._safe_get_value(daily_weather, "wind_speed_10m_mean", idx)
                            wind_dir = self._safe_get_value(daily_weather, "wind_direction_10m_dominant", idx)
                            pressure = self._safe_get_value(daily_weather, "pressure_msl_mean", idx)
                            
                            if temp is not None:
                                temps.append(temp)
                            if hum is not None:
                                hums.append(hum)
                            if wind is not None:
                                winds.append(wind)
                            if wind_dir is not None:
                                wind_dirs.append(wind_dir)
                            if pressure is not None:
                                pressures.append(pressure)
                        
                        # Use averages for more stable predictions
                        current_weather = {
                            "Temperature": sum(temps) / len(temps) if temps else 20,
                            "Humidity": sum(hums) / len(hums) if hums else 70,
                            "Wind Speed": sum(winds) / len(winds) if winds else 5,
                            "Wind Bearing": sum(wind_dirs) / len(wind_dirs) if wind_dirs else 180,
                            "Visibility": 10,  # Default visibility (not in Open-Meteo)
                            "Pressure": sum(pressures) / len(pressures) if pressures else 1013
                        }
                        
                        # Validate current prediction with ML classifier
                        validation = classifier.validate_prediction(current_weather, result)
                        
                        # If adjustment was made, update the result
                        if validation.get("adjustment_made"):
                            adjusted = validation.get("adjusted_prediction", {})
                            if adjusted:
                                result["late_blight_risk"]["risk_percentage"] = round(adjusted["late_blight"], 1)
                                result["early_blight_risk"]["risk_percentage"] = round(adjusted["early_blight"], 1)
                                
                                # Recalculate risk levels based on adjusted percentages
                                weighted_lb = adjusted["late_blight"]
                                weighted_eb = adjusted["early_blight"]
                                
                                if weighted_lb >= 70:
                                    result["late_blight_risk"]["risk_level"] = "high"
                                elif weighted_lb >= 40:
                                    result["late_blight_risk"]["risk_level"] = "medium"
                                elif weighted_lb >= 20:
                                    result["late_blight_risk"]["risk_level"] = "low"
                                else:
                                    result["late_blight_risk"]["risk_level"] = "none"
                                
                                if weighted_eb >= 70:
                                    result["early_blight_risk"]["risk_level"] = "high"
                                elif weighted_eb >= 40:
                                    result["early_blight_risk"]["risk_level"] = "medium"
                                elif weighted_eb >= 20:
                                    result["early_blight_risk"]["risk_level"] = "low"
                                else:
                                    result["early_blight_risk"]["risk_level"] = "none"
                                
                                print(f"[ML_VALIDATION] Adjusted predictions - Late Blight: {weighted_lb:.1f}%, Early Blight: {weighted_eb:.1f}%")
                        
                        # Store ML validation metadata in result
                        result["ml_validation"] = {
                            "validated": validation.get("validated", True),
                            "adjustment_made": validation.get("adjustment_made", False),
                            "disagreement_score": validation.get("disagreement_score", 0),
                            "ml_prediction": validation.get("ml_prediction", {}),
                            "model_accuracy": validation.get("model_accuracy"),
                            "model_metrics": validation.get("model_metrics"),
                            "recommendation": validation.get("recommendation", "")
                        }
                        
                        print(f"[ML_VALIDATION] {validation.get('recommendation', 'Validation complete')}")
                    else:
                        print("[ML_VALIDATION] Weather data not available for ML validation")
                else:
                    print("[ML_VALIDATION] Classifier not available, skipping ML validation")
            except Exception as e:
                print(f"[ML_VALIDATION] Error during ML validation: {e}")
                import traceback
                traceback.print_exc()
                # Continue without ML validation - don't break the flow
            
            # Ensure growth_stage and days_after_planting are in result
            if "growth_stage" not in result:
                result["growth_stage"] = growth_stage
            if "days_after_planting" not in result:
                result["days_after_planting"] = days_after_planting
            
            # Step 13: Generating charts and visualizations
            yield yield_step("Generating charts and insights...", "generate_charts")
            
            # Generate chart data if not provided
            if "chart_data" not in result:
                result["chart_data"] = self._generate_chart_data(result, weather_dataset)
            
            # Stream chart data immediately
            if result.get("chart_data"):
                yield {
                    "type": "chart_data",
                    "data": result["chart_data"],
                    "message": "Risk visualization data ready"
                }
            
            # Add enhanced metadata
            result["analysis_timestamp"] = datetime.now().isoformat()
            result["model_version"] = "gpt-4o-mini"
            result["data_source"] = "Open-Meteo API"
            result["elevation"] = location_data.get('elevation', 'Unknown')
            result["country"] = country
            result["sowing_date"] = user_data.get("sowing_date")
            result["location_from_profile"] = user_data.get("location")
            
            # Add Hutton Criteria for UK
            if country == "UK" and hutton_criteria:
                result["hutton_criteria"] = hutton_criteria
                if not result.get("hutton_criteria_met"):
                    result["hutton_criteria_met"] = hutton_criteria.get("met", False)
            
            # Stream environmental observations
            env_observations = "## 🌿 Key Environmental Observations\n\n"
            daily_weather = weather_dataset.get("daily_weather", {})
            soil_moisture = weather_dataset.get("soil_moisture", {})
            if soil_moisture:
                moisture_values = soil_moisture.get("soil_moisture_0_to_7cm", [])
                if moisture_values:
                    avg_moisture = sum(moisture_values) / len(moisture_values) if moisture_values else 0
                    env_observations += f"- **Soil Moisture:** {avg_moisture:.2f} m³/m³"
                    if avg_moisture < 0.2:
                        env_observations += " → irrigation advised"
                    env_observations += "\n"
            
            daily_air = weather_dataset.get("daily_air_quality", {})
            if daily_air and "pm2_5" in daily_air:
                pm25_values = daily_air.get("pm2_5", [])
                if pm25_values:
                    pm25_min = min(pm25_values)
                    pm25_max = max(pm25_values)
                    env_observations += f"- **Air Quality:** PM2.5 levels {pm25_min}-{pm25_max} µg/m³"
                    if pm25_max > 50:
                        env_observations += " → may enhance spore dispersal"
                    env_observations += "\n"
            
            cloud_cover = daily_weather.get("cloud_cover_mean", [])
            if cloud_cover:
                cloud_min = min(cloud_cover)
                cloud_max = max(cloud_cover)
                env_observations += f"- **Cloud Cover:** {cloud_min}-{cloud_max}% during peak risk days\n"
            
            env_observations += "\n---\n\n"
            
            yield {
                "type": "content_chunk",
                "stage": "environmental_observations",
                "content": env_observations,
                "message": "Environmental analysis complete"
            }
            
            # Get Tavily recommendations based on ACTUAL risk prediction results
            yield yield_step("Gathering location-specific recommendations based on risk assessment...", "tavily_search")
            
            tavily_data = {}
            location_for_tavily = location_name
            
            # Determine which diseases have actual risk (not "none" or very low)
            late_blight_risk_level = late_blight_risk.get("risk_level", "none").lower()
            late_blight_risk_pct = late_blight_risk.get("risk_percentage", 0)
            early_blight_risk_level = early_blight_risk.get("risk_level", "none").lower()
            early_blight_risk_pct = early_blight_risk.get("risk_percentage", 0)
            
            print(f"[TAVILY_LOGIC] Late Blight: risk_level={late_blight_risk_level}, risk_pct={late_blight_risk_pct}")
            print(f"[TAVILY_LOGIC] Early Blight: risk_level={early_blight_risk_level}, risk_pct={early_blight_risk_pct}")
            
            # Check if there's any actual risk (not "none" and > 0%)
            has_late_blight_risk = late_blight_risk_level != "none" and late_blight_risk_pct > 0
            has_early_blight_risk = early_blight_risk_level != "none" and early_blight_risk_pct > 0
            
            if has_late_blight_risk or has_early_blight_risk:
                # Search for specific diseases that have risk - location-specific
                print(f"[TAVILY_LOGIC] Searching for diseases with risk: Late Blight={has_late_blight_risk}, Early Blight={has_early_blight_risk}")
                
                if has_late_blight_risk:
                    print(f"[TAVILY_LOGIC] Searching Tavily for Late Blight recommendations in {location_for_tavily}, {country}")
                    tavily_late = self._get_tavily_recommendations("Late Blight", location, country, weather_dataset)
                    if any(tavily_late.values()):
                        tavily_data["Late Blight"] = tavily_late
                        print(f"[TAVILY_LOGIC] Found {sum(len(v) if isinstance(v, list) else 1 for v in tavily_late.values())} Late Blight recommendations")
                
                if has_early_blight_risk:
                    print(f"[TAVILY_LOGIC] Searching Tavily for Early Blight recommendations in {location_for_tavily}, {country}")
                    tavily_early = self._get_tavily_recommendations("Early Blight", location, country, weather_dataset)
                    if any(tavily_early.values()):
                        tavily_data["Early Blight"] = tavily_early
                        print(f"[TAVILY_LOGIC] Found {sum(len(v) if isinstance(v, list) else 1 for v in tavily_early.values())} Early Blight recommendations")
            else:
                # No risk detected - provide general potato disease prevention recommendations
                print(f"[TAVILY_LOGIC] No specific disease risk detected - searching for general potato disease prevention recommendations")
                yield yield_step("Gathering general potato disease prevention recommendations...", "tavily_search")
                
                # Search for general recommendations (not disease-specific)
                general_query = f"potato disease prevention general recommendations best practices {location_for_tavily} {country}"
                general_results = self._search_tavily(general_query, max_results=3)
                
                if general_results:
                    # Refine general results
                    general_refined = self._refine_tavily_results(general_results, "general_recommendations")
                    if general_refined:
                        tavily_data["General Prevention"] = {
                            "recommendations": general_refined,
                            "historical_context": [],
                            "preventive_measures": []
                        }
                        print(f"[TAVILY_LOGIC] Found {len(general_refined)} general prevention recommendations")
            
            # Store Tavily data in result for report generation
            result["tavily_data"] = tavily_data
            
            # Stream Tavily section incrementally
            if tavily_data and any(any(data.values()) for data in tavily_data.values()):
                print(f"[TAVILY_LOGIC] Formatting Tavily section with {len(tavily_data)} disease categories")
                tavily_section = self._format_tavily_section(
                    tavily_data=tavily_data,
                    location=location_for_tavily,
                    country=country,
                    result=result,
                    weather_dataset=weather_dataset
                )
                
                if tavily_section:
                    # Stream Tavily section character-by-character
                    from src.utils.streaming_helpers import stream_text_character_by_character
                    for char_event in stream_text_character_by_character(tavily_section, chunk_size=2, delay=0.01, event_type="stream_char"):
                        yield char_event
            
            # Generate final report sections
            yield yield_step("Summarizing recommendations and generating final report...", "final_report")
            
            # Stream recommendations section
            recommendations = result.get("immediate_recommendations", [])
            preventive = result.get("preventive_recommendations", [])
            
            if recommendations or preventive:
                rec_section = "🧪 Recommendations\n\n"
                
                if recommendations:
                    rec_section += "Immediate Actions:\n\n"
                    for i, action in enumerate(recommendations, 1):
                        rec_section += f"{i}. {action}\n"
                    rec_section += "\n"
                
                if preventive:
                    rec_section += "Preventive Measures:\n\n"
                    for i, rec in enumerate(preventive, 1):
                        rec_section += f"{i}. {rec}\n"
                    rec_section += "\n"
                
                yield {
                    "type": "content_chunk",
                    "stage": "recommendations",
                    "content": rec_section,
                    "message": "Recommendations ready"
                }
            
            # Stream weekly outlook
            weekly_outlook = result.get("weekly_outlook", "")
            confidence_level = result.get("confidence_level", "MEDIUM")
            confidence_explanation = result.get("confidence_explanation", "")
            
            if weekly_outlook or confidence_level:
                outlook_section = "📅 Weekly Outlook\n\n"
                if weekly_outlook:
                    outlook_section += f"{weekly_outlook}\n\n"
                if confidence_level:
                    outlook_section += f"Confidence Level: {confidence_level.upper()}\n"
                if confidence_explanation:
                    outlook_section += f"{confidence_explanation}\n"
                outlook_section += "\n"
                
                yield {
                    "type": "content_chunk",
                    "stage": "weekly_outlook",
                    "content": outlook_section,
                    "message": "Weekly forecast complete"
                }
            
            # Generate beautiful natural language report
            yield yield_step("Generating comprehensive natural language report...", "final_report")
            report = self._generate_report(result, weather_dataset)
            result["final_report"] = report
            
            # Stream the final report character-by-character for smooth typing effect
            if report:
                # Import streaming helper
                from src.utils.streaming_helpers import stream_text_character_by_character
                
                # Stream report character-by-character
                for char_event in stream_text_character_by_character(report, chunk_size=2, delay=0.01, event_type="stream_char"):
                    yield char_event
            
            # Check for language preference and generate translations
            user_profile = state.get("user_profile", {})
            language_preference = user_profile.get("language_preference", None)
            translations = {}
            primary_language = "english"
            show_english_secondary = False
            
            if language_preference and report:
                requested_languages = language_preference if isinstance(language_preference, list) else [language_preference]
                # Filter out English from translation list
                requested_languages = [lang for lang in requested_languages if lang.lower() != "english"]
                
                if requested_languages:
                    yield yield_step(f"Generating report in {', '.join(requested_languages)}...", "translating")
                    try:
                        translations = self._translate_response(report, requested_languages)
                        print(f"[TRANSLATION] Blight report translated to: {', '.join(requested_languages)}")
                        
                        # Set primary language to user's preference
                        if requested_languages[0] in translations and translations[requested_languages[0]]:
                            primary_language = requested_languages[0]
                            # Add English as secondary/reference
                            translations["english"] = report
                            # The primary report will be the translated version
                            report = translations[requested_languages[0]]
                            show_english_secondary = True
                            print(f"[TRANSLATION] Primary language set to: {primary_language}")
                        
                    except Exception as e:
                        print(f"[TRANSLATION] Error translating blight report: {e}")
            
            # Final step
            yield yield_step("Analysis complete!", "complete")
            yield {
                "type": "result", 
                "data": result, 
                "report": report,  # This is now in the user's preferred language
                "translations": translations,
                "requested_languages": language_preference if isinstance(language_preference, list) else ([language_preference] if language_preference else []),
                "primary_language": primary_language,
                "show_english_secondary": show_english_secondary
            }
            
        except Exception as e:
            yield {"type": "error", "message": str(e)}
    
    def _format_weather_for_analysis(self, weather_dataset: Dict) -> str:
        """
        Format weather dataset for AI analysis.
        Creates a readable summary of all daily data points.
        
        Args:
            weather_dataset: Dataset from ComprehensiveBlightDataCollector
            
        Returns:
            Formatted string with daily weather summaries
        """
        daily_weather = weather_dataset.get("daily_weather", {})
        daily_air = weather_dataset.get("daily_air_quality", {})
        dates = daily_weather.get("date", [])
        target_date = weather_dataset.get("target_date", "")
        
        formatted = []
        
        for i, date in enumerate(dates):
            marker = " [TARGET DAY]" if date == target_date else ""
            day_summary = [f"\n[Date] {date}{marker}"]
            day_summary.append("-" * 60)
            
            # Temperature
            if "temperature_2m_mean" in daily_weather:
                temp_mean = self._safe_get(daily_weather, "temperature_2m_mean", i)
                temp_min = self._safe_get(daily_weather, "temperature_2m_min", i)
                temp_max = self._safe_get(daily_weather, "temperature_2m_max", i)
                day_summary.append(f"Temperature: Min {temp_min}°C, Max {temp_max}°C, Avg {temp_mean}°C")
            
            # Humidity
            if "relative_humidity_2m_mean" in daily_weather:
                hum_mean = self._safe_get(daily_weather, "relative_humidity_2m_mean", i)
                hum_min = self._safe_get(daily_weather, "relative_humidity_2m_min", i)
                hum_max = self._safe_get(daily_weather, "relative_humidity_2m_max", i)
                day_summary.append(f"Humidity: Min {hum_min}%, Max {hum_max}%, Avg {hum_mean}%")
            
            # Dew Point (important for disease)
            if "dew_point_2m_mean" in daily_weather:
                dew_mean = self._safe_get(daily_weather, "dew_point_2m_mean", i)
                day_summary.append(f"Dew Point: {dew_mean}°C")
            
            # Precipitation
            if "precipitation_sum" in daily_weather:
                precip = self._safe_get(daily_weather, "precipitation_sum", i)
                day_summary.append(f"Precipitation: {precip} mm")
            
            # Wind
            if "wind_speed_10m_mean" in daily_weather:
                wind_mean = self._safe_get(daily_weather, "wind_speed_10m_mean", i)
                wind_max = self._safe_get(daily_weather, "wind_speed_10m_max", i)
                day_summary.append(f"Wind Speed: Avg {wind_mean} km/h, Max {wind_max} km/h")
            
            # Cloud Cover
            if "cloud_cover_mean" in daily_weather:
                clouds = self._safe_get(daily_weather, "cloud_cover_mean", i)
                day_summary.append(f"Cloud Cover: {clouds}%")
            
            # Solar Radiation
            if "shortwave_radiation_sum" in daily_weather:
                solar = self._safe_get(daily_weather, "shortwave_radiation_sum", i)
                day_summary.append(f"Solar Radiation: {solar} Wh/m²")
            
            # Soil Temperature
            if "soil_temperature_0_to_7cm_mean" in daily_weather:
                soil_temp = self._safe_get(daily_weather, "soil_temperature_0_to_7cm_mean", i)
                day_summary.append(f"Soil Temperature (0-7cm): {soil_temp}°C")
            
            # Soil Moisture
            if "soil_moisture_0_to_7cm_mean" in daily_weather:
                soil_moist = self._safe_get(daily_weather, "soil_moisture_0_to_7cm_mean", i)
                day_summary.append(f"Soil Moisture (0-7cm): {soil_moist} m³/m³")
            
            # Air Quality
            if i < len(daily_air.get("date", [])):
                if "pm2_5_mean" in daily_air:
                    pm25 = self._safe_get(daily_air, "pm2_5_mean", i)
                    day_summary.append(f"PM2.5: {pm25} µg/m³")
                
                if "ozone_mean" in daily_air:
                    ozone = self._safe_get(daily_air, "ozone_mean", i)
                    day_summary.append(f"Ozone: {ozone} µg/m³")
                
                if "uv_index_max" in daily_air:
                    uv = self._safe_get(daily_air, "uv_index_max", i)
                    day_summary.append(f"UV Index (Max): {uv}")
            
            formatted.append("\n".join(day_summary))
        
        return "\n".join(formatted)
    
    def _safe_get(self, data_dict: Dict, key: str, index: int, decimals: int = 1) -> str:
        """
        Safely get value from dict at index with proper formatting.
        
        Args:
            data_dict: Dictionary with list values
            key: Key to access
            index: Index in the list
            decimals: Number of decimal places for floats
            
        Returns:
            Formatted string value or "N/A" if missing
        """
        if key in data_dict and index < len(data_dict[key]):
            val = data_dict[key][index]
            if val is not None:
                if isinstance(val, float):
                    return f"{val:.{decimals}f}"
                return str(val)
        return "N/A"
    
    def _determine_growth_stage(self, dap: int, country: str = "India") -> str:
        """
        Determine growth stage based on Days After Planting and country.
        
        Args:
            dap: Days after planting
            country: "India" or "UK"
            
        Returns:
            Growth stage name
        """
        if country == "UK":
            # UK growth stages
            if dap <= 20:
                return "Sowing & Germination"
            elif dap <= 50:
                return "Vegetative Growth"
            elif dap <= 75:
                return "Flowering"
            elif dap <= 105:
                return "Tuber Formation"
            elif dap <= 140:
                return "Maturity"
            else:
                return "Harvest"
        else:
            # India growth stages (existing)
            if dap <= 15:
                return "Sowing & Germination"
            elif dap <= 45:
                return "Vegetative Growth"
            elif dap <= 60:
                return "Tuber Initiation"
            elif dap <= 90:
                return "Tuber Bulking"
            elif dap <= 110:
                return "Maturity & Senescence"
            else:
                return "Harvest & Storage"
    
    def _generate_chart_data(self, result: Dict[str, Any], weather_dataset: Dict) -> Dict[str, Any]:
        """
        Generate chart data for risk visualization with detailed risk factor contributions.
        
        Args:
            result: Prediction result from LLM
            weather_dataset: Weather dataset
            
        Returns:
            Dict with chart data for frontend visualization including bar charts
        """
        daily_weather = weather_dataset.get("daily_weather", {})
        dates = daily_weather.get("date", [])
        
        # Get risk percentages
        late_blight_risk_pct = result.get("late_blight_risk", {}).get("risk_percentage", 0)
        early_blight_risk_pct = result.get("early_blight_risk", {}).get("risk_percentage", 0)
        overall_risk_pct = result.get("overall_disease_pressure", "moderate")
        
        # Calculate risk factor contributions from weather data
        risk_factor_contributions = self._calculate_risk_factor_contributions(daily_weather, dates)
        
        chart_data = {
            "risk_timeline": {
                "dates": dates,
                "late_blight_risk": [],
                "early_blight_risk": [],
                "overall_risk": []
            },
            "temperature_trend": {
                "dates": dates,
                "min_temp": [],
                "max_temp": [],
                "avg_temp": []
            },
            "humidity_trend": {
                "dates": dates,
                "min_humidity": [],
                "max_humidity": [],
                "avg_humidity": []
            },
            "risk_factors": {
                "labels": ["Temperature", "Humidity", "Precipitation", "Wind", "Cloud Cover"],
                "late_blight_weights": [0.3, 0.4, 0.15, 0.1, 0.05],
                "early_blight_weights": [0.25, 0.3, 0.2, 0.1, 0.15]
            },
            "risk_factor_contributions": risk_factor_contributions,
            "final_risk_percentage": {
                "late_blight": late_blight_risk_pct,
                "early_blight": early_blight_risk_pct,
                "overall": self._convert_pressure_to_percentage(overall_risk_pct, late_blight_risk_pct, early_blight_risk_pct)
            }
        }
        
        # Extract temperature data
        if "temperature_2m_min" in daily_weather:
            chart_data["temperature_trend"]["min_temp"] = [
                daily_weather["temperature_2m_min"][i] if i < len(daily_weather["temperature_2m_min"]) else None
                for i in range(len(dates))
            ]
        if "temperature_2m_max" in daily_weather:
            chart_data["temperature_trend"]["max_temp"] = [
                daily_weather["temperature_2m_max"][i] if i < len(daily_weather["temperature_2m_max"]) else None
                for i in range(len(dates))
            ]
        if "temperature_2m_mean" in daily_weather:
            chart_data["temperature_trend"]["avg_temp"] = [
                daily_weather["temperature_2m_mean"][i] if i < len(daily_weather["temperature_2m_mean"]) else None
                for i in range(len(dates))
            ]
        
        # Extract humidity data
        if "relative_humidity_2m_min" in daily_weather:
            chart_data["humidity_trend"]["min_humidity"] = [
                daily_weather["relative_humidity_2m_min"][i] if i < len(daily_weather["relative_humidity_2m_min"]) else None
                for i in range(len(dates))
            ]
        if "relative_humidity_2m_max" in daily_weather:
            chart_data["humidity_trend"]["max_humidity"] = [
                daily_weather["relative_humidity_2m_max"][i] if i < len(daily_weather["relative_humidity_2m_max"]) else None
                for i in range(len(dates))
            ]
        if "relative_humidity_2m_mean" in daily_weather:
            chart_data["humidity_trend"]["avg_humidity"] = [
                daily_weather["relative_humidity_2m_mean"][i] if i < len(daily_weather["relative_humidity_2m_mean"]) else None
                for i in range(len(dates))
            ]
        
        # Calculate daily risk scores using SLIDING WINDOW approach
        # For each day, calculate risk using a 7-day window (3 days before + current + 3 days after)
        # This provides more stable and context-aware risk assessments
        window_size = 3  # Days before and after to include in window
        
        for i in range(len(dates)):
            # Determine window bounds for this day
            window_start = max(0, i - window_size)
            window_end = min(len(dates) - 1, i + window_size)
            
            # Collect weather data for all days in the window
            window_temp_means = []
            window_temp_mins = []
            window_temp_maxs = []
            window_humidity_means = []
            window_humidity_mins = []
            window_humidity_maxs = []
            window_precips = []
            window_winds = []
            window_clouds = []
            
            for j in range(window_start, window_end + 1):
                temp_mean = daily_weather.get("temperature_2m_mean", [None] * len(dates))[j] if j < len(daily_weather.get("temperature_2m_mean", [])) else None
                temp_min = daily_weather.get("temperature_2m_min", [None] * len(dates))[j] if j < len(daily_weather.get("temperature_2m_min", [])) else None
                temp_max = daily_weather.get("temperature_2m_max", [None] * len(dates))[j] if j < len(daily_weather.get("temperature_2m_max", [])) else None
                humidity_mean = daily_weather.get("relative_humidity_2m_mean", [None] * len(dates))[j] if j < len(daily_weather.get("relative_humidity_2m_mean", [])) else None
                humidity_min = daily_weather.get("relative_humidity_2m_min", [None] * len(dates))[j] if j < len(daily_weather.get("relative_humidity_2m_min", [])) else None
                humidity_max = daily_weather.get("relative_humidity_2m_max", [None] * len(dates))[j] if j < len(daily_weather.get("relative_humidity_2m_max", [])) else None
                precip = daily_weather.get("precipitation_sum", [None] * len(dates))[j] if j < len(daily_weather.get("precipitation_sum", [])) else None
                wind = daily_weather.get("wind_speed_10m_mean", [None] * len(dates))[j] if j < len(daily_weather.get("wind_speed_10m_mean", [])) else None
                cloud = daily_weather.get("cloud_cover_mean", [None] * len(dates))[j] if j < len(daily_weather.get("cloud_cover_mean", [])) else None
                
                if temp_mean is not None:
                    window_temp_means.append(temp_mean)
                if temp_min is not None:
                    window_temp_mins.append(temp_min)
                if temp_max is not None:
                    window_temp_maxs.append(temp_max)
                if humidity_mean is not None:
                    window_humidity_means.append(humidity_mean)
                if humidity_min is not None:
                    window_humidity_mins.append(humidity_min)
                if humidity_max is not None:
                    window_humidity_maxs.append(humidity_max)
                if precip is not None:
                    window_precips.append(precip)
                if wind is not None:
                    window_winds.append(wind)
                if cloud is not None:
                    window_clouds.append(cloud)
            
            # Calculate window averages (weighted: current day has 40% weight, others share 60%)
            current_day_weight = 0.4
            other_days_weight = 0.6 / max(1, len(range(window_start, window_end + 1)) - 1) if window_end > window_start else 0
            
            # Get current day values (for weighted calculation)
            current_temp_mean = daily_weather.get("temperature_2m_mean", [None] * len(dates))[i] if i < len(daily_weather.get("temperature_2m_mean", [])) else None
            current_temp_min = daily_weather.get("temperature_2m_min", [None] * len(dates))[i] if i < len(daily_weather.get("temperature_2m_min", [])) else None
            current_temp_max = daily_weather.get("temperature_2m_max", [None] * len(dates))[i] if i < len(daily_weather.get("temperature_2m_max", [])) else None
            current_humidity_mean = daily_weather.get("relative_humidity_2m_mean", [None] * len(dates))[i] if i < len(daily_weather.get("relative_humidity_2m_mean", [])) else None
            current_humidity_min = daily_weather.get("relative_humidity_2m_min", [None] * len(dates))[i] if i < len(daily_weather.get("relative_humidity_2m_min", [])) else None
            current_humidity_max = daily_weather.get("relative_humidity_2m_max", [None] * len(dates))[i] if i < len(daily_weather.get("relative_humidity_2m_max", [])) else None
            current_precip = daily_weather.get("precipitation_sum", [None] * len(dates))[i] if i < len(daily_weather.get("precipitation_sum", [])) else None
            current_wind = daily_weather.get("wind_speed_10m_mean", [None] * len(dates))[i] if i < len(daily_weather.get("wind_speed_10m_mean", [])) else None
            current_cloud = daily_weather.get("cloud_cover_mean", [None] * len(dates))[i] if i < len(daily_weather.get("cloud_cover_mean", [])) else None
            
            # Calculate weighted averages for window
            if window_temp_means:
                window_avg_temp = (current_temp_mean * current_day_weight + 
                                 sum([t for t in window_temp_means if t != current_temp_mean]) * other_days_weight) if current_temp_mean is not None else sum(window_temp_means) / len(window_temp_means)
            else:
                window_avg_temp = current_temp_mean
            
            window_avg_temp_min = sum(window_temp_mins) / len(window_temp_mins) if window_temp_mins else current_temp_min
            window_avg_temp_max = sum(window_temp_maxs) / len(window_temp_maxs) if window_temp_maxs else current_temp_max
            window_avg_humidity = (current_humidity_mean * current_day_weight + 
                                 sum([h for h in window_humidity_means if h != current_humidity_mean]) * other_days_weight) if current_humidity_mean is not None and window_humidity_means else (sum(window_humidity_means) / len(window_humidity_means) if window_humidity_means else current_humidity_mean)
            window_avg_humidity_min = sum(window_humidity_mins) / len(window_humidity_mins) if window_humidity_mins else current_humidity_min
            window_avg_humidity_max = sum(window_humidity_maxs) / len(window_humidity_maxs) if window_humidity_maxs else current_humidity_max
            window_total_precip = sum(window_precips)  # Total precipitation in window
            window_avg_wind = sum(window_winds) / len(window_winds) if window_winds else current_wind
            window_avg_cloud = sum(window_clouds) / len(window_clouds) if window_clouds else current_cloud
            
            # Use current day's values with window context for risk calculation
            # This gives more weight to current conditions while considering trends
            effective_temp_mean = current_temp_mean if current_temp_mean is not None else window_avg_temp
            effective_temp_min = current_temp_min if current_temp_min is not None else window_avg_temp_min
            effective_temp_max = current_temp_max if current_temp_max is not None else window_avg_temp_max
            effective_humidity_mean = current_humidity_mean if current_humidity_mean is not None else window_avg_humidity
            effective_humidity_min = current_humidity_min if current_humidity_min is not None else window_avg_humidity_min
            effective_humidity_max = current_humidity_max if current_humidity_max is not None else window_avg_humidity_max
            effective_precip = current_precip if current_precip is not None else (window_total_precip / max(1, window_end - window_start + 1))
            effective_wind = current_wind if current_wind is not None else window_avg_wind
            effective_cloud = current_cloud if current_cloud is not None else window_avg_cloud
            
            # Calculate Late Blight risk using sliding window context
            lb_risk = self._calculate_daily_late_blight_risk(
                effective_temp_mean, effective_temp_min, effective_temp_max,
                effective_humidity_mean, effective_humidity_min, effective_humidity_max,
                effective_precip, effective_wind, effective_cloud
            )
            
            # Calculate Early Blight risk using sliding window context
            eb_risk = self._calculate_daily_early_blight_risk(
                effective_temp_mean, effective_temp_min, effective_temp_max,
                effective_humidity_mean, effective_humidity_min, effective_humidity_max,
                effective_precip, effective_wind, effective_cloud
            )
            
            # Overall risk is weighted average (Late Blight is more serious)
            overall_risk = (lb_risk * 0.7 + eb_risk * 0.3)
            
            chart_data["risk_timeline"]["late_blight_risk"].append(max(0, min(100, round(lb_risk, 1))))
            chart_data["risk_timeline"]["early_blight_risk"].append(max(0, min(100, round(eb_risk, 1))))
            chart_data["risk_timeline"]["overall_risk"].append(max(0, min(100, round(overall_risk, 1))))
        
        return chart_data
    
    def _calculate_daily_late_blight_risk(
        self, temp_mean, temp_min, temp_max,
        humidity_mean, humidity_min, humidity_max,
        precip, wind, cloud
    ) -> float:
        """Calculate Late Blight risk (0-100) for a single day based on weather conditions."""
        risk_score = 0.0
        
        # Temperature factor (optimal: 10-20°C, risk increases outside)
        if temp_mean is not None:
            if 10 <= temp_mean <= 20:
                temp_risk = 20  # Low risk in optimal range
            elif 8 <= temp_mean < 10 or 20 < temp_mean <= 25:
                temp_risk = 40  # Moderate risk
            elif 5 <= temp_mean < 8 or 25 < temp_mean <= 30:
                temp_risk = 60  # Higher risk
            elif temp_mean < 5 or temp_mean > 30:
                temp_risk = 30  # Very cold or hot = lower risk (pathogen less active)
            else:
                temp_risk = 50
            risk_score += temp_risk * 0.25  # 25% weight
        elif temp_min is not None and temp_max is not None:
            # Use min/max if mean not available
            avg_temp = (temp_min + temp_max) / 2
            if 10 <= avg_temp <= 20:
                temp_risk = 20
            elif 8 <= avg_temp < 10 or 20 < avg_temp <= 25:
                temp_risk = 40
            else:
                temp_risk = 50
            risk_score += temp_risk * 0.25
        
        # Humidity factor (critical: >90% for 6+ hours = high risk)
        if humidity_mean is not None:
            if humidity_mean >= 90:
                hum_risk = 90  # Very high risk
            elif humidity_mean >= 85:
                hum_risk = 70  # High risk
            elif humidity_mean >= 80:
                hum_risk = 50  # Moderate risk
            elif humidity_mean >= 70:
                hum_risk = 30  # Low risk
            else:
                hum_risk = 15  # Very low risk
            risk_score += hum_risk * 0.35  # 35% weight (most important)
        elif humidity_max is not None:
            # Use max if mean not available (conservative estimate)
            if humidity_max >= 90:
                hum_risk = 85
            elif humidity_max >= 85:
                hum_risk = 65
            else:
                hum_risk = 40
            risk_score += hum_risk * 0.35
        
        # Precipitation factor (rain increases risk)
        if precip is not None:
            if precip >= 10:
                precip_risk = 80  # High risk with heavy rain
            elif precip >= 5:
                precip_risk = 60  # Moderate risk
            elif precip >= 2:
                precip_risk = 40  # Low-moderate risk
            elif precip > 0:
                precip_risk = 25  # Low risk with light rain
            else:
                precip_risk = 10  # Very low risk, no rain
            risk_score += precip_risk * 0.20  # 20% weight
        
        # Wind factor (low wind = higher risk, spores don't disperse)
        if wind is not None:
            if wind < 5:
                wind_risk = 70  # High risk, low wind
            elif wind < 10:
                wind_risk = 50  # Moderate risk
            elif wind < 15:
                wind_risk = 30  # Lower risk, moderate wind
            else:
                wind_risk = 15  # Very low risk, high wind disperses spores
            risk_score += wind_risk * 0.10  # 10% weight
        
        # Cloud cover factor (high clouds = higher humidity risk)
        if cloud is not None:
            if cloud >= 80:
                cloud_risk = 60  # High risk, overcast
            elif cloud >= 60:
                cloud_risk = 40  # Moderate risk
            elif cloud >= 40:
                cloud_risk = 25  # Low risk
            else:
                cloud_risk = 10  # Very low risk, clear skies
            risk_score += cloud_risk * 0.10  # 10% weight
        
        # Ensure minimum visibility (if any risk factors present, show at least 5%)
        if risk_score > 0 and risk_score < 5:
            risk_score = 5
        
        return risk_score
    
    def _calculate_daily_early_blight_risk(
        self, temp_mean, temp_min, temp_max,
        humidity_mean, humidity_min, humidity_max,
        precip, wind, cloud
    ) -> float:
        """Calculate Early Blight risk (0-100) for a single day based on weather conditions."""
        risk_score = 0.0
        
        # Temperature factor (optimal: 20-25°C, warm days + cool nights)
        if temp_mean is not None:
            if 20 <= temp_mean <= 25:
                temp_risk = 60  # Optimal for Early Blight
            elif 18 <= temp_mean < 20 or 25 < temp_mean <= 28:
                temp_risk = 50  # Good conditions
            elif 15 <= temp_mean < 18 or 28 < temp_mean <= 30:
                temp_risk = 40  # Moderate
            elif temp_mean < 15 or temp_mean > 30:
                temp_risk = 20  # Too cold or hot
            else:
                temp_risk = 35
            risk_score += temp_risk * 0.30  # 30% weight
        elif temp_min is not None and temp_max is not None:
            # Warm days + cool nights are ideal
            day_night_diff = temp_max - temp_min
            avg_temp = (temp_min + temp_max) / 2
            if 20 <= avg_temp <= 25 and day_night_diff >= 8:
                temp_risk = 70  # Ideal: warm day, cool night
            elif 18 <= avg_temp <= 28:
                temp_risk = 50
            else:
                temp_risk = 30
            risk_score += temp_risk * 0.30
        
        # Humidity factor (moderate humidity: 70-90%)
        if humidity_mean is not None:
            if 80 <= humidity_mean <= 90:
                hum_risk = 70  # Optimal range
            elif 70 <= humidity_mean < 80:
                hum_risk = 55  # Good
            elif 60 <= humidity_mean < 70:
                hum_risk = 40  # Moderate
            elif humidity_mean >= 90:
                hum_risk = 50  # Too high (more Late Blight)
            else:
                hum_risk = 25  # Too low
            risk_score += hum_risk * 0.25  # 25% weight
        elif humidity_max is not None:
            if 75 <= humidity_max <= 90:
                hum_risk = 60
            else:
                hum_risk = 35
            risk_score += hum_risk * 0.25
        
        # Precipitation factor (moderate rain is good for Early Blight)
        if precip is not None:
            if 5 <= precip <= 15:
                precip_risk = 65  # Optimal
            elif 2 <= precip < 5 or 15 < precip <= 20:
                precip_risk = 50  # Good
            elif precip > 20:
                precip_risk = 40  # Too much rain
            elif precip > 0:
                precip_risk = 35  # Light rain
            else:
                precip_risk = 20  # No rain
            risk_score += precip_risk * 0.25  # 25% weight
        
        # Wind factor (moderate wind is okay, low wind helps)
        if wind is not None:
            if wind < 8:
                wind_risk = 55  # Low wind helps
            elif wind < 15:
                wind_risk = 40  # Moderate
            else:
                wind_risk = 25  # High wind disperses
            risk_score += wind_risk * 0.10  # 10% weight
        
        # Cloud cover factor (moderate clouds)
        if cloud is not None:
            if 50 <= cloud <= 70:
                cloud_risk = 50  # Moderate clouds
            elif 40 <= cloud < 50 or 70 < cloud <= 80:
                cloud_risk = 40
            elif cloud >= 80:
                cloud_risk = 30  # Too overcast (more Late Blight)
            else:
                cloud_risk = 25  # Clear skies
            risk_score += cloud_risk * 0.10  # 10% weight
        
        # Ensure minimum visibility
        if risk_score > 0 and risk_score < 5:
            risk_score = 5
        
        return risk_score
    
    def _calculate_risk_factor_contributions(self, daily_weather: Dict, dates: List[str]) -> Dict[str, Any]:
        """
        Calculate risk factor contributions for bar chart visualization.
        
        Returns:
            Dict with risk factor contributions (0-100) for each factor
        """
        contributions = {
            "late_blight": {
                "temperature": 0,
                "humidity": 0,
                "precipitation": 0,
                "wind": 0,
                "cloud_cover": 0
            },
            "early_blight": {
                "temperature": 0,
                "humidity": 0,
                "precipitation": 0,
                "wind": 0,
                "cloud_cover": 0
            }
        }
        
        if not dates:
            return contributions
        
        # Calculate averages across all days
        temp_values = []
        humidity_values = []
        precip_values = []
        wind_values = []
        cloud_values = []
        
        for i in range(len(dates)):
            # Temperature (optimal: 10-25°C, risk increases outside this range)
            if "temperature_2m_mean" in daily_weather and i < len(daily_weather["temperature_2m_mean"]):
                temp = daily_weather["temperature_2m_mean"][i]
                if temp is not None:
                    temp_values.append(temp)
            
            # Humidity (optimal: 60-80%, risk increases >90%)
            if "relative_humidity_2m_mean" in daily_weather and i < len(daily_weather["relative_humidity_2m_mean"]):
                hum = daily_weather["relative_humidity_2m_mean"][i]
                if hum is not None:
                    humidity_values.append(hum)
            
            # Precipitation (risk increases with >5mm)
            if "precipitation_sum" in daily_weather and i < len(daily_weather["precipitation_sum"]):
                precip = daily_weather["precipitation_sum"][i]
                if precip is not None:
                    precip_values.append(precip)
            
            # Wind (low wind = higher risk for spore spread)
            if "wind_speed_10m_mean" in daily_weather and i < len(daily_weather["wind_speed_10m_mean"]):
                wind = daily_weather["wind_speed_10m_mean"][i]
                if wind is not None:
                    wind_values.append(wind)
            
            # Cloud Cover (high clouds = higher humidity risk)
            if "cloud_cover_mean" in daily_weather and i < len(daily_weather["cloud_cover_mean"]):
                cloud = daily_weather["cloud_cover_mean"][i]
                if cloud is not None:
                    cloud_values.append(cloud)
        
        # Calculate risk contributions
        if temp_values:
            avg_temp = sum(temp_values) / len(temp_values)
            # Optimal: 10-25°C = low risk (20), outside = higher risk
            if 10 <= avg_temp <= 25:
                temp_risk = 20
            elif avg_temp < 5 or avg_temp > 30:
                temp_risk = 90
            elif avg_temp < 10 or avg_temp > 25:
                temp_risk = 60
            else:
                temp_risk = 40
            contributions["late_blight"]["temperature"] = int(temp_risk)
            contributions["early_blight"]["temperature"] = int(temp_risk * 0.9)
        
        if humidity_values:
            avg_humidity = sum(humidity_values) / len(humidity_values)
            # Optimal: 60-80% = low risk (30), >90% = high risk (90)
            if avg_humidity > 90:
                hum_risk = 90
            elif avg_humidity > 80:
                hum_risk = 70
            elif 60 <= avg_humidity <= 80:
                hum_risk = 30
            else:
                hum_risk = 50
            contributions["late_blight"]["humidity"] = int(hum_risk)
            contributions["early_blight"]["humidity"] = int(hum_risk * 0.8)
        
        if precip_values:
            total_precip = sum(precip_values)
            # Risk increases with precipitation
            if total_precip > 20:
                precip_risk = 85
            elif total_precip > 10:
                precip_risk = 70
            elif total_precip > 5:
                precip_risk = 50
            else:
                precip_risk = 25
            contributions["late_blight"]["precipitation"] = int(precip_risk)
            contributions["early_blight"]["precipitation"] = int(precip_risk * 0.7)
        
        if wind_values:
            avg_wind = sum(wind_values) / len(wind_values)
            # Low wind = higher risk (spores don't disperse)
            if avg_wind < 5:
                wind_risk = 70
            elif avg_wind < 10:
                wind_risk = 50
            else:
                wind_risk = 30
            contributions["late_blight"]["wind"] = int(wind_risk)
            contributions["early_blight"]["wind"] = int(wind_risk * 0.6)
        
        if cloud_values:
            avg_cloud = sum(cloud_values) / len(cloud_values)
            # High cloud cover = higher humidity risk
            if avg_cloud > 80:
                cloud_risk = 75
            elif avg_cloud > 60:
                cloud_risk = 55
            else:
                cloud_risk = 35
            contributions["late_blight"]["cloud_cover"] = int(cloud_risk)
            contributions["early_blight"]["cloud_cover"] = int(cloud_risk * 0.7)
        
        return contributions
    
    def _convert_pressure_to_percentage(self, pressure: str, late_blight: float, early_blight: float) -> float:
        """Convert overall disease pressure string to percentage"""
        if isinstance(pressure, str):
            pressure_lower = pressure.lower()
            if "high" in pressure_lower or "severe" in pressure_lower:
                return max(late_blight, early_blight) * 1.1  # Slightly above max
            elif "moderate" in pressure_lower or "medium" in pressure_lower:
                return (late_blight + early_blight) / 2
            elif "low" in pressure_lower or "minimal" in pressure_lower:
                return min(late_blight, early_blight) * 0.9  # Slightly below min
            else:
                return (late_blight + early_blight) / 2
        return (late_blight + early_blight) / 2
    
    def _search_tavily(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search Tavily for disease recommendations and historical data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not TAVILY_AVAILABLE:
            return []
        
        try:
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                return []
            
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            return response.get("results", [])
        except Exception as e:
            print(f"[WARNING] Tavily search failed: {e}")
            return []
    
    def _refine_tavily_results(self, raw_results: List[Dict], category: str) -> List[Dict]:
        """
        Process raw Tavily search results through LLM to make them human-readable,
        grammatically correct, and professionally formatted.
        
        Args:
            raw_results: List of raw Tavily search results
            category: Category of results ("historical_context", "recommendations", "preventive_measures")
            
        Returns:
            List of refined results with cleaned content
        """
        if not raw_results:
            return []
        
        try:
            # Prepare raw content for LLM processing
            raw_content = []
            for i, result in enumerate(raw_results, 1):
                title = result.get("title", f"Result {i}")
                content = result.get("content", "")
                url = result.get("url", "")
                raw_content.append(f"Result {i}:\nTitle: {title}\nContent: {content}\nURL: {url}")
            
            raw_text = "\n\n---\n\n".join(raw_content)
            
            # Create prompt for LLM to refine the content
            system_prompt = """You are an expert agricultural content editor specializing in plant disease management. 
Your task is to refine raw research data into clear, professional, and grammatically correct recommendations.

STREAMING BEHAVIOR:
Process and refine content step-by-step. Do not mention progress, loading, or percentages. Instead, communicate naturally like "Refining research recommendations..." or "Formatting treatment guidelines...". Stream your outputs in stages, with each section being complete and self-contained.

CRITICAL CLEANING RULES:
- REMOVE ALL markdown headers: #, ##, ###, ####, etc. - convert them to plain text or remove entirely
- REMOVE ALL references to AI services: "ChatGPT", "OpenAI", "ChatOpenAI", "chatopen ai", "AI assistant", "AI model", etc.
- REMOVE ALL markdown formatting: **bold**, *italic*, `code`, etc. - convert to plain text
- REMOVE ALL markdown list markers if they appear in content: -, *, 1., etc. (keep the content, just remove the markers)
- PRESERVE location-specific data: dates, locations, weather conditions, historical outbreaks
- PRESERVE actionable recommendations: fungicide names, dosages, application rates, treatment methods
- Format as clear, readable paragraphs WITHOUT markdown
- Use plain text only - no markdown syntax whatsoever

Guidelines:
- Remove technical jargon, copyright notices, citation formats, and metadata
- Improve grammar and sentence structure
- Make content concise and actionable
- Maintain scientific accuracy
- Use professional agricultural terminology
- Format as clear, readable paragraphs (NO markdown)
- Preserve key information (dates, locations, specific recommendations)
- Remove redundant information and formatting artifacts
- Do NOT mention progress percentages, loading states, or step counters
- Do NOT mention AI tools, models, or services"""
            
            user_prompt = f"""Please refine the following {category} research data about potato disease management. 
Make it human-readable, grammatically correct, and professionally formatted.

RAW RESEARCH DATA:
{raw_text}

Please provide refined versions of each result. For each result, provide:
1. A clear, professional title (extract meaningful title from content or URL)
2. A well-written, grammatically correct summary (2-4 sentences) that highlights key insights
3. Key actionable points if applicable (extract specific recommendations, fungicides, dosages, dates)
4. Source name (extract meaningful source name from URL domain, e.g., "IntechOpen", "Academia.edu", "NACL Industries")

Format your response as JSON:
{{
    "refined_results": [
        {{
            "title": "Refined professional title",
            "summary": "Clear, grammatically correct summary paragraph with key insights",
            "key_points": ["Specific actionable point 1", "Specific actionable point 2", "Specific actionable point 3"],
            "source_name": "Extracted source name from URL",
            "url": "original_url"
        }}
    ]
}}

Important:
- Extract source names from URLs (e.g., "intechopen.com" → "IntechOpen", "academia.edu" → "Academia.edu")
- Preserve specific technical details (fungicide names, dosages, dates, locations)
- Remove copyright notices, citation formats, and metadata
- Make summaries concise but informative

Respond ONLY with valid JSON - no additional text."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            # Debug: Log raw response
            print(f"[TAVILY_DEBUG] Raw LLM response length: {len(result_text)} chars")
            print(f"[TAVILY_DEBUG] Raw response preview: {result_text[:200]}...")
            
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Additional cleaning: Remove any remaining markdown or AI references
            import re
            # Remove markdown headers
            result_text = re.sub(r'^#+\s*', '', result_text, flags=re.MULTILINE)
            # Remove AI service references
            result_text = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model|generated by|created by AI)\b', '', result_text, flags=re.IGNORECASE)
            
            parsed = json.loads(result_text)
            refined_results = parsed.get("refined_results", [])
            
            # Debug: Log refined results
            print(f"[TAVILY_DEBUG] Refined {len(refined_results)} results for category: {category}")
            
            # Post-process: Clean each refined result
            for refined in refined_results:
                # Remove markdown from title
                if refined.get("title"):
                    refined["title"] = re.sub(r'^#+\s*', '', refined["title"]).strip()
                    refined["title"] = re.sub(r'\*\*(.*?)\*\*', r'\1', refined["title"])  # Remove bold
                    refined["title"] = re.sub(r'\*(.*?)\*', r'\1', refined["title"])  # Remove italic
                
                # Remove markdown from summary
                if refined.get("summary"):
                    refined["summary"] = re.sub(r'^#+\s*', '', refined["summary"], flags=re.MULTILINE)
                    refined["summary"] = re.sub(r'\*\*(.*?)\*\*', r'\1', refined["summary"])  # Remove bold
                    refined["summary"] = re.sub(r'\*(.*?)\*', r'\1', refined["summary"])  # Remove italic
                    refined["summary"] = re.sub(r'`(.*?)`', r'\1', refined["summary"])  # Remove code
                    # Remove AI references
                    refined["summary"] = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model)\b', '', refined["summary"], flags=re.IGNORECASE)
                    refined["summary"] = refined["summary"].strip()
                
                # Clean key points
                if refined.get("key_points"):
                    cleaned_points = []
                    for point in refined["key_points"]:
                        cleaned = re.sub(r'^#+\s*', '', point)
                        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
                        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
                        cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)
                        cleaned = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model)\b', '', cleaned, flags=re.IGNORECASE)
                        cleaned = cleaned.strip()
                        if cleaned:  # Only add non-empty points
                            cleaned_points.append(cleaned)
                    refined["key_points"] = cleaned_points
            
            # Merge with original URLs and metadata, extract source names
            for i, refined in enumerate(refined_results):
                if i < len(raw_results):
                    original_url = raw_results[i].get("url", "")
                    refined["original_url"] = original_url
                    # Keep original URL as primary
                    if not refined.get("url"):
                        refined["url"] = original_url
                    
                    # Extract source name from URL if not provided
                    if not refined.get("source_name") and original_url:
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(original_url)
                            domain = parsed.netloc.replace("www.", "")
                            # Extract meaningful name (e.g., "intechopen.com" → "IntechOpen")
                            if domain:
                                parts = domain.split(".")
                                if len(parts) > 0:
                                    source_name = parts[0].capitalize()
                                    # Handle special cases
                                    if "academia" in domain:
                                        source_name = "Academia.edu"
                                    elif "intechopen" in domain:
                                        source_name = "IntechOpen"
                                    elif "mdpi" in domain:
                                        source_name = "MDPI"
                                    elif "pmc" in domain or "ncbi" in domain:
                                        source_name = "PubMed Central"
                                    refined["source_name"] = source_name
                        except Exception:
                            pass
            
            return refined_results
            
        except Exception as e:
            print(f"[WARNING] Failed to refine Tavily results: {e}")
            # Return original results if refinement fails
            return raw_results
    
    def _get_tavily_recommendations(self, disease_name: str, location: str, country: str, 
                                     current_weather: Dict = None) -> Dict[str, Any]:
        """
        Get comprehensive Tavily recommendations for a disease including:
        - Location-specific recommendations
        - Historical context and occurrences with weather comparisons
        - Preventive measures
        
        Results are processed through LLM to make them human-readable and professional.
        Uses location-specific site filters for better quality results.
        Compares historical outbreak weather conditions with current conditions.
        
        Args:
            disease_name: Name of the disease (e.g., "Late Blight", "Early Blight")
            location: Location name (e.g., "Coventry", "Hyderabad")
            country: Country name (e.g., "UK", "India")
            current_weather: Current weather conditions for comparison (optional)
            
        Returns:
            Dict with recommendations, historical_context, and preventive_measures (all refined)
        """
        tavily_data = {
            "recommendations": [],
            "historical_context": [],
            "preventive_measures": [],
            "weather_comparison": None
        }
        
        if not TAVILY_AVAILABLE:
            return tavily_data
        
        try:
            # Build location-specific query with site filters for better quality
            # For India: prefer .gov.in, .edu, .org sites
            # For UK: prefer .gov.uk, .ac.uk, .org.uk sites
            site_filter = ""
            if country == "India":
                site_filter = " site:.gov.in OR site:.edu OR site:.org"
            elif country == "UK":
                site_filter = " site:.gov.uk OR site:.ac.uk OR site:.org.uk"
            
            # Search for location-specific recommendations
            rec_query = f"{disease_name} potato management recommendations treatment {location} {country}{site_filter}"
            rec_results = self._search_tavily(rec_query, max_results=3)
            if rec_results:
                # Refine through LLM
                tavily_data["recommendations"] = self._refine_tavily_results(rec_results, "recommendations")
            
            # Search for RECENT outbreaks with dates and weather conditions
            # Use more specific queries to get recent outbreaks
            history_queries = [
                f"potato {disease_name} outbreak {location} {country} 2024 2023 2022 recent occurrence date weather conditions temperature humidity",
                f"{disease_name} potato epidemic {location} {country} recent years outbreak date temperature rainfall",
                f"potato {disease_name} {location} {country} last outbreak when date weather conditions similar"
            ]
            
            all_history_results = []
            for query in history_queries:
                results = self._search_tavily(query + site_filter, max_results=2)
                all_history_results.extend(results)
                if len(all_history_results) >= 5:  # Get top 5 most relevant
                    break
            
            if all_history_results:
                # Refine through LLM with emphasis on extracting dates and weather
                tavily_data["historical_context"] = self._refine_tavily_results_with_weather(
                    all_history_results, current_weather, location, country
                )
            
            # Search for preventive measures
            preventive_query = f"{disease_name} potato prevention preventive measures {location} {country}{site_filter}"
            preventive_results = self._search_tavily(preventive_query, max_results=2)
            if preventive_results:
                # Refine through LLM
                tavily_data["preventive_measures"] = self._refine_tavily_results(preventive_results, "preventive_measures")
                
        except Exception as e:
            print(f"[WARNING] Tavily recommendation search failed: {e}")
            import traceback
            traceback.print_exc()
        
        return tavily_data
    
    def _refine_tavily_results_with_weather(self, raw_results: List[Dict], current_weather: Dict, 
                                            location: str, country: str) -> List[Dict]:
        """
        Process raw Tavily results and extract historical outbreak data with weather conditions.
        Compare historical weather with current weather and generate clear, professional comparisons.
        
        Args:
            raw_results: List of raw Tavily search results
            current_weather: Current weather conditions for comparison
            location: Location name
            country: Country name
            
        Returns:
            List of refined results with weather comparisons
        """
        if not raw_results:
            return []
        
        try:
            # Prepare current weather summary for comparison
            current_weather_summary = ""
            if current_weather:
                daily_weather = current_weather.get("daily_weather", {})
                temp_mean = daily_weather.get("temperature_2m_mean", [])
                hum_mean = daily_weather.get("relative_humidity_2m_mean", [])
                precip = daily_weather.get("precipitation_sum", [])
                
                if temp_mean:
                    current_weather_summary += f"Current Temperature: {temp_mean[0] if temp_mean else 'N/A'}°C (avg)\n"
                if hum_mean:
                    current_weather_summary += f"Current Humidity: {hum_mean[0] if hum_mean else 'N/A'}% (avg)\n"
                if precip:
                    current_weather_summary += f"Current Precipitation: {precip[0] if precip else 'N/A'}mm\n"
            
            # Prepare raw content for LLM processing
            raw_content = []
            for i, result in enumerate(raw_results, 1):
                title = result.get("title", f"Result {i}")
                content = result.get("content", "")
                url = result.get("url", "")
                raw_content.append(f"Result {i}:\nTitle: {title}\nContent: {content}\nURL: {url}")
            
            raw_text = "\n\n---\n\n".join(raw_content)
            
            # Create enhanced prompt for extracting historical data and comparing weather
            system_prompt = """You are an expert agricultural analyst specializing in plant disease outbreaks and weather pattern analysis.
Your task is to extract historical outbreak information, identify weather conditions during those outbreaks, and compare them with current conditions.

STREAMING BEHAVIOR:
Process historical data step-by-step and communicate what you're doing naturally. Do not mention progress, loading, or percentages. Instead, describe what you're analyzing in conversational language like "Extracting historical outbreak dates..." or "Comparing weather conditions with current data...". Stream your outputs in stages, with each section being complete and self-contained.

Guidelines:
- Extract specific dates (year, month, season) from historical outbreaks
- Identify weather conditions mentioned (temperature, humidity, rainfall, etc.)
- Compare historical weather with current weather conditions
- Generate clear, professional sentences explaining similarities
- Remove technical jargon and make content readable
- Highlight key similarities that indicate risk
- Use professional agricultural terminology
- Do NOT mention progress percentages, loading states, or step counters"""
            
            user_prompt = f"""Analyze the following research data about historical {location}, {country} potato disease outbreaks.
Extract outbreak dates, weather conditions during outbreaks, and compare them with current conditions.

CURRENT WEATHER CONDITIONS:
{current_weather_summary if current_weather_summary else "Current weather data not available"}

RAW RESEARCH DATA:
{raw_text}

For each historical outbreak found, provide:
1. **Outbreak Date**: Specific date, year, or season if mentioned
2. **Historical Weather Conditions**: Temperature, humidity, rainfall during the outbreak
3. **Similarities with Current Conditions**: Clear comparison explaining how current weather matches historical outbreak conditions
4. **Risk Assessment**: Professional assessment of whether similar conditions indicate elevated risk

Format your response as JSON:
{{
    "refined_results": [
        {{
            "title": "Clear title describing the outbreak",
            "outbreak_date": "Date or year of outbreak (e.g., 'November 2023', '2022', 'Winter 2021')",
            "historical_weather": {{
                "temperature": "Temperature range or average during outbreak",
                "humidity": "Humidity levels during outbreak",
                "rainfall": "Rainfall amounts during outbreak",
                "other_conditions": "Any other relevant weather conditions"
            }},
            "summary": "2-3 clear, professional sentences summarizing the outbreak and its conditions",
            "similarities_with_current": "2-3 clear, well-written sentences explaining how current weather conditions are similar to the historical outbreak conditions. Be specific about temperature, humidity, and rainfall comparisons.",
            "risk_implication": "1-2 professional sentences explaining what this similarity means for current disease risk",
            "key_points": ["Key point 1", "Key point 2", "Key point 3"],
            "source_name": "Extracted source name from URL",
            "url": "original_url"
        }}
    ]
}}

Important:
- Extract dates and weather conditions accurately from the content
- Write clear, professional sentences (not technical jargon)
- Make comparisons specific and actionable
- If no weather data is found in a result, still extract the date and provide general context
- Focus on the MOST RECENT outbreaks first

Respond ONLY with valid JSON - no additional text."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use a more capable model for better analysis
            analyzer_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                max_tokens=2000
            )
            
            response = analyzer_llm.invoke(messages)
            result_text = response.content.strip()
            
            # Debug: Log raw response
            print(f"[TAVILY_DEBUG] Raw LLM response (with weather) length: {len(result_text)} chars")
            print(f"[TAVILY_DEBUG] Raw response preview: {result_text[:200]}...")
            
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Additional cleaning: Remove any remaining markdown or AI references
            import re
            # Remove markdown headers
            result_text = re.sub(r'^#+\s*', '', result_text, flags=re.MULTILINE)
            # Remove AI service references
            result_text = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model|generated by|created by AI)\b', '', result_text, flags=re.IGNORECASE)
            
            parsed = json.loads(result_text)
            refined_results = parsed.get("refined_results", [])
            
            # Debug: Log refined results
            print(f"[TAVILY_DEBUG] Refined {len(refined_results)} results with weather comparison")
            
            # Post-process: Clean each refined result (same as _refine_tavily_results)
            for refined in refined_results:
                # Remove markdown from title
                if refined.get("title"):
                    refined["title"] = re.sub(r'^#+\s*', '', refined["title"]).strip()
                    refined["title"] = re.sub(r'\*\*(.*?)\*\*', r'\1', refined["title"])
                    refined["title"] = re.sub(r'\*(.*?)\*', r'\1', refined["title"])
                
                # Remove markdown from summary
                if refined.get("summary"):
                    refined["summary"] = re.sub(r'^#+\s*', '', refined["summary"], flags=re.MULTILINE)
                    refined["summary"] = re.sub(r'\*\*(.*?)\*\*', r'\1', refined["summary"])
                    refined["summary"] = re.sub(r'\*(.*?)\*', r'\1', refined["summary"])
                    refined["summary"] = re.sub(r'`(.*?)`', r'\1', refined["summary"])
                    refined["summary"] = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model)\b', '', refined["summary"], flags=re.IGNORECASE)
                    refined["summary"] = refined["summary"].strip()
                
                # Clean key points
                if refined.get("key_points"):
                    cleaned_points = []
                    for point in refined["key_points"]:
                        cleaned = re.sub(r'^#+\s*', '', point)
                        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
                        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
                        cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)
                        cleaned = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model)\b', '', cleaned, flags=re.IGNORECASE)
                        cleaned = cleaned.strip()
                        if cleaned:
                            cleaned_points.append(cleaned)
                    refined["key_points"] = cleaned_points
            
            # Merge with original URLs and metadata, extract source names
            for i, refined in enumerate(refined_results):
                if i < len(raw_results):
                    original_url = raw_results[i].get("url", "")
                    refined["original_url"] = original_url
                    if not refined.get("url"):
                        refined["url"] = original_url
                    
                    # Extract source name from URL if not provided
                    if not refined.get("source_name") and original_url:
                        try:
                            from urllib.parse import urlparse
                            parsed_url = urlparse(original_url)
                            domain = parsed_url.netloc.replace("www.", "")
                            if domain:
                                parts = domain.split(".")
                                if len(parts) > 0:
                                    source_name = parts[0].capitalize()
                                    if "academia" in domain:
                                        source_name = "Academia.edu"
                                    elif "intechopen" in domain:
                                        source_name = "IntechOpen"
                                    elif "mdpi" in domain:
                                        source_name = "MDPI"
                                    elif "pmc" in domain or "ncbi" in domain:
                                        source_name = "PubMed Central"
                                    refined["source_name"] = source_name
                        except Exception:
                            pass
            
            return refined_results
            
        except Exception as e:
            print(f"[WARNING] Failed to refine Tavily results with weather comparison: {e}")
            import traceback
            traceback.print_exc()
            # Return basic refined results if weather comparison fails
            return self._refine_tavily_results(raw_results, "historical_context")
    
    def _format_tavily_section(self, tavily_data: Dict[str, Any], location: str, country: str, 
                               result: Dict[str, Any], weather_dataset: Dict) -> str:
        """
        Format all Tavily data into a well-structured, readable markdown section using OpenAI.
        Creates a professional report with proper hierarchy, clickable links, and clear sections.
        
        Args:
            tavily_data: Dict with all Tavily results for each disease
            location: Location name
            country: Country name
            result: Main prediction result (for context)
            weather_dataset: Weather dataset (for context)
            
        Returns:
            Formatted markdown string with structured Tavily recommendations
        """
        if not tavily_data or not any(any(data.values()) for data in tavily_data.values()):
            return ""
        
        try:
            # Prepare context from prediction result
            location_data = weather_dataset.get("location", {})
            analysis_date = result.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
            growth_stage = result.get("growth_stage", "Unknown")
            days_after_planting = result.get("days_after_planting", "N/A")
            elevation = location_data.get("elevation", "N/A")
            
            # Collect all raw Tavily data for formatting
            all_tavily_content = []
            for disease_name, disease_data in tavily_data.items():
                if not any(disease_data.values()):
                    continue
                
                disease_section = {
                    "disease": disease_name,
                    "historical_context": disease_data.get("historical_context", []),
                    "recommendations": disease_data.get("recommendations", []),
                    "preventive_measures": disease_data.get("preventive_measures", [])
                }
                all_tavily_content.append(disease_section)
            
            if not all_tavily_content:
                return ""
            
            # Prepare raw content for OpenAI formatting
            raw_content_text = json.dumps(all_tavily_content, indent=2)
            
            # Create comprehensive formatting prompt
            system_prompt = """You are an expert agricultural report writer specializing in plant disease management.
Your task is to transform raw research data into a well-structured, professional markdown report.

STREAMING BEHAVIOR:
Process and format each section completely before moving to the next. Do not mention progress, loading, or percentages. Instead, communicate naturally like "Formatting historical outbreak data..." or "Structuring treatment recommendations...". Stream your outputs in stages, with each section being complete and self-contained.

CRITICAL FORMATTING RULES:
- START your response directly with "## 📚 Location-Specific Research & Historical Context" - do NOT include any headers before this
- Do NOT include headers like "## 🌿 Key Environmental Observations" or any other headers before the main Location-Specific header
- Do NOT mention AI services: "ChatGPT", "OpenAI", "ChatOpenAI", "chatopen ai", "AI assistant", "AI model", etc.
- Do NOT include duplicate "Location-Specific Research" headers - only include it once at the start
- PRESERVE location-specific data: dates, locations, weather conditions, historical outbreaks
- PRESERVE actionable recommendations: fungicide names, dosages, application rates, treatment methods

Guidelines:
- Create clear hierarchical structure with proper markdown headers (##, ###) - but ONLY after the main header
- Format links as clickable markdown: [Link Text](URL)
- Extract and label source domains (e.g., "IntechOpen", "Academia.edu", "NACL Industries")
- Remove redundancy while preserving all critical technical details
- Highlight actionable recommendations with clear formatting
- Use bullet points and numbered lists for readability
- Maintain scientific accuracy and terminology
- Group related information logically
- Add emoji icons for visual hierarchy (🥔, 🌦, 🧬, 🌿, 🧪, 📚, 🗓)
- Ensure all links are properly formatted and clickable
- Do NOT mention progress percentages, loading states, or step counters
- Do NOT mention AI tools, models, or services"""
            
            user_prompt = f"""Transform the following raw Tavily research data into a well-structured markdown section for a potato disease risk report.

CONTEXT:
- Location: {location}, {country}
- Elevation: {elevation}m
- Growth Stage: {growth_stage} ({days_after_planting} days after planting)
- Analysis Date: {analysis_date}

RAW TAVILY DATA (JSON):
{raw_content_text}

Create a structured markdown section titled "📚 Location-Specific Research & Historical Context" that includes:

1. **Historical Outbreak Analysis** (if available):
   - For each historical outbreak, clearly state:
     * **Outbreak Date**: When it occurred (e.g., "November 2023", "Winter 2022")
     * **Historical Weather Conditions**: Temperature, humidity, rainfall during the outbreak
     * **Weather Similarities**: Clear, well-written sentences comparing historical weather with current conditions
       Example: "The current temperature of 18°C and humidity of 85% closely match conditions during the November 2023 outbreak in {location}, when temperatures averaged 17-19°C with 82-88% humidity."
     * **Risk Implication**: What this similarity means for current disease risk
   - Write in clear, professional sentences (not bullet points for the comparisons)
   - Make the weather comparisons specific and actionable
   - Highlight the most recent outbreaks first

2. **Management Recommendations**:
   - Actionable treatment recommendations
   - Specific fungicides/products if mentioned
   - Application methods and timing

3. **Preventive Measures**:
   - Cultural practices
   - Preventive treatments
   - Field management tips

4. **References** (as clickable links):
   - Format as: [Source Name – Article Title](URL)
   - Extract meaningful source names from URLs
   - Group by disease if multiple diseases

Requirements:
- Use proper markdown formatting (##, ###, **bold**, *italic*)
- Make ALL links clickable markdown format: [Text](URL)
- Write clear, professional sentences for weather comparisons (not technical jargon)
- For historical context, use paragraphs with clear sentences explaining the similarities
- Remove copyright notices, citation metadata, redundant text
- Keep technical details but make them concise and readable
- Use bullet points only for lists of recommendations
- Add clear section separators (---)
- Ensure professional, readable formatting
- Make sentences flow naturally and be grammatically correct

Example format for historical context:
**Historical Outbreak - November 2023:**
During the November 2023 outbreak in {location}, weather conditions included average temperatures of 17-19°C and relative humidity levels of 82-88%. Current conditions show temperatures of 18°C with 85% humidity, closely matching these historical outbreak conditions. This similarity suggests elevated disease risk, as the pathogen thrives under these specific temperature and humidity ranges.

Respond ONLY with the formatted markdown section - no additional text or explanations."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use a more capable model for better formatting
            formatter_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                max_tokens=2000
            )
            
            response = formatter_llm.invoke(messages)
            formatted_section = response.content.strip()
            
            # Debug: Log raw formatted section
            print(f"[TAVILY_DEBUG] Raw formatted section length: {len(formatted_section)} chars")
            print(f"[TAVILY_DEBUG] Raw formatted preview: {formatted_section[:300]}...")
            
            # Clean up any markdown code blocks if present
            if formatted_section.startswith("```"):
                # Extract content from code block
                if "```markdown" in formatted_section:
                    formatted_section = formatted_section.split("```markdown")[1].split("```")[0].strip()
                elif "```" in formatted_section:
                    formatted_section = formatted_section.split("```")[1].split("```")[0].strip()
            
            # Post-process: Remove unwanted markdown headers at the start and AI references
            import re
            
            # Remove leading markdown headers (but keep section headers inside)
            # Only remove if they're at the very start of the document
            formatted_section = re.sub(r'^#+\s*📚\s*Location-Specific', '## 📚 Location-Specific Research & Historical Context', formatted_section, flags=re.MULTILINE)
            formatted_section = re.sub(r'^#+\s*Location-Specific', '## 📚 Location-Specific Research & Historical Context', formatted_section, flags=re.MULTILINE)
            
            # Remove duplicate section headers - FIXED: Handle "Research & Historical Context Research & Historical Context"
            # First, fix the duplicate "Research & Historical Context" pattern
            formatted_section = re.sub(
                r'📚\s*Location-Specific\s+Research[^\n]*\s+Research[^\n]*\s+Historical\s+Context',
                '📚 Location-Specific Research & Historical Context',
                formatted_section,
                flags=re.IGNORECASE
            )
            
            # Count occurrences of "Location-Specific Research"
            location_header_count = len(re.findall(r'📚\s*Location-Specific\s+Research', formatted_section, re.IGNORECASE))
            if location_header_count > 1:
                print(f"[TAVILY_DEBUG] Found {location_header_count} duplicate Location-Specific headers, removing duplicates")
                # Keep only the first occurrence
                parts = re.split(r'📚\s*Location-Specific\s+Research', formatted_section, flags=re.IGNORECASE)
                if len(parts) > 1:
                    formatted_section = '📚 Location-Specific Research & Historical Context' + parts[1]
            
            # Remove AI service references
            formatted_section = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model|generated by|created by AI|powered by AI)\b', '', formatted_section, flags=re.IGNORECASE)
            
            # Remove unwanted standalone headers that might appear (like "## 🌿 Key Environmental Observations")
            # But preserve legitimate section headers within the Tavily section
            # Remove headers that appear before the main Location-Specific header
            lines = formatted_section.split('\n')
            cleaned_lines = []
            found_main_header = False
            for line in lines:
                # If we find the main header, mark it and keep it
                if re.match(r'^##\s*📚\s*Location-Specific', line, re.IGNORECASE):
                    found_main_header = True
                    cleaned_lines.append(line)
                # If we haven't found the main header yet, skip other headers
                elif not found_main_header and re.match(r'^#+\s*', line):
                    print(f"[TAVILY_DEBUG] Removing unwanted header before main section: {line[:50]}")
                    continue
                else:
                    cleaned_lines.append(line)
            
            formatted_section = '\n'.join(cleaned_lines)
            
            # Clean up extra whitespace
            formatted_section = re.sub(r'\n{3,}', '\n\n', formatted_section)
            formatted_section = formatted_section.strip()
            
            # Debug: Log cleaned section
            print(f"[TAVILY_DEBUG] Cleaned formatted section length: {len(formatted_section)} chars")
            print(f"[TAVILY_DEBUG] Cleaned formatted preview: {formatted_section[:300]}...")
            
            return formatted_section
            
        except Exception as e:
            print(f"[WARNING] Failed to format Tavily section: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic formatting
            return self._format_tavily_section_fallback(tavily_data, location, country)
    
    def _format_tavily_section_fallback(self, tavily_data: Dict[str, Any], location: str, country: str) -> str:
        """
        Fallback formatting if OpenAI formatting fails.
        Creates basic structured output.
        """
        if not tavily_data:
            return ""
        
        section = "\n## 📚 Location-Specific Research & References\n\n"
        
        for disease_name, disease_data in tavily_data.items():
            if not any(disease_data.values()):
                continue
            
            section += f"### {disease_name}\n\n"
            
            # Historical Context with Weather Comparisons
            if disease_data.get("historical_context"):
                section += "### Historical Outbreak Analysis\n\n"
                for hist in disease_data["historical_context"]:
                    title = hist.get("title", "Historical Data")
                    outbreak_date = hist.get("outbreak_date", "")
                    historical_weather = hist.get("historical_weather", {})
                    similarities = hist.get("similarities_with_current", "")
                    risk_implication = hist.get("risk_implication", "")
                    summary = hist.get("summary", hist.get("content", ""))
                    url = hist.get("url") or hist.get("original_url", "")
                    source_name = hist.get("source_name", "")
                    
                    # Format outbreak with date and weather comparison
                    if outbreak_date:
                        section += f"**Historical Outbreak - {outbreak_date}:**\n\n"
                    
                    # Historical weather conditions
                    if historical_weather:
                        section += "**Historical Weather Conditions:**\n"
                        if historical_weather.get("temperature"):
                            section += f"- Temperature: {historical_weather.get('temperature')}\n"
                        if historical_weather.get("humidity"):
                            section += f"- Humidity: {historical_weather.get('humidity')}\n"
                        if historical_weather.get("rainfall"):
                            section += f"- Rainfall: {historical_weather.get('rainfall')}\n"
                        section += "\n"
                    
                    # Weather similarities (clear sentences)
                    if similarities:
                        section += f"{similarities}\n\n"
                    
                    # Risk implication
                    if risk_implication:
                        section += f"**Risk Assessment:** {risk_implication}\n\n"
                    
                    # Summary if no specific fields
                    if summary and not similarities:
                        section += f"{summary}\n\n"
                    
                    # Source link
                    if url:
                        if source_name:
                            link_text = f"{source_name} – {title}"
                        else:
                            try:
                                from urllib.parse import urlparse
                                domain = urlparse(url).netloc.replace("www.", "")
                                link_text = domain if domain else title
                            except:
                                link_text = title
                        section += f"Source: [{link_text}]({url})\n\n"
                    
                    section += "---\n\n"
            
            # Recommendations
            if disease_data.get("recommendations"):
                section += "**Management Recommendations:**\n\n"
                for rec in disease_data["recommendations"]:
                    title = rec.get("title", "Recommendation")
                    summary = rec.get("summary", rec.get("content", ""))
                    url = rec.get("url") or rec.get("original_url", "")
                    source_name = rec.get("source_name", "")
                    
                    if summary:
                        section += f"- {summary}\n"
                    if url:
                        if source_name:
                            link_text = f"{source_name} – {title}"
                        else:
                            try:
                                from urllib.parse import urlparse
                                domain = urlparse(url).netloc.replace("www.", "")
                                link_text = domain if domain else title
                            except:
                                link_text = title
                        section += f"  Source: [{link_text}]({url})\n"
                section += "\n"
            
            # Preventive Measures
            if disease_data.get("preventive_measures"):
                section += "**Preventive Measures:**\n\n"
                for prev in disease_data["preventive_measures"]:
                    title = prev.get("title", "Prevention")
                    summary = prev.get("summary", prev.get("content", ""))
                    url = prev.get("url") or prev.get("original_url", "")
                    source_name = prev.get("source_name", "")
                    
                    if summary:
                        section += f"- {summary}\n"
                    if url:
                        if source_name:
                            link_text = f"{source_name} – {title}"
                        else:
                            try:
                                from urllib.parse import urlparse
                                domain = urlparse(url).netloc.replace("www.", "")
                                link_text = domain if domain else title
                            except:
                                link_text = title
                        section += f"  Source: [{link_text}]({url})\n"
                section += "\n"
        
        return section
    
    def _generate_report(self, result: Dict[str, Any], weather_dataset: Dict) -> str:
        """
        Generate beautiful, natural language report with Tavily-powered recommendations.
        Uses OpenAI to transform structured data into professional, readable prose.
        
        Args:
            result: Parsed JSON result from LLM
            weather_dataset: Original weather dataset
            
        Returns:
            Beautiful formatted natural language report string
        """
        location_data = weather_dataset.get("location", {})
        # Get country from location data first, then result, with no default assumption
        country = location_data.get('country') or result.get('country', 'Unknown')
        location = result.get('location', 'N/A')
        
        # Use OpenAI to generate beautiful natural language report
        try:
            # Extract daily weather data for temperature analysis
            daily_weather = weather_dataset.get("daily_weather", {})
            temperature_data = {
                "dates": daily_weather.get("date", []),
                "min_temperatures": daily_weather.get("temperature_2m_min", []),
                "max_temperatures": daily_weather.get("temperature_2m_max", []),
                "mean_temperatures": daily_weather.get("temperature_2m_mean", []),
                "humidity": daily_weather.get("relative_humidity_2m_mean", [])
            }
            
            report_prompt = f"""Transform the following structured disease risk analysis data into a beautiful, professional, natural language report.

STRUCTURED DATA:
{json.dumps(result, indent=2)}

WEATHER DATASET LOCATION:
{json.dumps(location_data, indent=2)}

DAILY TEMPERATURE DATA FROM API (Use this for Temperature Analysis section):
{json.dumps(temperature_data, indent=2)}

IMPORTANT: Extract and explain ALL temperature values from the daily temperature data above. Include specific dates, minimum and maximum temperatures, and explain how these temperatures influence disease risk in natural, conversational language.

CRITICAL FORMATTING RULES:
- DO NOT use markdown headers (##, ###, #) - write plain text with emoji icons only
- DO NOT use markdown bold (**text**) or italic (*text*) - write naturally without formatting
- DO NOT use asterisks (*) or hashtags (#) anywhere in the text
- Write in plain, natural language without any markdown syntax
- Use emoji icons (🌦️, 🧬, 🌿, 🧪, 📚, 📅) for visual sections but NO markdown headers

INSTRUCTIONS:
- Write in clear, professional, natural language (NOT JSON format, NO markdown)
- Make it conversational and easy to read
- Include all key information from the structured data
- Write complete sentences and paragraphs, not bullet points for main content
- Use emoji icons for visual hierarchy (🌦️, 🧬, 🌿, 🧪, 📚) but NO markdown headers
- Format recommendations as actionable, clear instructions
- Make the report feel like it's written by an expert agricultural consultant

OUTPUT FORMAT:
🌦️ Field & Weather Information
[Natural language description of location, elevation, analysis date, growth stage]

🌡️ Temperature Analysis
[Natural language description of temperature patterns from the API data. Include:
- Daily minimum and maximum temperatures observed
- Average temperature trends over the analysis period
- Temperature ranges and how they compare to ideal conditions
- Specific dates with notable temperature values
- How temperature patterns influence disease risk
Write this in conversational, informative language - make it feel like an expert explaining the weather data]

🧬 Disease Risk Assessment
[Natural language explanation of Late Blight and Early Blight risks with percentages]
[Explain what the risk levels mean in practical terms]

🌿 Key Environmental Observations
[Natural language description of critical weather observations and environmental factors]

🧪 Recommendations
[Natural language actionable recommendations with specific fungicides, dosages, and timing]

📅 Weekly Outlook
[Natural language summary of disease risk for next 7 days]

IMPORTANT:
- DO NOT include "Location-Specific Research & Historical Context" section in your output - it will be added automatically if data is available
- DO NOT output JSON format
- DO NOT use markdown syntax (##, ###, **, *)
- Write in beautiful, natural, professional English
- Make it readable and engaging
- Use complete sentences and paragraphs
- Include specific values (temperatures, percentages, dates) naturally in the text
- For temperature section, extract and explain ALL temperature data from the weather dataset in natural language

Generate the report now:"""
            
            formatter_llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=2000
            )
            
            response = formatter_llm.invoke(report_prompt)
            formatted_report = response.content.strip()
            
            # Clean up any markdown code blocks if present
            if formatted_report.startswith("```"):
                if "```markdown" in formatted_report:
                    formatted_report = formatted_report.split("```markdown")[1].split("```")[0].strip()
                elif "```" in formatted_report:
                    formatted_report = formatted_report.split("```")[1].split("```")[0].strip()
            
            # Post-process: Remove ALL markdown formatting (stars, hashtags)
            import re
            # Remove markdown headers (##, ###, #)
            formatted_report = re.sub(r'^#+\s*', '', formatted_report, flags=re.MULTILINE)
            # Remove markdown bold (**text**)
            formatted_report = re.sub(r'\*\*(.*?)\*\*', r'\1', formatted_report)
            # Remove markdown italic (*text*)
            formatted_report = re.sub(r'\*(.*?)\*', r'\1', formatted_report)
            # Remove standalone asterisks
            formatted_report = re.sub(r'\s+\*\s+', ' ', formatted_report)
            # Remove any remaining hashtags (but keep emoji)
            formatted_report = re.sub(r'#+', '', formatted_report)
            
            # CRITICAL FIX: Remove placeholder text for Location-Specific Research
            # Remove lines that contain placeholder text
            formatted_report = re.sub(
                r'📚\s*Location-Specific\s+Research[^\n]*\n[^\n]*This section will be added[^\n]*\n?',
                '',
                formatted_report,
                flags=re.IGNORECASE | re.MULTILINE
            )
            formatted_report = re.sub(
                r'📚\s*Location-Specific[^\n]*\n[^\n]*will be added separately[^\n]*\n?',
                '',
                formatted_report,
                flags=re.IGNORECASE | re.MULTILINE
            )
            formatted_report = re.sub(
                r'📚\s*Location-Specific[^\n]*\n[^\n]*\[This will be added[^\n]*\n?',
                '',
                formatted_report,
                flags=re.IGNORECASE | re.MULTILINE
            )
            
            # Remove duplicate "Location-Specific Research & Historical Context" headers
            # Keep only the first occurrence if there are duplicates
            location_header_pattern = r'📚\s*Location-Specific\s+Research[^\n]*'
            location_headers = list(re.finditer(location_header_pattern, formatted_report, re.IGNORECASE | re.MULTILINE))
            if len(location_headers) > 1:
                print(f"[REPORT_CLEAN] Found {len(location_headers)} duplicate Location-Specific headers, removing duplicates")
                # Keep only the first one, remove the rest
                for match in location_headers[1:]:
                    # Remove the duplicate header and any text until next section or end
                    start = match.start()
                    # Find next section marker or end of string
                    next_section = re.search(r'\n📅|\n🧪|\n🌿|\n🌡️|\n🌦️|\n🧬|\Z', formatted_report[start:], re.MULTILINE)
                    if next_section:
                        end = start + next_section.start()
                        formatted_report = formatted_report[:start] + formatted_report[end:]
                    else:
                        formatted_report = formatted_report[:start]
                    break  # Only remove first duplicate
            
            # Clean up extra whitespace
            formatted_report = re.sub(r'\n{3,}', '\n\n', formatted_report)
            formatted_report = formatted_report.strip()
            
            print(f"[REPORT_CLEAN] Removed markdown formatting and placeholder text from report")
            
            # Add Tavily section if available
            tavily_data = result.get('tavily_data', {})
            location_for_tavily = location_data.get('city', location or 'Unknown')
            
            if tavily_data and any(any(data.values()) for data in tavily_data.values()):
                tavily_section = self._format_tavily_section(
                    tavily_data=tavily_data,
                    location=location_for_tavily,
                    country=country,
                    result=result,
                    weather_dataset=weather_dataset
                )
                
                if tavily_section:
                    # Clean Tavily section from markdown too
                    tavily_section = re.sub(r'^#+\s*', '', tavily_section, flags=re.MULTILINE)
                    tavily_section = re.sub(r'\*\*(.*?)\*\*', r'\1', tavily_section)
                    tavily_section = re.sub(r'\*(.*?)\*', r'\1', tavily_section)
                    tavily_section = re.sub(r'#+', '', tavily_section)
                    
                    # Remove duplicate headers from Tavily section
                    tavily_section = re.sub(
                        r'📚\s*Location-Specific\s+Research[^\n]*\s+Research[^\n]*\s+Historical\s+Context',
                        '📚 Location-Specific Research & Historical Context',
                        tavily_section,
                        flags=re.IGNORECASE
                    )
                    
                    # Insert Tavily section before Weekly Outlook, replacing any placeholder
                    if "📅 Weekly Outlook" in formatted_report:
                        # Remove any existing placeholder Location-Specific section
                        formatted_report = re.sub(
                            r'📚\s*Location-Specific[^\n]*\n[^\n]*(?:NOTE|This section|will be added)[^\n]*\n?\n?',
                            '',
                            formatted_report,
                            flags=re.IGNORECASE | re.MULTILINE
                        )
                        formatted_report = formatted_report.replace(
                            "📅 Weekly Outlook",
                            tavily_section + "\n\n📅 Weekly Outlook"
                        )
                    else:
                        # Remove any existing placeholder
                        formatted_report = re.sub(
                            r'📚\s*Location-Specific[^\n]*\n[^\n]*(?:NOTE|This section|will be added)[^\n]*\n?\n?',
                            '',
                            formatted_report,
                            flags=re.IGNORECASE | re.MULTILINE
                        )
                        formatted_report += "\n\n" + tavily_section
            
            return formatted_report
            
        except Exception as e:
            print(f"[WARNING] Failed to generate beautiful report with OpenAI: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic formatting
            return self._generate_report_fallback(result, weather_dataset)
    
    def _generate_report_fallback(self, result: Dict[str, Any], weather_dataset: Dict) -> str:
        """
        Fallback report generation if OpenAI formatting fails.
        Creates basic natural language report.
        """
        location_data = weather_dataset.get("location", {})
        # Get country from location data first (most accurate from geocoding API)
        country = location_data.get('country', None)
        if not country:
            country = result.get('country', 'Unknown')
        location = result.get('location', 'N/A')
        
        # Header
        report = "## 🌦️ Field & Weather Information\n\n"
        report += f"**Location:** {location}, {country}\n"
        report += f"**Elevation:** {result.get('elevation', 'N/A')}m\n"
        report += f"**Analysis Date:** {result.get('analysis_date', 'N/A')}\n"
        report += f"**Growth Stage:** {result.get('growth_stage', 'N/A')} ({result.get('days_after_planting', 'N/A')} days after planting)\n\n"
        
        # Hutton Criteria for UK
        if country == "UK" and result.get('hutton_criteria'):
            hc = result.get('hutton_criteria', {})
            report += "HUTTON CRITERIA STATUS\n\n"
            if hc.get('met'):
                report += "Status: MET - HIGH RISK PERIOD\n"
                report += f"Consecutive days meeting criteria: {hc.get('consecutive_days', 0)}\n"
                report += "⚠️ IMMEDIATE FUNGICIDE APPLICATION RECOMMENDED\n\n"
            else:
                report += "Status: Not Met\n\n"
        
        # Risk Assessment Section
        report += "RISK ASSESSMENT\n\n"
        report += f"Overall Disease Pressure: {result.get('overall_disease_pressure', 'N/A').upper()}\n\n"
        
        # Late Blight Risk
        lb = result.get('late_blight_risk', {})
        report += "Late Blight Risk (Primary Concern)\n"
        report += f"  Risk Level: {lb.get('risk_level', 'N/A').upper()} ({lb.get('risk_percentage', 0)}%)\n"
        if lb.get('peak_risk_days'):
            report += f"  Peak Risk Days: {', '.join(lb.get('peak_risk_days', []))}\n"
        report += f"  Summary: {lb.get('weather_summary', 'N/A')}\n"
        if lb.get('key_risk_factors'):
            report += "  Key Risk Factors:\n"
            for factor in lb.get('key_risk_factors', []):
                report += f"    - {factor}\n"
        report += "\n"
        
        # Early Blight Risk
        eb = result.get('early_blight_risk', {})
        report += "Early Blight Risk (Secondary Concern)\n"
        report += f"  Risk Level: {eb.get('risk_level', 'N/A').upper()} ({eb.get('risk_percentage', 0)}%)\n"
        if eb.get('peak_risk_days'):
            report += f"  Peak Risk Days: {', '.join(eb.get('peak_risk_days', []))}\n"
        report += f"  Summary: {eb.get('weather_summary', 'N/A')}\n\n"
        
        # Critical Observations
        if result.get('critical_weather_observations'):
            report += "CRITICAL WEATHER OBSERVATIONS\n\n"
            for obs in result.get('critical_weather_observations', []):
                report += f"• {obs}\n"
            report += "\n"
        
        # Environmental Factors
        report += "ENVIRONMENTAL FACTORS\n\n"
        
        aq = result.get('air_quality_impact', {})
        if aq:
            report += f"Air Quality: PM2.5 Concern - {aq.get('pm25_concern', 'N/A').upper()}\n"
            report += f"  PM2.5 Values: {aq.get('pm25_values', 'N/A')}\n"
            report += f"  Impact: {aq.get('impact_on_disease', 'N/A')}\n"
        
        soil = result.get('soil_conditions_analysis', {})
        if soil:
            report += f"Soil Conditions: {soil.get('moisture_status', 'N/A').replace('_', ' ').title()}\n"
            report += f"  Soil Temperature Range: {soil.get('soil_temp_range', 'N/A')}\n"
            report += f"  Impact: {soil.get('impact_on_disease', 'N/A')}\n"
        report += "\n"
        
        # Get Tavily recommendations from stored data (already fetched for ALL diseases)
        tavily_data = result.get('tavily_data', {})
        location_for_tavily = location_data.get('city', location or 'Unknown')
        
        # Final Conclusion Section
        report += "\nFINAL CONCLUSION\n\n"
        
        overall_pressure = result.get('overall_disease_pressure', 'moderate').upper()
        report += f"Based on comprehensive analysis of weather conditions, crop stage, and environmental factors, "
        report += f"the overall disease pressure for your potato crop is {overall_pressure}.\n\n"
        
        # Risk Summary
        report += "Risk Summary:\n"
        report += f"• Late Blight: {lb.get('risk_level', 'N/A').upper()} ({lb.get('risk_percentage', 0)}%)\n"
        report += f"• Early Blight: {eb.get('risk_level', 'N/A').upper()} ({eb.get('risk_percentage', 0)}%)\n\n"
        
        # Recommendations Section
        report += "\nRECOMMENDATIONS\n\n"
        
        if result.get('immediate_actions'):
            report += "Immediate Actions Required:\n"
            for i, action in enumerate(result.get('immediate_actions', []), 1):
                report += f"{i}. {action}\n"
            report += "\n"
        
        if result.get('preventive_recommendations'):
            report += "Preventive Measures:\n"
            for i, rec in enumerate(result.get('preventive_recommendations', []), 1):
                report += f"{i}. {rec}\n"
            report += "\n"
        
        # Add Tavily-powered recommendations with structured formatting
        if tavily_data and any(any(data.values()) for data in tavily_data.values()):
            # Use OpenAI to format Tavily section into structured markdown
            tavily_section = self._format_tavily_section(
                tavily_data=tavily_data,
                location=location_for_tavily,
                country=country,
                result=result,
                weather_dataset=weather_dataset
            )
            
            if tavily_section:
                report += "\n" + tavily_section + "\n"
            else:
                # Fallback to basic formatting if OpenAI formatting fails
                report += "\n## 📚 Location-Specific Research & References\n\n"
                report += f"*Research data for {location_for_tavily}, {country} is available. Please check the detailed recommendations above.*\n\n"
        
        # Weekly Outlook
        report += f"\nWeekly Outlook:\n{result.get('weekly_outlook', 'N/A')}\n\n"
        
        # Confidence
        report += f"Confidence Level: {result.get('confidence_level', 'N/A').upper()}\n"
        report += f"{result.get('confidence_explanation', 'N/A')}\n\n"
        
        # Footer
        report += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Data Sources: {result.get('data_source', 'Open-Meteo API')}"
        if tavily_data and any(any(data.values()) for data in tavily_data.values()):
            report += ", Tavily Research\n"
        else:
            report += "\n"
        
        return report
    
    def _translate_response(self, english_text: str, target_languages: list = None) -> Dict[str, str]:
        """
        Translate the English report into requested languages using OpenAI.
        Args:
            english_text: The English text to translate
            target_languages: List of language codes to translate to (e.g., ["telugu", "hindi"])
        Returns:
            Dictionary with translations for each requested language
        """
        translations = {}
        
        # Define all available languages with their native names
        all_languages = {
            "telugu": "Telugu (తెలుగు)",
            "hindi": "Hindi (हिंदी)",
            "tamil": "Tamil (தமிழ்)"
        }
        
        # If no specific languages requested, return empty dict
        if not target_languages:
            return translations
        
        # Only translate to requested languages
        languages_to_translate = {
            lang: all_languages[lang] 
            for lang in target_languages 
            if lang in all_languages
        }
        
        # Translate to each requested language
        for lang_key, lang_name in languages_to_translate.items():
            try:
                translation_prompt = f"""You are a professional translator specializing in agricultural and technical content.

Translate the following English text into {lang_name}. 

IMPORTANT GUIDELINES:
1. Maintain the same tone and formality as the original
2. Keep technical terms related to agriculture and disease accurate
3. If a technical term has no direct translation, keep it in English with a brief explanation in {lang_name}
4. Preserve any formatting (markdown, line breaks, bullet points, emojis, etc.)
5. Make the translation natural and fluent for native speakers
6. Keep disease names (Late Blight, Early Blight) in English but explain their nature
7. Maintain all numerical values, percentages, and dates exactly as they appear
8. Keep section headers clear and formatted

English text to translate:
{english_text}

Provide ONLY the {lang_name} translation (no explanations or notes):"""

                translation_response = self.translation_llm.invoke(translation_prompt)
                translations[lang_key] = translation_response.content.strip()
                
                print(f"[TRANSLATION] Successfully translated blight report to {lang_key}")
                
            except Exception as e:
                print(f"[TRANSLATION] Error translating to {lang_key}: {e}")
                translations[lang_key] = None
        
        return translations


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    # Step 1: Collect weather data
    print("="*70)
    print("BLIGHT PREDICTION - COMPLETE WORKFLOW")
    print("="*70)
    print("\nStep 1: Collecting weather data...")
    
    collector = ComprehensiveBlightDataCollector()
    weather_dataset = collector.collect_complete_dataset(
        location_name="Hyderabad",
        target_date="2025-11-10",
        country_code="IN"
    )
    
    # Print weather summary
    collector.print_summary(weather_dataset)
    
    # Step 2: Initialize blight prediction agent
    print("\nStep 2: Initializing Blight Prediction Agent...")
    agent = BlightPredictionAgent()
    
    # Step 3: Create state with weather data
    state = {
        "weather_dataset": weather_dataset,  # Full dataset from collector
        "days_after_planting": 30,  # Vegetative growth stage
    }
    
    # Step 4: Run prediction
    print("\nStep 3: Running blight risk prediction...")
    result_state = agent.predict_blight_risk(state)
    
    # Step 5: Print report
    print("\n" + "="*70)
    print("BLIGHT PREDICTION REPORT")
    print("="*70)
    print(result_state["final_report"])
    
    # Step 6: Access structured prediction data
    prediction = result_state.get("blight_prediction", {})
    print("\n" + "="*70)
    print("STRUCTURED PREDICTION DATA (JSON)")
    print("="*70)
    print(json.dumps(prediction, indent=2))
