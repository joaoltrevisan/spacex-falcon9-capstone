"""Compact technical presentation; evidence and literal source URLs are visible."""
from pathlib import Path
import json,html
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from sql_lab import QUERIES
R=Path(__file__).resolve().parents[1];F=R/'outputs/figures';repo='https://github.com/joaoltrevisan/spacex-falcon9-capstone';N=[str(p.relative_to(R)) for p in sorted((R/'notebooks').glob('*.ipynb'))];results=json.loads((R/'outputs/sql_lab/results.json').read_text())
OUT=R/'reports/Capstone_Entrega_Final.pdf';c=canvas.Canvas(str(OUT),pagesize=(1100,700));c.setTitle('SpaceX Falcon 9 - Final Capstone Presentation');c.setAuthor('Joao Trevisan');num=0
base=ParagraphStyle('base',fontName='Helvetica',fontSize=16,leading=21,textColor=HexColor('#18374c'))
def p(s,x,y,w,size=16):
 obj=Paragraph(s,ParagraphStyle('p',parent=base,fontSize=size,leading=size*1.32));_,h=obj.wrap(w,900);obj.drawOn(c,x,y-h);assert y-h>=25,(num,s[:50],y-h);return y-h-12
def start(title,tag):
 global num;num+=1;c.setFillColor(HexColor('#f7f9fb'));c.rect(0,0,1100,700,fill=1,stroke=0);c.setFillColor(HexColor('#087e9c'));c.rect(0,688,1100,12,fill=1,stroke=0);p(tag.upper(),35,666,1020,11);p(title,35,638,1030,28);c.setFont('Helvetica',9);c.setFillColor(HexColor('#526879'));c.drawString(35,15,'Joao Trevisan | IBM Applied Data Science Capstone | 23 October 2026');c.drawRightString(1065,15,str(num))
def end():c.showPage()
def url(path,y=55):
 u=repo+('/blob/main/'+path if path else '');p(f'<link href="{u}" color="#00799c"><u>{u}</u></link>',35,y,1030,11)
