"""Create notebook wrappers, an interactive map preview, and model CM art."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NBDIR = ROOT / "notebooks"
RES = json.loads((ROOT / "outputs/analysis_results.json").read_text())

def md(source):
    return {"cell_type":"markdown","metadata":{},"source":source.splitlines(True)}

def code(source, count=None, output=None):
    outputs=[]
    if output is not None:
        outputs=[{"output_type":"stream","name":"stdout","text":output.splitlines(True)}]
    return {"cell_type":"code","execution_count":count,"metadata":{},"outputs":outputs,"source":source.splitlines(True)}

def notebook(cells, title):
    return {"cells":[md(f"# {title}\n\nKernel: Python 3.10+. Install `../requirements.txt` from the project root before running cells that need optional libraries.\n"),*cells],
            "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},
            "nbformat":4,"nbformat_minor":5}

def save(name, cells, title):
    (NBDIR/name).write_text(json.dumps(notebook(cells,title),ensure_ascii=False,indent=1),encoding="utf-8")

def main():
    NBDIR.mkdir(exist_ok=True)
    save("01_Data_Collection_API.ipynb",[
        md("## Collection method\nThe archived IBM Skills Network API response was downloaded and saved unchanged as `../data/raw/API_call_spacex_api.json`. Nested launch, payload, core and landing fields were normalized into `../data/processed/api_launches_normalized.csv`. This archive contains more records than the 90-row labeled modeling sample; the two sources are preserved separately."),
        code("from pathlib import Path\nimport runpy\nimport pandas as pd\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nresult = runpy.run_path(str(root / 'src/collect_api.py'), run_name='capstone_api_collection')\nresult['main']()\nframe = pd.read_csv(root / 'data/processed/api_launches_normalized.csv')\nframe.head()"),
        md("Execution result: 107 API records normalized to 107 rows and 18 fields. The raw JSON and normalized CSV are included in the project. Source URL and retrieval date are listed in `../SOURCES.md`.")
    ],"1. Data Collection with the SpaceX API")
    save("02_Data_Collection_Web_Scraping.ipynb",[
        md("## Scraping method\nTo keep the scrape aligned with the course period, the source is a dated Wikipedia revision from 2020-11-06, retrieved from its page history and saved locally. Tables with flight number and UTC launch date were parsed with `pandas.read_html`; reference marks and non-launch rows were removed, and dates were restricted through 2020-11-05."),
        code("from pathlib import Path\nimport runpy\nimport pandas as pd\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nresult = runpy.run_path(str(root / 'src/scrape_wikipedia.py'), run_name='capstone_wikipedia_scrape')\nresult['main']()\nlaunches = pd.read_csv(root / 'data/raw/wikipedia_launch_history.csv')\nlaunches.head()"),
        md("Execution result: 97 unique launch-number rows were extracted from the archived Wikipedia tables. This historical scrape has a different inclusion/numbering scope from IBM's 90-row modeling table, so the datasets are not joined. The exact revision and local source snapshot are cited in `../SOURCES.md`.")
    ],"2. Web Scraping of Launch Records")
    counts=RES["class_counts"]
    save("03_Data_Wrangling_and_Target.ipynb",[
        md("## Inputs and validation\nThe supplied `dataset_part_3.csv` is already numeric and one-hot encoded (90 rows, 80 features). IBM's labeled `dataset_part_2.csv` was downloaded from the official course source. The script verifies row order and decoded categories before taking `Class` from that labeled table; no target labels are reconstructed from a third-party rendering."),
        code("from pathlib import Path\nimport runpy\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nrunpy.run_path(str(root / 'src/analyze_model.py'), run_name='__main__')"),
        md(f"## Result from executed preparation script\n- Rows: {RES['rows']}\n- Encoded features: {RES['feature_columns']}\n- Class counts: {counts}\n- Output files: `data/processed/landing_success_labels.csv` and `course_model_dataset.csv`. The analysis script was executed from the project runtime; this notebook wrapper cell itself has not been run."),
        md("The processed course table is a validated join of the supplied feature matrix with IBM's labeled 90-row source table. The separate archived API extract and Wikipedia scrape are retained under `data/raw/` and are not substituted into this fixed course model sample.")
    ],"3. Data Wrangling and Target Preparation")
    # A separate SQL notebook with actual rows returned by SQLite.
    site=RES['sql']['site_success']; orbit=RES['sql']['orbit_success']; payload=RES['sql']['payload_by_success']
    sql_source=(ROOT/'outputs/sql/capstone_queries.sql').read_text()
    save("05_SQL_EDA_and_Folium_Map.ipynb",[
        md("## SQL exploratory analysis\nThe following queries were run against an in-memory SQLite table built from the validated IBM 90-row labeled course table."),
        code("from pathlib import Path\nimport runpy\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nrunpy.run_path(str(root / 'src/analyze_model.py'), run_name='__main__')"),
        md("The SQL query text and returned CSV tables are included under `../outputs/sql/`. The same analysis script regenerates the validated data table and model metrics."),
        md("### Query text\n```sql\n"+sql_source+"```\n"),
        md("### Site success rate (actual query output)\n"+"\n".join(f"- {r['LaunchSite']}: {r['launches']} launches, {r['success_rate']:.3f} success rate" for r in site)),
        md("### Folium map\nThe Folium map was generated from the validated 90-row course table. It contains one proportional marker per launch site and a popup with launch count and observed success rate. The HTML output is `../outputs/launch_sites_folium.html`."),
        code("from pathlib import Path\nimport runpy\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nrunpy.run_path(str(root / 'src/build_folium_map.py'), run_name='__main__')\nprint(root / 'outputs/launch_sites_folium.html')"),
    ],"5. SQL EDA and Launch-Site Map")
    save("06_Plotly_Dash_Dashboard.ipynb",[
        md("## Dashboard\n`../src/dash_app.py` implements the Plotly Dash dashboard with launch-site and orbit filters, landing-success rate by site, and payload-mass distribution by outcome. The app layout and callback were tested with Flask's test client; the layout, dependency endpoint and both filtered figures returned successfully. The app uses the validated 90-row course sample."),
        code("from pathlib import Path\nimport runpy\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nns = runpy.run_path(str(root / 'src/dash_app.py'), run_name='capstone_dash_test')\nclient = ns['app'].server.test_client()\nassert client.get('/').status_code == 200\nassert client.get('/_dash-layout').status_code == 200\nfigures = ns['update']('All', 'All')\nassert len(figures) == 2\nprint('Dash layout and callback verified; figures:', [len(f.data) for f in figures])"),
        md("To open it interactively from the project root, run `python src/dash_app.py` and visit `http://127.0.0.1:8050`.")
    ],"6. Plotly Dash Dashboard")
    model_text=json.dumps(RES['models']['metrics'],indent=2)
    split=RES['models']['split']
    cv_text=json.dumps(RES['models']['cross_validation'],indent=2)
    save("07_Modeling.ipynb",[
        md("## Preparation, model tuning, and evaluation\nThe validated matrix has 90 observations and 80 numeric features; `Class` is 0 for an unsuccessful landing and 1 for a successful landing. The data were split into 72 training and 18 test rows with a stratified 80/20 split and seed 2. Standardization is inside a scikit-learn pipeline for linear models and KNN, so each cross-validation fold fits its scaler using only that fold's training rows. Logistic Regression, SVM, KNN, and Decision Tree were tuned with five-fold stratified GridSearchCV; final metrics below use only the held-out test rows."),
        code("from pathlib import Path\nimport runpy\nroot = Path.cwd()\nif not (root / 'src').exists(): root = root.parent\nrunpy.run_path(str(root / 'src/analyze_model.py'), run_name='__main__')"),
        md(f"## Results\nTrain n={split['train_n']}; test n={split['test_n']}; seed={split['random_state']}. Test metrics: `{model_text}`. Five-fold CV scores and selected parameters: `{cv_text}`. The model selected by mean CV accuracy is **{RES['models']['best_by_cv_accuracy']}**; its held-out confusion matrix (actual rows, predicted columns) is `{RES['models']['best_confusion_matrix']}`."),
        md("### Interpretation\nThe holdout has 18 observations, including six unsuccessful landings, so each error shifts the failure-class estimate substantially. The selected model is chosen from training folds by mean cross-validated accuracy; the test set is used only for the final report. These results are a small-sample course exercise and should not be treated as operational prediction performance."),
    ],"7. Predictive Modeling")
    # Actual best-model confusion matrix as accessible SVG.
    best_name=RES['models']['best_by_cv_accuracy']
    vals=RES['models']['best_confusion_matrix']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="620" height="390" viewBox="0 0 620 390"><rect width="100%" height="100%" fill="white"/>',
         f'<text x="310" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold">{best_name} confusion matrix</text>']
    labels=['Predicted 0','Predicted 1']
    for j,t in enumerate(labels): svg.append(f'<text x="{260+j*150}" y="80" text-anchor="middle" font-family="Arial" font-size="15">{t}</text>')
    for i,truth in enumerate(['Actual 0','Actual 1']):
        svg.append(f'<text x="90" y="{160+i*110}" text-anchor="middle" font-family="Arial" font-size="15">{truth}</text>')
        for j in range(2):
            v=vals[i][j]; x=180+j*150; y=100+i*110
            shade=230-min(150,v*10)
            svg.append(f'<rect x="{x}" y="{y}" width="130" height="90" fill="rgb({shade-20},{shade},{shade})" stroke="#fff"/>')
            svg.append(f'<text x="{x+65}" y="{y+55}" text-anchor="middle" font-family="Arial" font-size="30">{v}</text>')
    svg.append('</svg>')
    (ROOT/'outputs/figures/best_model_confusion_matrix.svg').write_text('\n'.join(svg),encoding='utf-8')

if __name__=='__main__': main()

