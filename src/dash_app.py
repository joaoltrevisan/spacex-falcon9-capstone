"""Plotly Dash dashboard for the 90-row course sample. Requires Dash/Plotly."""
from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

ROOT = Path(__file__).resolve().parents[1]
DATA = pd.read_csv(ROOT / "data/processed/course_model_dataset.csv")
app = Dash(__name__)
sites = sorted(DATA.LaunchSite.unique())
orbits = sorted(DATA.Orbit.unique())
app.layout = html.Div([
    html.H1("SpaceX Falcon 9 - First-stage landing outcomes"),
    html.P("IBM Skills Network course sample: 90 launches through November 2020."),
    html.Label("Launch site"), dcc.Dropdown(["All"] + sites, "All", id="site"),
    html.Label("Orbit"), dcc.Dropdown(["All"] + orbits, "All", id="orbit"),
    dcc.Graph(id="outcomes"), dcc.Graph(id="payload"),
])

@app.callback(Output("outcomes", "figure"), Output("payload", "figure"),
              Input("site", "value"), Input("orbit", "value"))
def update(site, orbit):
    frame = DATA.copy()
    if site != "All": frame = frame[frame.LaunchSite == site]
    if orbit != "All": frame = frame[frame.Orbit == orbit]
    counts = frame.Class.map({0: "Failure", 1: "Success"}).value_counts().rename_axis("Outcome").reset_index(name="Launches")
    f1 = px.pie(counts, names="Outcome", values="Launches", title="Launch outcomes in filtered sample",
                color="Outcome", color_discrete_map={"Failure": "#F36B3F", "Success": "#1677A8"})
    f2 = px.scatter(frame, x="PayloadMass", y="Class", color="Class", hover_data=["FlightNumber", "LaunchSite", "Orbit"],
                    title="Payload mass versus landing outcome",
                    labels={"PayloadMass": "Payload mass (kg)", "Class": "Landing outcome (0 = failure, 1 = success)"},
                    color_discrete_map={0: "#F36B3F", 1: "#1677A8"})
    f2.update_yaxes(tickmode="array", tickvals=[0, 1], ticktext=["Failure", "Success"])
    return f1, f2

if __name__ == "__main__":
    app.run(debug=False)

