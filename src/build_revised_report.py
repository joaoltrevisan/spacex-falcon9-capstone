"""Generate a native-text PDF with executed results and actual browser screenshots."""
from pathlib import Path
import json,textwrap,html
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1];F=R/'outputs/figures';F.mkdir(exist_ok=True)
repo='https://github.com/joaoltrevisan/spacex-falcon9-capstone'
df=pd.read_csv(R/'data/processed/course_model_dataset.csv');res=json.loads((R/'outputs/analysis_results.json').read_text());sql=json.loads((R/'outputs/sql_lab/results.json').read_text())
from sql_lab import QUERIES
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
for x,y,name in [('FlightNumber','LaunchSite','flight_site'),('PayloadMass','LaunchSite','payload_site'),('FlightNumber','Orbit','flight_orbit'),('PayloadMass','Orbit','payload_orbit')]:
 fig,ax=plt.subplots(figsize=(10,4.3));
 for cl,color in [(0,'#e66c43'),(1,'#127c9a')]:
  sub=df[df.Class==cl];ax.scatter(sub[x],sub[y],c=color,label=f'Class {cl}',s=38,alpha=.8)
 ax.set(xlabel=x+(' (kg)' if x=='PayloadMass' else ''),ylabel=y);ax.legend();ax.grid(alpha=.18);fig.tight_layout();fig.savefig(F/f'{name}.png',dpi=150);plt.close(fig)
for group,name in [('Orbit','orbit_rates'),('year','year_rates')]:
 d=df.copy();d['year']=pd.to_datetime(d.Date).dt.year;g=d.groupby(group).Class.agg(['mean','size']);fig,ax=plt.subplots(figsize=(10,4.3))
 if group=='Orbit':ax.bar(g.index,g['mean'],color='#127c9a')
 else:ax.plot(g.index,g['mean'],marker='o',color='#127c9a')
 for i,(idx,row) in enumerate(g.iterrows()):ax.annotate(f'n={int(row["size"])}',(i if group=='Orbit' else idx,row['mean']),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
 ax.set(xlabel=group,ylabel='Landing success rate',ylim=(0,1.18));ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(F/f'{name}.png',dpi=150);plt.close(fig)
cv=res['models']['cross_validation'];names=list(cv);x=np.arange(4);fig,ax=plt.subplots(figsize=(10,4.3))
for off,key,label,color in [(-.18,'cv_accuracy','5-fold CV','#127c9a'),(.18,'test_accuracy','Holdout','#e66c43')]:
 bars=ax.bar(x+off,[cv[n][key] for n in names],.36,label=label,color=color);ax.bar_label(bars,fmt='%.3f',padding=3)
ax.set(xticks=x,xticklabels=names,ylim=(0,1.08),ylabel='Accuracy');ax.legend();fig.tight_layout();fig.savefig(F/'accuracy_comparison.png',dpi=150);plt.close(fig)
fig,ax=plt.subplots(figsize=(6,4.5));cm=np.array(res['models']['best_confusion_matrix']);ax.imshow(cm,cmap='Blues',vmin=0,vmax=12)
for i in range(2):
 for j in range(2):ax.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=30,color='white' if cm[i,j]>6 else '#08253e')
ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['Failure (0)','Success (1)'],yticklabels=['Failure (0)','Success (1)'],xlabel='Predicted',ylabel='Actual');fig.tight_layout();fig.savefig(F/'confusion_revised.png',dpi=150);plt.close(fig)
OUT=R/'reports/Capstone_Final_Revisado.pdf';c=canvas.Canvas(str(OUT),pagesize=(960,540));c.setTitle('SpaceX Falcon 9 - Applied Data Science Capstone');c.setAuthor('Joao Trevisan');page=0
style=ParagraphStyle('body',fontName='Helvetica',fontSize=17,leading=24,textColor=HexColor('#18374c'))
def para(text,x,y,w,size=17):
 st=ParagraphStyle('p',parent=style,fontSize=size,leading=size*1.35);p=Paragraph(text,st);a,h=p.wrap(w,500);p.drawOn(c,x,y-h);return y-h-14

