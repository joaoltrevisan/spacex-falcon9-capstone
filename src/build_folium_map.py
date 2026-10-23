"""Build an interactive Folium launch-site map from the reconstructed sample."""
from pathlib import Path
import pandas as pd
import folium
from math import radians, sin, cos, asin, sqrt

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data/processed/course_model_dataset.csv")
site = df.groupby("LaunchSite").agg(
    launches=("Class", "size"), successes=("Class", "sum"),
    success_rate=("Class", "mean"), Latitude=("Latitude", "first"), Longitude=("Longitude", "first")
).reset_index()

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two launch-site coordinates."""
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlat, dlon = lat2-lat1, lon2-lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

locations = site.set_index("LaunchSite")[["Latitude", "Longitude"]].to_dict("index")
proximity = {}
for name, coord in locations.items():
    others = [(other, haversine_km(coord["Latitude"], coord["Longitude"], target["Latitude"], target["Longitude"]))
              for other, target in locations.items() if other != name]
    proximity[name] = min(others, key=lambda item: item[1])
m = folium.Map(location=[30, -100], zoom_start=3, tiles="OpenStreetMap")
for row in site.to_dict(orient="records"):
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]], radius=8 + row["launches"] ** .5,
        popup=(f"{row['LaunchSite']}<br>Launches: {row['launches']}<br>"
               f"Successes: {row['successes']}<br>Success rate: {row['success_rate']:.1%}<br>"
               f"Nearest sampled site: {proximity[row['LaunchSite']][0]} "
               f"({proximity[row['LaunchSite']][1]:.1f} km)"),
        tooltip=row["LaunchSite"], color="#225ea8", fill=True,
        fill_color="#41b6c4", fill_opacity=.8,
    ).add_to(m)
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        tooltip=f"{row['LaunchSite']}: {row['launches']} launch records",
        icon=folium.Icon(color="blue", icon="rocket", prefix="fa"),
    ).add_to(m)
out = ROOT / "outputs/launch_sites_folium.html"
m.save(str(out))
print(out)

