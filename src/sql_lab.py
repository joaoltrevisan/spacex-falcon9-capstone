"""Ten SQL tasks from the official IBM presentation template."""
from pathlib import Path
import sqlite3,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
QUERIES={
'01_unique_sites':'SELECT DISTINCT Launch_Site FROM launches ORDER BY Launch_Site',
'02_cca_records':"SELECT Date, Booster_Version, Launch_Site, PAYLOAD_MASS__KG_ FROM launches WHERE Launch_Site LIKE 'CCA%' ORDER BY Date LIMIT 5",
'03_nasa_payload':"SELECT Customer, SUM(PAYLOAD_MASS__KG_) AS payload_kg FROM launches WHERE Customer = 'NASA (CRS)' GROUP BY Customer",
'04_f9_v11_average':"SELECT COUNT(*) AS launches, ROUND(AVG(PAYLOAD_MASS__KG_), 2) AS mean_payload_kg FROM launches WHERE Booster_Version LIKE 'F9 v1.1%'",
'05_first_ground_landing':"SELECT MIN(Date) AS first_successful_ground_landing FROM launches WHERE Landing_Outcome = 'Success (ground pad)'",
'06_drone_4000_6000':"SELECT Date, Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE Landing_Outcome = 'Success (drone ship)' AND PAYLOAD_MASS__KG_ > 4000 AND PAYLOAD_MASS__KG_ < 6000 ORDER BY Date",
'07_mission_outcomes':'SELECT Mission_Outcome, COUNT(*) AS missions FROM launches GROUP BY Mission_Outcome ORDER BY missions DESC',
'08_max_payload_boosters':'SELECT Booster_Version, PAYLOAD_MASS__KG_ FROM launches WHERE PAYLOAD_MASS__KG_ = (SELECT MAX(PAYLOAD_MASS__KG_) FROM launches) ORDER BY Date',
'09_2015_drone_failures':"SELECT Date, substr(Date,6,2) AS month, Booster_Version, Launch_Site, Landing_Outcome FROM launches WHERE Date LIKE '2015-%' AND Landing_Outcome = 'Failure (drone ship)' ORDER BY Date",
'10_rank_outcomes':"SELECT Landing_Outcome, COUNT(*) AS launches, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rank FROM launches WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' GROUP BY Landing_Outcome ORDER BY launches DESC, Landing_Outcome"
}
def main():
 data=pd.read_csv(ROOT/'data/raw/Spacex_SQL.csv').dropna(subset=['Date'])
 for col in data.select_dtypes(include=['object','string']).columns:data[col]=data[col].str.strip()
 out=ROOT/'outputs/sql_lab';out.mkdir(parents=True,exist_ok=True)
 con=sqlite3.connect(':memory:');data.to_sql('launches',con,index=False)
 results={}
 for name,q in QUERIES.items():
  frame=pd.read_sql_query(q,con);frame.to_csv(out/f'{name}.csv',index=False);results[name]=frame.to_dict('records')
 results['nasa_all_mentions']=pd.read_sql_query("SELECT COUNT(*) AS launches, SUM(PAYLOAD_MASS__KG_) AS payload_kg FROM launches WHERE Customer LIKE '%NASA%'",con).to_dict('records')
 (out/'queries.sql').write_text('\n\n'.join(f'-- {n}\n{q};' for n,q in QUERIES.items()))
 (out/'results.json').write_text(json.dumps(results,indent=2))
 print(json.dumps(results,indent=2));return results
if __name__=='__main__':main()