def start(title,section='RESULTS'):
 global page;page+=1;c.setFillColor(HexColor('#f6f8fa'));c.rect(0,0,960,540,fill=1,stroke=0);c.setFillColor(HexColor('#127c9a'));c.rect(0,530,960,10,fill=1,stroke=0);c.setFont('Helvetica-Bold',10);c.drawString(40,502,section);para(title,40,482,880,28);c.setFillColor(HexColor('#526879'));c.setFont('Helvetica',9);c.drawString(40,19,'IBM Applied Data Science Capstone | SpaceX Falcon 9 | Joao Trevisan');c.drawRightString(920,19,str(page));
def end():c.showPage()
def link(label,path,y=63):
 url=repo+('/blob/main/'+path if path else '');para(f'<link href="{url}" color="#007da3"><u>{html.escape(label)}</u></link>',40,y,880,11)
def bullets(title,items,ref=None,section='METHODOLOGY'):
 start(title,section);y=411
 for t in items:y=para('• '+t,45,y,865,18)
 if ref:link('Executed notebook / source: '+ref,ref)
 end()
def visual(title,img,caption,ref=None):
 start(title);c.drawImage(str(F/img),40,123,width=880,height=300,preserveAspectRatio=True,anchor='c',mask='auto');para(caption,40,111,880,13)
 if ref:link('Source: '+ref,ref,y=48)
 end()
