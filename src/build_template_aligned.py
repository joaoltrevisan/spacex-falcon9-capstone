"""Build a slide-by-slide PDF matching IBM's official 47-slide content structure."""
from pathlib import Path
import json,html
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from sql_lab import QUERIES
R=Path(__file__).resolve().parents[1];F=R/'outputs/figures';repo='https://github.com/joaoltrevisan/spacex-falcon9-capstone';N=[str(p.relative_to(R)) for p in sorted((R/'notebooks').glob('*.ipynb'))];sql=json.loads((R/'outputs/sql_lab/results.json').read_text());res=json.loads((R/'outputs/analysis_results.json').read_text())
OUT=R/'reports/Capstone_Entrega_Final.pdf';c=canvas.Canvas(str(OUT),pagesize=(1100,700));c.setTitle('SpaceX Falcon 9 - IBM Capstone Final Presentation');c.setAuthor('Joao Trevisan');num=0
base=ParagraphStyle('base',fontName='Helvetica',fontSize=17,leading=23,textColor=HexColor('#17364b'))
def p(s,x=38,y=605,w=1024,size=17,color=None):
 st=ParagraphStyle('pp',parent=base,fontSize=size,leading=size*1.35,textColor=color or base.textColor)
 ob=Paragraph(s,st);_,h=ob.wrap(w,1000);ob.drawOn(c,x,y-h)
 if y-h<25:raise ValueError(f'Overflow p{num}: {s[:70]}, bottom={y-h}')
 return y-h-12
def start(title,tag):
 global num;num+=1;c.setFillColor(HexColor('#f5f8fa'));c.rect(0,0,1100,700,fill=1,stroke=0);c.setFillColor(HexColor('#087e9c'));c.rect(0,688,1100,12,fill=1,stroke=0);p(tag.upper(),y=665,size=11,color=HexColor('#087e9c'));p(title,y=638,size=29);c.setFillColor(HexColor('#526879'));c.setFont('Helvetica',9);c.drawString(38,15,'Joao Trevisan | IBM Applied Data Science Capstone');c.drawRightString(1060,15,str(num))
def end():c.showPage()
def link(path,y=48):
 u=repo+('/blob/main/'+path if path else '');p(f'<link href="{u}" color="#00799c"><u>{u}</u></link>',y=y,size=11)
def bullets(xs,y=583,size=18):
 for x in xs:y=p('• '+x,y=y,size=size)
 return y
