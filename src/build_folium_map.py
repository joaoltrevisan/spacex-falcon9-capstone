"""Three IBM Folium tasks using the official 56-record geographic dataset."""
from pathlib import Path
from math import radians,sin,cos,asin,sqrt
import json,pandas as pd,folium
from folium.plugins import MarkerCluster,MousePosition
ROOT=Path(__file__).resolve().parents[1]
def distance_km(a,b):
 lat1,lon1,lat2,lon2=map(radians,[*a,*b])
 return 6371*2*asin(sqrt(sin((lat2-lat1)/2)**2+cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))
def main():
 df=pd.read_csv(ROOT/'data/raw/spacex_launch_geo.csv')
 sites=df.groupby('Launch Site').agg(Lat=('Lat','first'),Long=('Long','first'),launches=('class','size'),successes=('class','sum')).reset_index()
 m=folium.Map(location=[32,-99],zoom_start=4,tiles='OpenStreetMap')
 for _,r in sites.iterrows():
  loc=[r.Lat,r.Long]
  folium.Circle(loc,radius=1000,color='#137da0',fill=True).add_to(m)
  folium.Marker(loc,tooltip=r['Launch Site'],popup=f"{r['Launch Site']}<br>{r.successes}/{r.launches} successes ({r.successes/r.launches:.1%})").add_to(m)
 m.get_root().html.add_child(folium.Element('<div style="position:fixed;top:12px;right:12px;z-index:9999;background:white;padding:14px;font:16px Arial"><b>Four launch-site labels in the IBM dataset</b><br>Florida: CCAFS LC-40, CCAFS SLC-40, KSC LC-39A<br>California: VAFB SLC-4E<br>Nearby Florida markers overlap at this zoom; zoom to inspect.</div>'))
 m.save(ROOT/'outputs/launch_sites_folium.html')
 ksc=sites[sites['Launch Site']=='KSC LC-39A'].iloc[0]
 outcomes=folium.Map(location=[ksc.Lat,ksc.Long],zoom_start=16,tiles='OpenStreetMap')
 cluster=MarkerCluster(name='56 launch records',options={'spiderfyOnMaxZoom':True}).add_to(outcomes)
 for _,r in df.iterrows():
  color='green' if r['class'] else 'red'
  folium.Marker([r.Lat,r.Long],icon=folium.Icon(color=color,icon='info-sign'),popup=f"Flight {r['Flight Number']} | {r['Launch Site']} | {'Success' if r['class'] else 'Failure'}",tooltip=f"Flight {r['Flight Number']}: {'Success' if r['class'] else 'Failure'}").add_to(cluster)
 outcomes.get_root().html.add_child(folium.Element('<div style="position:fixed;top:12px;right:12px;z-index:9999;background:white;padding:12px;font:16px Arial"><b>Launch outcomes - 56 records</b><br><span style="color:green">Green: successful landing</span><br><span style="color:red">Red: unsuccessful landing</span><br>Click a cluster to inspect individual records</div>'))
 outcomes.save(ROOT/'outputs/launch_outcomes_folium.html')
 pad=sites[sites['Launch Site']=='CCAFS LC-40'].iloc[0]
 start=[float(pad.Lat),float(pad.Long)]
 # Points read through Folium MousePosition on visible OpenStreetMap tiles.
 coast=[28.56268,-80.56789];road=[28.56268,-80.57077]
 km=distance_km(start,coast);road_km=distance_km(start,road)
 proximity=folium.Map(location=[28.563,-80.573],zoom_start=16,tiles='OpenStreetMap')
 folium.Marker(start,tooltip='CCAFS LC-40',popup='Launch pad').add_to(proximity)
 for point,label,color in [(coast,'Coastline','#e35f35'),(road,'Samuel C. Phillips Parkway','#127c9a')]:
  distance=distance_km(start,point)
  folium.CircleMarker(point,radius=7,color=color,fill=True,fill_opacity=1,tooltip=f'{label}: {distance:.3f} km').add_to(proximity)
  folium.PolyLine([start,point],color=color,weight=4,tooltip=f'{label}: {distance:.3f} km').add_to(proximity)
 MousePosition(position='bottomleft').add_to(proximity)
 proximity.get_root().html.add_child(folium.Element(f'<div style="position:fixed;top:12px;right:12px;z-index:9999;background:white;padding:14px;font:16px Arial"><b>CCAFS LC-40 proximity</b><br>Coastline point: {km:.3f} km<br>Samuel C. Phillips Parkway: {road_km:.3f} km<br>Haversine straight-line distances<br>Points selected visually on OpenStreetMap<br>Approximate, not surveyed nearest distances</div>'))
 proximity.save(ROOT/'outputs/launch_proximity_folium.html')
 summary={'records':len(df),'sites':sites.to_dict('records'),'coastline_point':coast,'launch_pad':start,'distance_km':km,'road_point':road,'road_distance_km':road_km,'point_method':'Visual OpenStreetMap selection using Folium MousePosition, 2026-10-23'}
 (ROOT/'outputs/folium_results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));return summary
if __name__=='__main__':main()