def pic(name,x,y,w,h):c.drawImage(str(F/name),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
def items(vals,x=35,y=575,w=1030,size=17):
 for v in vals:y=p('• '+v,x,y,w,size)
 return y
start('SpaceX Falcon 9: can the first stage land successfully?','Final presentation · Executive Summary · Introduction')
p('<b>Business question.</b> First-stage reuse influences launch economics. This project predicts landing success from historical mission characteristics; payload delivery success is a different target.',35,575,1030,18)
p('<b>Executive summary.</b> The 90-record modeling sample contains 60 successful landings (66.7%). Decision Tree wins training cross-validation (87.7%) and correctly predicts 15/18 holdout records (83.3%). Later flights generally show higher recovery success, but orbit, site and hardware are confounded.',35,480,1030,18)
p('<b>Public project repository: executed notebooks, Python files, datasets and results</b>',35,366,1030,17);url('',330)
p('<b>Evidence guide.</b> Model results and confusion matrix: p. 2. Folium maps: pp. 3-4. Dash screenshots and payload interaction: pp. 5-6. Conclusions and original insights: p. 7. Methods and direct notebook URLs: pp. 8-10. Six EDA charts: pp. 11-13. Ten SQL queries and results: pp. 14-18.',35,279,1030,17)
p('<b>Scope.</b> Archived API: 107 records; historical scrape: 97 rows; model/EDA: 90 rows; SQL: 101 rows; Folium and Dash: 56 records each. These are separate laboratory samples, not one combined dataset.',35,153,1030,15);end()
start('Best classifier: Decision Tree; 15 of 18 holdout predictions correct','Predictive Analysis · Evaluation Results')
pic('accuracy_comparison.png',25,319,640,255);pic('confusion_revised.png',685,315,380,265)
p('<b>Selection:</b> highest five-fold training CV accuracy, 0.877. Best tree parameters: gini, max_depth=5, min_samples_leaf=1. Holdout was excluded from tuning.',35,302,1030,17)
p('<b>Confusion matrix:</b> actual rows and predicted columns, ordered [failure, success]: <b>[[4, 2], [1, 11]]</b>. True negatives=4; false positives=2; false negatives=1; true positives=11.',35,229,1030,17)
p('<b>Holdout metrics:</b> accuracy 83.3%; precision 84.6%; recall 91.7%; F1 0.880. The majority baseline is 66.7%. One changed prediction shifts accuracy by 5.6 percentage points; temporal validation remains necessary.',35,156,1030,16);url(N[6]);end()
start('Folium: all sites and color-coded landing outcomes','Interactive Visual Analytics · Map Evidence')
pic('map_sites.png',30,292,505,280);pic('map_outcomes.png',555,292,515,280)
p('<b>Left:</b> national map of the four site labels in the 56-record geographic dataset: CCAFS LC-40, CCAFS SLC-40, KSC LC-39A and VAFB SLC-4E. Nearby Florida markers overlap at national zoom; the interactive map supports zoom and popups.',35,277,1030,17)
p('<b>Right:</b> expanded KSC launch cluster separates 13 overlapping records: 10 successes in green and 3 failures in red. The cluster preserves individual launch outcomes instead of showing only a site average.',35,170,1030,17);url(N[4]);end()
start('Folium: measured proximity to coastline and roadway','Interactive Map · Distance Analysis')
pic('map_proximity.png',35,220,1030,365)
p('<b>CCAFS LC-40:</b> 0.925 km to coastline point (28.56268, -80.56789); 0.645 km to Samuel C. Phillips Parkway point (28.56268, -80.57077). Haversine distance uses the course launch-pad coordinates (28.56230197, -80.57735648).',35,203,1030,16)
p('Points were selected visually on OpenStreetMap using MousePosition. The colored lines show approximate straight-line proximity, not routes or surveyed nearest distances. Coastal location is observable; its causal effect on landing success is not established.',35,123,1030,15);url('src/build_folium_map.py',47);end()
start('Dash: successful-launch counts and highest site success ratio','Dashboard · Actual Application Screenshot')
pic('dash_all.png',35,235,1030,355)
p('<b>All-site pie:</b> 24 successes in total: KSC 10 (41.7% of successes), CCAFS LC-40 7, VAFB 4, CCAFS SLC-40 3. These slices show success counts, not within-site success rates.',35,218,1030,17)
p('<b>Within-site comparison:</b> KSC 10/13=76.9%, CCAFS LC-40 7/26=26.9%, CCAFS SLC-40 3/7=42.9%, VAFB 4/10=40.0%. KSC has the highest rate in this sample. The selected-site view and slider comparison follow.',35,132,1030,16);url(N[5],48);end()
start('Dash: site selection and payload RangeSlider in action','Dashboard · Interactive Results')
pic('dash_ksc.png',30,300,510,285);pic('dash_filtered.png',555,300,515,285)
p('<b>Left:</b> dropdown set to KSC LC-39A; its pie displays 76.9% success (10/13). The scatter contains the 13 KSC records.',35,285,1030,17)
p('<b>Right:</b> All sites with payload range 2,000-6,000 kg: 34 records, 18 successes (52.9%). Full range 0-10,000 kg on p. 5 contains 56 records and 24 successes (42.9%). The slider changes the scatter sample; the pie keeps all payloads at the selected site.',35,216,1030,16)
p('Color identifies booster version. Overall FT succeeds in 16/24 launches, B4 in 6/11, B5 in 1/1, v1.0 in 0/5 and v1.1 in 1/15. B5’s 100% is based on only one observation; it is not reliable evidence of superiority.',35,121,1030,15);url('src/dash_app.py',47);end()
start('Conclusions and additional insights','Conclusion · Interpretation · Original Analysis')
items([
'<b>Prediction:</b> Decision Tree improves on the holdout majority baseline by three correct predictions (15/18 versus 12/18). It identifies 11/12 successes and 4/6 failures; two failures are incorrectly predicted as successes.',
'<b>Original insight - denominator sensitivity:</b> 90-row modeling baseline = 66.7%; 56-row dashboard baseline = 42.9%. The 23.8 percentage-point difference reflects sample coverage, not a measured operational improvement.',
'<b>Original insight - selection changes the apparent rate:</b> filtering the dashboard to 2,000-6,000 kg changes observed success from 42.9% (24/56) to 52.9% (18/34). That association cannot establish a causal payload effect.',
'<b>EDA conclusion:</b> later missions show more successes; SSO is 5/5 and GTO 14/27 in the modeling sample. Sparse orbits and correlated mission characteristics limit interpretation.',
'<b>Next steps:</b> evaluate chronologically, remove post-launch information, test probability calibration and collect more independent observations before operational use.'
],size=17);url(N[6]);end()
start('Collection and wrangling: reproducible sources and outcomes','Methodology · API · Web Scraping · Target')
y=items([
'<b>API:</b> archived IBM JSON → validate list → flatten launch/first-core fields → sort by flight number → export 107 × 18 normalized table. This is archived-response processing; live API enrichment is not claimed.',
'<b>Scraping:</b> fixed Wikipedia revision 987426997 → identify launch tables → clean headers/reference markers → parse UTC dates → filter 2010-06-04 to 2020-11-05 → deduplicate. Result: 97 rows.',
'<b>Wrangling:</b> align the supplied 90 × 80 matrix with IBM labels by flight number and four one-hot category groups. Recreate encoding and confirm every feature value. Display missing landing-pad values as Unknown; retain the course’s prepared numeric values.',
'<b>Target:</b> Class 1 = successful landing (60 rows). Class 0 = other landing outcomes, including unsuccessful/unavailable outcomes (30 rows). Mission delivery success is separate.'
],size=15)
for path in N[:3]:url(path,y);y-=32
end()
start('EDA, SQL and interactive visualization methods','Methodology · Laboratory-specific URLs')
y=items([
'<b>Charts:</b> four scatter plots compare flight/payload with site/orbit; color encodes Class. Orbit bars and annual lines show success rate with sample sizes. Purpose: inspect mission mix, chronology and sparse categories.',
'<b>SQL:</b> trim text whitespace in the separate 101-row source; load SQLite; use DISTINCT, LIKE, grouped aggregates, MIN/MAX, a maximum-payload subquery and DENSE_RANK to answer ten lab questions.',
'<b>Folium:</b> site circles and markers identify geography; MarkerCluster reveals overlapping outcomes; green/red icons encode success/failure; PolyLine and Haversine show coast/road proximity; MousePosition provides point coordinates.',
'<b>Dash:</b> dropdown selects site; pie switches between success counts and within-site outcome ratio; scatter shows payload/outcome with booster color; RangeSlider filters payload and updates the sample count.'
],size=15)
for path in [N[3],N[4],N[5],'src/dash_app.py']:url(path,y);y-=31
end()
start('Classification methodology and tuned parameters','Predictive Analysis · Reproducible Evaluation')
items([
'<b>Split:</b> 90 observations; stratified training/holdout split of 72/18 with random_state=2. The holdout has 12 successes and 6 failures.',
'<b>Tuning:</b> GridSearchCV with five-fold stratified training CV. Scaling is inside the Logistic Regression, SVM and KNN pipelines, avoiding scaling leakage across CV folds.',
'<b>Models:</b> Logistic Regression (best C=1); SVM (linear, C=0.1); KNN (3 neighbors, uniform); Decision Tree (gini, depth 5, minimum leaf 1).',
'<b>CV accuracy / holdout accuracy:</b> Logistic Regression 0.837/0.778; SVM 0.823/0.778; KNN 0.694/0.667; Decision Tree 0.877/0.833.',
'<b>Interpretation:</b> select the tree by training CV, then inspect holdout confusion matrix and precision/recall (p. 2). KNN predicts every holdout row as success, matching the majority baseline. Random holdout performance is not evidence of future-launch forecasting accuracy.'
],size=17);url(N[6]);end()
for title,img1,img2,cap1,cap2 in [
('EDA: launch site, flight sequence and payload','flight_site.png','payload_site.png','Later flights show more successes across sites; flight sequence can proxy changes in experience and hardware.','Site rates: KSC 17/22=77.3%, VAFB 10/13=76.9%, CCAFS 33/55=60.0%. Unequal sample sizes and mission mix matter.'),
('EDA: orbit success and mission sequence','orbit_rates.png','flight_orbit.png','SSO 5/5; VLEO 12/14; GTO 14/27. ES-L1, GEO and HEO each have only one record; their 100% rates are fragile.','Orbit use changes over flight sequence. Descriptive differences cannot isolate the effect of orbit from chronology or hardware.'),
('EDA: payload by orbit and annual success','payload_orbit.png','year_rates.png','Orbit and payload reflect mission requirements. Both outcomes occur across payloads; heavier payload is not proven to cause better recovery.','2017: 15/18; 2018: 11/18; 2019: 9/10; 2020: 16/19. The overall increase is not monotonic; early samples are small.')]:
 start(title,'EDA with Visualization · 90-record modeling sample');pic(img1,30,290,510,290);pic(img2,555,290,515,290);p('<b>Left:</b> '+cap1,35,270,1030,18);p('<b>Right:</b> '+cap2,35,170,1030,18);url(N[3]);end()
titles=['Unique launch sites','First five chronological CCA records','Total NASA CRS payload','Average F9 v1.1 payload','First ground-pad success','Successful droneship, 4000 < payload < 6000 kg','Mission outcomes','Boosters with maximum payload','2015 failed droneship landings','Landing outcome ranking: 2010-06-04 to 2017-03-20']
notes=['Four distinct labels retained from the source.','First five CCA records span 2010-2013.','NASA (CRS) = 45,596 kg. All NASA mentions = 107,010 kg / 32 records.','F9 v1.1: 15 launches; mean payload 2,534.67 kg.','Earliest successful ground-pad landing: 2015-12-22.','Four records meet the successful landing and strict payload conditions.','99 Success; 1 Success (payload status unclear); 1 Failure (in flight). These are not landing outcomes.','Maximum 15,600 kg; 12 booster records share that maximum.','Two failures: January 10 and April 14, both CCAFS LC-40.','Inclusive date range; tied outcome counts share a dense rank.']
keys=list(QUERIES)
for offset in range(0,10,2):
 start(f'SQL evidence | tasks {offset+1} and {offset+2}','EDA with SQL · 101-record laboratory sample');y=578
 for i in [offset,offset+1]:
  key=keys[i];q=QUERIES[key];y=p(f'<b>{i+1}. {titles[i]}</b>',35,y,1030,17);y=p(html.escape(q),35,y,1030,11)
  rows=results[key]
  # Native text includes every result; compact two-column layout for maximum boosters.
  if i==7:
   txt='; '.join(str(r['Booster_Version']) for r in rows)+'; each = 15,600 kg.'
  else:txt='<br/>'.join(' | '.join(f'{html.escape(str(k))}: {html.escape(str(v))}' for k,v in row.items()) for row in rows)
  y=p(txt,35,y,1030,11);y=p(notes[i],35,y,1030,13);y-=8
 url(N[4],46);end()
c.save();print(OUT,'pages',num)