notebooks=sorted((R/'notebooks').glob('*.ipynb'));N=[str(p.relative_to(R)) for p in notebooks]
start('Predicting Falcon 9 first-stage landing success','FINAL PROJECT SUBMISSION');para('Applied Data Science Capstone',40,399,860,24);para('Joao Trevisan<br/>23 October 2026',40,348,850,18);para('<b>Submitted public GitHub repository URL</b>',40,264,850,18);para(f'<link href="{repo}" color="#007da3"><u>{repo}</u></link>',40,224,870,19);para('The repository contains executed notebooks, Python source, laboratory datasets, interactive maps and the final report. All links in this PDF are clickable.',40,160,860,17);end()
bullets('Executive summary',[
'Objective: estimate whether the first stage lands successfully, supporting an initial assessment of recovery potential.',
'The 90-row modeling sample contains 60 successful landings (66.7%). Site, orbit, payload and mission sequence show descriptive associations.',
'Decision Tree wins training cross-validation (87.7%) and achieves 83.3% on the 18-row holdout: 15 correct predictions.',
'The findings describe historical samples. They do not establish causal effects or estimate actual launch costs.'
],section='OVERVIEW')
bullets('Introduction and business question',[
'First-stage reuse is relevant to launch economics. The prediction target is successful landing, not payload delivery or total mission success.',
'Question: how do launch characteristics relate to landing outcomes, and which classifier performs best on the provided dataset?',
'Workflow: collect historical data → validate and encode → explore with charts and SQL → inspect maps/dashboard → tune classifiers → evaluate holdout.',
'A technical audience can reproduce the analysis through the linked notebooks and source files.'
],section='OVERVIEW')
bullets('Data sources and sample boundaries',[
'API collection: 107 archived launch records; web scraping: 97 historical launch rows from Wikipedia revision 987426997.',
'Modeling and six EDA charts: the supplied 90 × 80 encoded matrix, aligned against the IBM 90-row labeled table.',
'SQL: the separate 101-row Spacex.csv laboratory dataset. Folium and Dash: their separate 56-record laboratory datasets.',
'These samples are not joined or treated as interchangeable. Counts, categories and success rates are reported with their own denominator.'
])
bullets('API collection: archived response to normalized table',[
'Read IBM’s archived API_call_spacex_api.json → verify a JSON list → flatten launch and first-core fields → sort by flight number → export CSV.',
'Extract dates, rocket/launchpad IDs, payload IDs, core reuse fields and landing outcomes. Preserve nested payload/failure data as JSON.',
'Output: 107 rows × 18 columns. The notebook displays the resulting records and counts by rocket ID.',
'This is reproducible archived-response processing. The separate supplied modeling table provides enriched features; live API enrichment is not claimed.'
],N[0])
bullets('Web scraping: fixed historical Wikipedia revision',[
'Read saved HTML for revision 987426997 → identify flight/date tables → flatten headers and remove reference markers.',
'Parse UTC dates and numeric flight identifiers → retain 2010-06-04 through 2020-11-05 → sort and deduplicate by flight number.',
'Output: 97 historical launch rows. The executed notebook displays sample rows, date coverage and duplicate count.',
'The historical revision avoids silently mixing the present-day launch list with the course’s older sample.'
],N[1])
bullets('Wrangling and target definition',[
'Validate 90 feature rows against the labeled course table using flight order and decoded Orbit, LaunchSite, LandingPad and Serial categories.',
'Retain the course’s prepared numeric values; missing landing-pad values are represented as Unknown in the display table.',
'Class 1: successful landing. Class 0: the remaining landing outcomes, including no landing attempt or unavailable outcome.',
'Recreate one-hot encoding, cast to float64 and verify all 80 columns match the supplied matrix. Labels: 60 positive, 30 negative.'
],N[2])
bullets('EDA methods: six complementary views',[
'Scatter plots: flight number versus site; payload versus site; flight number versus orbit; payload versus orbit. Color indicates landing outcome.',
'Bar chart: mean success rate by orbit, annotated with the number of observations.',
'Line chart: annual mean success rate, with yearly sample sizes.',
'Purpose: identify descriptive patterns, differences in mission mix and sparse categories before interpreting model performance.'
],N[3])
bullets('SQL methods: ten laboratory questions',[
'Load Spacex.csv into SQLite; trim surrounding whitespace in text fields; retain 101 dated records.',
'Use DISTINCT, LIKE, aggregates, MIN/MAX, grouped counts, a maximum-payload subquery and DENSE_RANK.',
'Answer all ten template questions. NASA CRS is reported separately from all customer strings mentioning NASA.',
'Mission_Outcome and Landing_Outcome remain separate: payload mission success is not equivalent to successful booster recovery.'
],N[4])
bullets('Folium methods: locations, outcomes and proximity',[
'Markers and 1 km circles identify sites; a MarkerCluster preserves all 56 launch records and expands overlapping points.',
'Green markers represent success; red markers represent failure. Popups identify individual flights.',
'Two PolyLines connect CCAFS LC-40 to a visually selected coastline point and Samuel C. Phillips Parkway; Haversine measures straight-line distance.',
'MousePosition supplies the coordinates selected on OpenStreetMap. Distances are approximate straight-line measurements, not surveyed nearest distances.'
], 'src/build_folium_map.py')
bullets('Dash methods: interactive comparison',[
'All-site pie: successful launch counts by site, totaling 24. Selected-site pie: success/failure proportions within that site.',
'Scatter: payload versus binary landing outcome; color identifies booster version; hover exposes flight and site.',
'Dropdown filters launch site. RangeSlider filters scatter payload from 0 to 10,000 kg; the sample count updates with both filters.',
'The pie uses all payloads at the selected site. Its denominator is explicitly different from the filtered scatter denominator.'
], 'src/dash_app.py')
bullets('Classification: train, tune and evaluate',[
'Stratified split, seed 2: 72 training records and 18 holdout records. Five-fold stratified cross-validation operates on training data.',
'Compare Logistic Regression, SVM, KNN and Decision Tree with GridSearchCV. Scaling is inside the training pipelines.',
'Select by cross-validation accuracy, then report holdout accuracy, precision, recall, F1 and confusion matrix.',
'Limitations: only 18 holdout rows; correlated flight/date/booster features; random split does not demonstrate forecasting performance on future launches.'
],N[6])
visual('Flight number versus launch site','flight_site.png','Later missions show more successes. Site comparisons also reflect different mission periods and objectives.',N[3])
visual('Payload versus launch site','payload_site.png','Both outcomes occur across payload levels. CCAFS SLC 40 has 55 records, KSC 22 and VAFB 13; the sites have different mission mixes.',N[3])
visual('Landing success by orbit','orbit_rates.png','SSO is 5/5; VLEO 12/14; GTO 14/27. A 100% rate based on a single flight is weak evidence of general reliability.',N[3])
visual('Flight number versus orbit','flight_orbit.png','Orbit categories are unevenly distributed over mission sequence. Apparent orbit effects can be confounded with experience and hardware changes.',N[3])
visual('Payload versus orbit','payload_orbit.png','Payload and orbit are associated with mission requirements. The plot does not establish that increasing payload improves landing success.',N[3])
visual('Annual landing success','year_rates.png','Success rises from 0/1 in 2010 to 16/19 in 2020, with a decline to 11/18 in 2018. Early years have very small samples.',N[3])
titles=['Unique launch sites','First five CCA launch-site records','Total payload: NASA CRS','Average payload: F9 v1.1','First successful ground-pad landing','Droneship success: 4,000 < payload < 6,000 kg','Mission outcome counts','Boosters carrying the maximum payload','2015 droneship landing failures','Rank landing outcomes within the date window']
notes=['Four source site labels; LC-40 and SLC-40 are preserved as recorded.','The first five chronological CCA records are from 2010 to 2013.','NASA (CRS): 45,596 kg. All strings mentioning NASA: 107,010 kg across 32 records. The filters answer different questions.','Mean = 2,534.67 kg across 15 F9 v1.1 records.','The first ground-pad success in this dataset is 22 December 2015.','Four missions meet both the successful droneship outcome and strict payload bounds.','99 Success + 1 Success (payload status unclear) + 1 Failure (in flight). These are mission outcomes, not landing labels.','The maximum is 15,600 kg, shared by 12 listed booster records.','Two failures: January and April 2015, both at CCAFS LC-40.','Inclusive dates: 2010-06-04 through 2017-03-20. Ties share a dense rank.']
for idx,(key,q) in enumerate(QUERIES.items()):
 start(f'SQL {idx+1:02d} | {titles[idx]}');rows=sql[key];headers=list(rows[0]);data=[[Paragraph(html.escape(str(h).replace('_',' ')),ParagraphStyle('h',fontSize=10,leading=12,textColor=HexColor('#ffffff'))) for h in headers]]
 for row in rows:data.append([Paragraph(html.escape(str(row[h])),ParagraphStyle('cell',fontSize=10,leading=12)) for h in headers])
 table=Table(data,colWidths=[880/len(headers)]*len(headers));table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#127c9a')),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#eaf1f5')]),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));w,h=table.wrap(880,400);table.drawOn(c,40,415-h)
 y=415-h-14;y=para(notes[idx],40,y,880,13)
 para('<b>Executed SQL</b><br/>'+html.escape(q),40,min(y,185),880,10)
 link('Executed SQL notebook',N[4],48);end()
