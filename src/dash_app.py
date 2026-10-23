"""IBM Dash lab: success-count pie, site outcome ratio, payload range slider."""
from pathlib import Path
import pandas as pd,plotly.express as px
from dash import Dash,Input,Output,dcc,html
ROOT=Path(__file__).resolve().parents[1]
DATA=pd.read_csv(ROOT/'data/raw/spacex_launch_dash.csv')
app=Dash(__name__)
app.layout=html.Div([
 html.H1('SpaceX launch outcomes',style={'margin':'8px 0','color':'#08253e'}),
 html.P('IBM Dash laboratory sample: 56 launch records. Outcome 1 = success, 0 = failure.'),
 html.Label('Launch site'),dcc.Dropdown(['All']+sorted(DATA['Launch Site'].unique()),'All',id='site',clearable=False),
 html.Div([dcc.Graph(id='success-pie',style={'width':'44%'}),dcc.Graph(id='payload-scatter',style={'width':'56%'})],style={'display':'flex'}),
 html.Label('Payload range (kg)'),dcc.RangeSlider(0,10000,100,value=[0,10000],id='payload-range',marks={i:str(i) for i in range(0,10001,2000)},tooltip={'placement':'bottom','always_visible':True}),
 html.Div(id='sample-count',style={'paddingTop':'20px'})],style={'fontFamily':'Arial','maxWidth':'1360px','margin':'auto','padding':'15px'})
@app.callback(Output('success-pie','figure'),Output('payload-scatter','figure'),Output('sample-count','children'),Input('site','value'),Input('payload-range','value'))
def update(site,payload):
 frame=DATA if site=='All' else DATA[DATA['Launch Site']==site]
 if site=='All':
  counts=frame[frame['class']==1].groupby('Launch Site',as_index=False).size()
  pie=px.pie(counts,names='Launch Site',values='size',title='Successful launches by site (24 total)')
 else:
  counts=frame['class'].map({0:'Failure',1:'Success'}).value_counts().rename_axis('Outcome').reset_index(name='Launches')
  pie=px.pie(counts,names='Outcome',values='Launches',color='Outcome',color_discrete_map={'Failure':'#eb6b45','Success':'#1677a8'},title=f'{site}: success / failure ratio')
 selected=frame[frame['Payload Mass (kg)'].between(payload[0],payload[1])]
 scatter=px.scatter(selected,x='Payload Mass (kg)',y='class',color='Booster Version Category',hover_data=['Flight Number','Launch Site'],title='Payload versus launch outcome',labels={'class':'Landing outcome'})
 scatter.update_yaxes(tickvals=[0,1],ticktext=['Failure (0)','Success (1)'],range=[-.15,1.15])
 for fig in [pie,scatter]:fig.update_layout(height=430,margin=dict(t=60,l=45,r=20,b=45),font=dict(size=14),template='plotly_white')
 return pie,scatter,f'Scatter: {len(selected)} records in payload range {payload[0]:,}-{payload[1]:,} kg. Pie chart uses all payloads at the selected site.'
if __name__=='__main__':app.run(host='127.0.0.1',port=8050,debug=False)