def pic(file,x=48,y=165,w=1000,h=395):c.drawImage(str(F/file),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def flow(nodes,caption):
 # Four clear stages, with connecting arrows, inside the slide body.
 n=len(nodes);x0=48;gap=20;bw=(1000-gap*(n-1))/n;yy=371;hh=115
 for i,node in enumerate(nodes):
  x=x0+i*(bw+gap);c.setFillColor(HexColor('#dceff4') if i%2==0 else HexColor('#e9f0f5'));c.roundRect(x,yy,bw,hh,12,fill=1,stroke=0);p(f'<b>{i+1}</b><br/>{node}',x=x+10,y=yy+hh-15,w=bw-20,size=15)
  if i<n-1:
   c.setStrokeColor(HexColor('#087e9c'));c.setLineWidth(2);sx=x+bw+3;ex=sx+gap-6;c.line(sx,yy+hh/2,ex,yy+hh/2);c.line(ex-7,yy+hh/2+5,ex,yy+hh/2);c.line(ex-7,yy+hh/2-5,ex,yy+hh/2)
 p(caption,y=325,size=17)
# 1 Title
start('SpaceX Falcon 9 landing prediction','Final presentation | Applied Data Science Capstone')
p('Joao Trevisan | 23 October 2026',y=550,size=20)
p('<b>Question:</b> Which Falcon 9 launch characteristics are associated with a successful first-stage landing, and how well can classifiers predict the outcome?',y=475,size=23)
p('<b>Public project repository: completed notebooks, Python scripts, data and results</b>',y=359,size=18);link('',y=325)
p('Decision Tree: best five-fold CV accuracy 87.7%; 83.3% holdout accuracy. Full evidence is presented in the following slides.',y=225,size=19);end()
# 2 exec summary
start('Executive Summary','Summary of methods and all principal results')
bullets(['API data collection; historical web scraping; feature wrangling; six EDA charts; ten SQL analyses; Folium mapping; interactive Plotly Dash; four tuned classifiers.',
'90-row modeling sample: 60/90 successful landings (66.7%). Success rates vary by site, orbit and year; categories and time periods are imbalanced.',
'10-query SQL task results are shown individually on slides 21-30. Folium and Dash evidence appears on slides 31-36.',
'Decision Tree led five-fold CV (0.877) and holdout accuracy (0.833). Confusion matrix: TN=4, FP=2, FN=1, TP=11; precision=.846, recall=.917, F1=.880.',
'Independent samples have different denominators: Dash 24/56=42.9%; modeling 60/90=66.7%. They must not be combined. A selected 2,000-6,000 kg Dash subset is 18/34=52.9%.'],size=16);end()
# 3 intro
start('Introduction: context and questions','Project background and context')
bullets(['Reusability of the Falcon 9 first stage is relevant to launch economics and recovery operations.',
'Target: booster landing success (Class 1) versus other recorded landing outcomes (Class 0). Mission payload delivery success is a different outcome.',
'Questions: how do landing outcomes vary with flight number, launch site, orbit and payload? What do the ten SQL tasks reveal? Which model performs best on a held-out sample?',
'Historical, observational analysis can identify associations; it cannot establish that a particular site, payload or orbit causes a successful landing.',
'The final repository and each completed notebook are linked on the relevant methodology slides.'],size=18);end()
# 4 methods overview
start('Workflow and datasets','Methodology | data sources kept distinct')
bullets(['Archived IBM SpaceX API response: 107 launch records, normalized to 18 fields. The notebook attempts the documented live REST GET and transparently falls back to the IBM archive if unreachable.',
'Wikipedia revision 987426997: 97 dated launch rows through 2020-11-05.',
'IBM modeling table plus supplied 90 x 80 feature matrix: validated and used for six EDA plots and predictive models.',
'SQL lab dataset: 101 records. Folium geography dataset and Dash dataset: 56 records each.',
'Every result below names its sample. No unsupported join combines these incompatible samples.'],size=17);end()
# 5 api flow
start('Data collection: SpaceX REST API','Flowchart | request, response, normalization')
flow(['GET /v4/launches/past<br/><font size="10">api.spacexdata.com</font>','Check HTTP status<br/>Parse JSON array','Flatten launch + first core<br/>Keep flight, rocket, payload, landing','Save normalized CSV<br/>107 rows x 18 fields'], 'Nested response fields include launch date, mission success, rocket and launchpad IDs, payload IDs, core reuse, landing attempt/type/result and failures. The notebook attempts the live request; when unreachable it uses the fixed IBM API response and reports that fallback.');link(N[0]);end()
# 6 API code evidence
start('SpaceX API: request and output evidence','GET endpoint | executed outcome cell')
p('GET https://api.spacexdata.com/v4/launches/past',y=572,size=18)
p('Python: requests.get(API_URL, timeout=5) -> inspect response.status_code -> raise_for_status() -> response.json() -> validate list -> normalize records -> export CSV.',y=518,size=19)
p('<b>Reproducible outcome:</b> IBM archive contains 107 records and the normalized output has 107 rows x 18 fields. The code records whether the current run used live JSON or the IBM fallback.',y=414,size=20)
p('The public SpaceX API endpoint is community-maintained. The saved course response makes the analysis reproducible when the live service is unreachable.',y=318,size=18);link(N[0],y=243);end()
# 7 scraping
start('Data collection: historical web scraping','Flowchart | table extraction and cleaning')
flow(['Load fixed Wikipedia HTML revision','Find flight/date tables<br/>Normalize headers','Parse UTC dates<br/>Filter course date window','Sort + deduplicate flights<br/>Export CSV'], 'Revision 987426997 | Date window: 2010-06-04 through 2020-11-05 | Output: 97 unique dated launch rows. The fixed source revision prevents the live page from changing this historical sample.');link(N[1]);end()
# 8 wrangle
start('Data wrangling: validate features and target','Flowchart | alignment, encoding, split')
flow(['IBM labeled rows +<br/>supplied 90x80 matrix','Match flight order;<br/>decode category columns','Check values and missingness;<br/>Class=landing outcome','Stratified 72/18 split;<br/>train-only CV tuning'], 'All 90 flights and 80 feature values validated against the IBM source; one-hot Orbit, LaunchSite, LandingPad and Serial categories align. Class 1=success (60); Class 0=other outcome (30).');link(N[2]);end()
# 9 visualization methodology
start('EDA with visualization: six required charts','Chart choice and purpose')
bullets(['Scatter plots: Flight Number vs Launch Site; Payload vs Launch Site; Flight Number vs Orbit; Payload vs Orbit. Color encodes Class 0/1.',
'Bar chart: success rate by orbit, with the count for each orbit to show small denominators.',
'Line chart: annual average landing success rate, annotated with yearly counts.',
'Use: examine launch sequence, site/orbit mix and payload patterns. These unadjusted comparisons are descriptive, not causal.',
'Six separate result slides with interpretation follow (slides 15-20).'],size=18);link(N[3]);end()
#10 SQL method
start('EDA with SQL: query method','Ten required SQL questions and repository notebook')
flow(['Load 101-row<br/>Spacex.csv','Trim string whitespace;<br/>SQLite table','SELECT, LIKE, aggregates,<br/>subquery, DENSE_RANK','Return each query +<br/>results + explanation'], 'Landing_Outcome (booster recovery) remains distinct from Mission_Outcome (payload delivery). Slide results 21-30 use this lab sample only.');link(N[4]);end()
#11 Folium method
start('Interactive mapping with Folium','Map objects and their purpose')
bullets(['Circle and marker for each launch site; tooltip/popup shows the site and launches.',
'MarkerCluster preserves 56 individual launch records at overlapping Florida coordinates; green=successful landing, red=unsuccessful landing.',
'Polyline between CCAFS LC-40 and selected coastline/road points displays approximate straight-line distances. Haversine computes distance.',
'MousePosition helps read coordinates on visible map tiles. Three result screenshots are provided on slides 31-33.']);link(N[4]);end()
#12 dash method
start('Dashboard with Plotly Dash','Plots, controls and purpose')
bullets(['Pie chart counts successful launches across all sites (24 successes); selecting a site changes the pie to its success/failure ratio.',
'Scatter plot shows Payload Mass vs binary landing outcome; marker color encodes booster version; hover shows flight and site.',
'Launch-site dropdown filters the selected site. Payload RangeSlider filters scatter records and updates visible sample size.',
'The pie denominator and scatter range are stated separately. Result screenshots on slides 34-36.']);link('src/dash_app.py');end()
#13 predictive method
start('Predictive analysis: classifier development','Flowchart | build, tune, select, evaluate')
flow(['Stratified split<br/>72 train / 18 test','Train-only 5-fold<br/>GridSearchCV','Compare Logistic Reg.,<br/>SVM, KNN, Tree','Select CV accuracy;<br/>evaluate once on test'], 'Scaling is inside the Logistic Regression/SVM/KNN pipelines. Tree grid tunes Gini/depth/leaf. Test metrics do not choose hyperparameters. Full parameter table and scores appear on slide 37.');link(N[6]);end()
#14 results overview
start('EDA and predictive results','Results section')
bullets(['Six visualization results from the validated 90-row labeled sample: site, orbit, payload, flight sequence and annual trends.',
'Ten separate SQL query outcomes on the 101-row laboratory dataset.',
'Interactive Folium maps show locations, landing results and approximate proximity.',
'Dash shows success counts/ratios and payload-range behavior from its own 56-record sample.',
'Four classifier metrics and the best model confusion matrix use the 18-record holdout.']);end()
#15-20 six EDA charts
charts=[('Flight Number vs Launch Site','flight_site.png','Later flights show more successes across sites. KSC has 17/22 (77.3%), VAFB 10/13 (76.9%), CCAFS SLC 40 33/55 (60.0%). Site results reflect unequal sample size and mission mix.'),('Payload vs Launch Site','payload_site.png','Both outcomes appear across payload values at each site. Payload distributions differ by site; mission mix limits a direct site comparison.'),('Success Rate vs Orbit Type','orbit_rates.png','SSO 5/5, VLEO 12/14, GTO 14/27. Several 100% orbits have one flight only. Small denominators make those rates unstable.'),('Flight Number vs Orbit Type','flight_orbit.png','Orbit types are unevenly distributed over mission sequence. Experience and hardware changes can confound the apparent relationship.'),('Payload vs Orbit Type','payload_orbit.png','Payload mass varies by orbit and mission requirements. The graph does not establish that higher payload causes successful landing.'),('Launch Success Yearly Trend','year_rates.png','Annual rates generally rise over time but are not monotonic: 2017=15/18, 2018=11/18, 2019=9/10, 2020=16/19. Early years are sparse.')]
for title,img,caption in charts:
 start(title,'EDA visualization result | 90-record IBM labeled sample');pic(img,x=65,y=190,w=970,h=385);p(caption,y=168,size=18);link(N[3]);end()
#21-30 SQL separate result slide per exact prompt
stitle=['All Launch Site Names','Launch Site Names Begin with CCA','Total Payload Mass from NASA CRS','Average Payload Mass by F9 v1.1','First Successful Ground Landing Date','Successful Drone Ship Landing: payload 4,000-6,000 kg','Total Successful and Failure Mission Outcomes','Boosters Carried Maximum Payload','2015 Failed Drone Ship Landing Records','Rank Landing Outcomes: 2010-06-04 to 2017-03-20']
explain=['Four distinct location labels are retained as recorded in the dataset.','The five earliest matching records are displayed in chronological order.','NASA (CRS) customers carry 45,596 kg total. A separate LIKE NASA query sums all NASA-named customers to 107,010 kg across 32 records.','F9 v1.1 carries an average 2,534.67 kg across 15 launches.','First ground-pad landing success: 2015-12-22.','Four successful drone-ship landings satisfy the strict payload bounds.','Mission outcomes concern payload delivery: 99 Success, 1 Success (payload status unclear), 1 Failure (in flight).','Maximum payload is 15,600 kg; 12 launches share the maximum.','Two failures occurred Jan 10 and Apr 14; both launched from CCAFS LC-40.','Dense ranking preserves ties. Date endpoints are inclusive.']
for i,key in enumerate(QUERIES):
 start(stitle[i],'EDA with SQL | Question '+str(i+1)+' of 10 | 101-row lab dataset')
 q=QUERIES[key];p('<b>Query</b><br/>'+html.escape(q),y=579,size=12)
 rows=sql[key]
 if i==7:rows=[{'Booster_Version':r['Booster_Version'],'PAYLOAD_MASS__KG_':15600} for r in rows]
 headers=list(rows[0]);data=[[str(h).replace('_',' ') for h in headers]]+[[str(r[h]) for h in headers] for r in rows]
 widths=[1024/len(headers)]*len(headers);tbl=Table(data,colWidths=widths,repeatRows=1)
 tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#087e9c')),('TEXTCOLOR',(0,0),(-1,0),white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),12),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#e7f0f4')]),('GRID',(0,0),(-1,-1),.35,HexColor('#c5d4dc')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 _,th=tbl.wrap(1024,300);tbl.drawOn(c,38,540-th)
 p('<b>Result and interpretation:</b> '+explain[i],y=510-th,size=16)
 if i==2:p('NASA CRS exact category is the course question. The all-NASA result is supplementary and does not replace it.',y=420-th,size=14)
 link(N[4],y=50);end()
#31-33 Folium evidence
for title,img,caption in [('All launch sites on a global map','map_sites.png','The four IBM dataset labels span Florida and California. Florida launch-pad markers overlap at national zoom; interactive zoom and marker popups distinguish them.'),('Color-coded launch outcomes on Folium','map_outcomes.png','At KSC, the expanded cluster displays 13 individual launch records: 10 successful outcomes (green) and 3 failures (red).'),('Selected launch-site proximity to coast and road','map_proximity.png','From CCAFS LC-40: 0.925 km to selected coastline point and 0.645 km to Samuel C. Phillips Parkway. Haversine straight-line distance; visually selected approximate points, not surveyed routes.')]:
 start(title,'Folium interactive map result');pic(img,x=60,y=170,w=980,h=400);p(caption,y=150,size=18);link(N[4]);end()
#34-36 Dash actual screenshots
for title,img,caption in [('Successful launch count by site','dash_all.png','All-site pie chart: 24 successful launches: KSC 10 (41.7%), CCAFS LC-40 7 (29.2%), VAFB 4 (16.7%), CCAFS SLC-40 3 (12.5%). Counts of success, not site-specific rates.'),('Pie chart for site with highest success ratio','dash_ksc.png','KSC is selected in dropdown: 10 successes / 13 = 76.9%, highest site ratio in the 56-row dashboard sample.'),('Payload vs launch outcome: two payload selections','dash_filtered.png','All-site RangeSlider 0-10,000 kg: 56 records / 24 successes (42.9%; page 34). Range 2,000-6,000 kg: 34 records / 18 successes (52.9%). Colors identify booster version; this is descriptive.')]:
 start(title,'Plotly Dash result screenshot');pic(img,x=55,y=182,w=990,h=385);p(caption,y=160,size=17);link(N[5]);end()
#37 classification results
start('Classification Accuracy','Holdout performance for all four models')
pic('accuracy_comparison.png',55,232,990,350)
p('Model table reports five-fold CV accuracy and held-out test accuracy. Highest test accuracy: Decision Tree 0.833 (15/18). Highest training-CV accuracy: Decision Tree 0.877.',y=211,size=18)
metrics=res['models']['metrics']
rows=[['Classifier','Accuracy','Precision','Recall','F1']]
for name,m in metrics.items():rows.append([name,*[f'{m[k]:.3f}' for k in ['accuracy','precision','recall','f1']]])
t=Table(rows,colWidths=[380,160,160,160,160]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#087e9c')),('TEXTCOLOR',(0,0),(-1,0),white),('GRID',(0,0),(-1,-1),.4,HexColor('#bccbd2')),('FONTSIZE',(0,0),(-1,-1),12),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#e7f0f4')])]))
_,h=t.wrap(1024,180);t.drawOn(c,38,184-h);link(N[6],y=46);end()
#38 confusion
start('Confusion Matrix: selected Decision Tree','Actual rows | predicted columns | positive class = successful landing')
pic('confusion_revised.png',285,291,530,270)
p('<b>[[TN=4, FP=2], [FN=1, TP=11]]</b>. Correctly predicted 4/6 unsuccessful landing outcomes and 11/12 successful outcomes.',y=240,size=20)
p('Precision=11/13=84.6%; recall=11/12=91.7%; F1=0.880; accuracy=15/18=83.3%. The small 18-launch holdout makes these estimates uncertain.',y=155,size=18);link(N[6]);end()
#39 conclusion
start('Conclusion: findings, implications and next steps','Conclusions')
bullets(['The Decision Tree outperforms the 66.7% majority baseline on this random holdout by three predictions, but two of six failures are missed.',
'Modeling sample: 60/90 successful landings (66.7%). Dashboard sample: 24/56 (42.9%). Different coverage changes the baseline; samples are not pooled.',
'Within the dashboard sample KSC has the highest site rate (10/13). This does not isolate site effect from flight time, payload and mission mix.',
'Filtering the dashboard to 2,000-6,000 kg yields 18/34 successes (52.9%) versus 24/56 (42.9%) overall. The association does not show a causal payload effect.',
'Limitations: small holdout, correlated flight/hardware/time, uneven categories and random split. Next: chronological evaluation, pre-launch features only, calibration and larger independent data.'],size=17);link(N[6]);end()
#40 creativity / appendix and repo links
start('Appendix: insight, sources and completed notebooks','Reproducibility and references')
p('<b>Original insights:</b> the success-rate baseline differs by 23.8 percentage points between the 90-row modeling sample and 56-row dashboard sample; the selected payload interval changes dashboard rate by 10.0 percentage points. Both illustrate how denominators and filters shape conclusions.',y=580,size=16)
p('<b>Repository</b>',y=458,size=17);link('',y=430)
y=375
for name in N:
 y=p(f'<link href="{repo}/blob/main/{name}" color="#00799c"><u>{name}</u></link>',y=y,size=12)
p('SpaceX API v4 docs: https://docs.spacexdata.com/ | Report builder and source code are in repository src/.',y=y-10,size=13);end()
c.save();print(OUT,'pages',num)