visual('Folium | all launch-site locations','map_sites.png','Four source labels span Florida and California. Three Florida markers overlap at national zoom; interactive zoom and popups distinguish them.','src/build_folium_map.py')
visual('Folium | color-coded launch outcomes','map_outcomes.png','Expanded KSC cluster: 13 records, including 10 successes (green) and 3 failures (red). Spiderfied markers separate overlapping coordinates.','src/build_folium_map.py')
visual('Folium | proximity to coastline and roadway','map_proximity.png','CCAFS LC-40 to the selected coastline point: 0.925 km; to Samuel C. Phillips Parkway: 0.645 km. Coordinates were read visually with MousePosition; distances are approximate.','src/build_folium_map.py')
visual('Dash | successful launches across all sites','dash_all.png','KSC contributes 10/24 successes (41.7% of successful launches); CCAFS LC-40 7, VAFB 4, CCAFS SLC-40 3. This pie shows counts, not per-site success rates.',N[5])
visual('Dash | highest site success ratio','dash_ksc.png','KSC: 10/13 = 76.9%, the highest ratio in this 56-record sample. Other rates: CCAFS LC-40 26.9%, SLC-40 42.9%, VAFB 40.0%.',N[5])
visual('Dash | payload filter changes the sample','dash_filtered.png','Changing All sites from 0-10,000 kg (56 rows) to 2,000-6,000 kg retains 34 rows. Both outcomes occur within the filtered interval.',N[5])
d=pd.read_csv(R/'data/raw/spacex_launch_dash.csv');g=d.groupby('Booster Version Category')['class'].agg(['sum','count','mean']);s=d[d['Payload Mass (kg)'].between(2000,6000)]
bullets('Dashboard findings: report denominators',[
'Filtered 2,000-6,000 kg sample: '+str(int(s['class'].sum()))+' successes / '+str(len(s))+' launches ('+f"{s['class'].mean():.1%}"+').',
'Booster categories: '+ '; '.join(f'{i}: {int(r["sum"])}/{int(r["count"])} ({r["mean"]:.1%})' for i,r in g.iterrows())+'.',
'The best observed category rate can be based on few launches; hardware version is also associated with mission period.',
'Counts and ratios answer different questions: KSC has the largest success count and highest site ratio here, but that does not isolate a causal site advantage.'
],N[5],section='RESULTS')
visual('Model comparison: cross-validation and holdout','accuracy_comparison.png','Decision Tree is selected by CV (0.877); holdout accuracy is 0.833. KNN predicts all holdout rows as success and matches the majority-class baseline.',N[6])
visual('Decision Tree confusion matrix','confusion_revised.png','Holdout: TN=4, FP=2, FN=1, TP=11. Recall=11/12=91.7%; precision=11/13=84.6%; F1=0.880. Three errors among 18 predictions.',N[6])
bullets('Selected hyperparameters and validation limits',[
'Logistic Regression: C=1. SVM: linear kernel, C=0.1. KNN: 3 neighbors, uniform weights.',
'Decision Tree: gini, maximum depth 5, minimum samples per leaf 1. Selected by training cross-validation.',
'One changed prediction shifts holdout accuracy by 5.6 percentage points. The observed model ranking needs validation on a larger independent sample.',
'Next experiment: chronological evaluation, remove features unavailable before launch, and assess calibration before using probabilities for operational decisions.'
],N[6],section='RESULTS')
bullets('Conclusions',[
'The historical 90-row sample has a 66.7% landing-success baseline. Later missions generally show higher success, with substantial variation by mission mix.',
'The 56-row dashboard sample yields a different baseline: 24/56 = 42.9%. Mixing these denominators would create misleading conclusions.',
'Decision Tree achieves 15/18 correct holdout predictions, exceeding the 12/18 majority baseline by three predictions.',
'Geographic proximity and descriptive associations support exploration; they do not prove why a landing succeeds. More data and temporal validation are required.'
],section='CONCLUSIONS')
start('Reproducibility and source references','APPENDIX');y=414
for name in N:y=para(f'<link href="{repo}/blob/main/{name}" color="#007da3"><u>{name}</u></link>',40,y,880,13)
y=para('Run: pip install -r requirements.txt; python src/sql_lab.py; python src/build_folium_map.py; python src/analyze_model.py; python src/dash_app.py',40,y,880,12)
base='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/'
for label,url in [('Official IBM presentation template',base+'labs/module_5/ds-capstone-template-coursera.pptx'),('Official submission overview',base+'labs/module_5/Submission_Overview_and_Instructions.pdf')]:y=para(f'<link href="{url}" color="#007da3"><u>{label}</u></link>',40,y,880,12)
end();c.save();print(OUT,'pages:',page)
