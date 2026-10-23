# IBM Applied Data Science Capstone - Falcon 9 Landing Prediction

**Current submission:** [40-slide final PDF](reports/Capstone_Entrega_Final.pdf).

Public repository: https://github.com/joaoltrevisan/spacex-falcon9-capstone

The current presentation follows the IBM template sequence: dedicated slides for each of the six EDA charts, all ten SQL questions, three Folium views, three Dash results, four classifiers, and the confusion matrix. It includes data collection, scraping, wrangling and model flowcharts, plus the direct URLs of all notebooks.

The PDF uses visible, selectable text, clickable repository/notebook links, six EDA charts, all ten SQL laboratory queries and results, three Folium screenshots, three Dash screenshots, model comparison, confusion matrix and conclusions. Seven notebooks have been executed without cell errors.

The older `Capstone_Final_Revisado.pdf` and `Relatorio_Capstone.pdf`, `.pptx` and `.md` are superseded historical drafts; they do not contain this correction. Do not use them for the current submission. The current PDF source is `src/build_template_aligned.py`; the earlier presentation generators are legacy drafts.

## Evidence and data boundaries

| Stage | Source and result |
|---|---|
| API | Archived IBM API JSON; 107 records normalized into 18 fields; no live API enrichment claimed |
| Web scraping | Wikipedia revision 987426997; 97 dated rows through 2020-11-05 |
| Wrangling / modeling | 90-row IBM labeled table and supplied 90 × 80 encoded matrix; all feature values, flight order and categories checked |
| EDA | Six required chart types from the 90-row modeling sample |
| SQL | Separate 101-row `Spacex_SQL.csv`; ten exact lab queries in `src/sql_lab.py`; result CSVs and SQL in `outputs/sql_lab/` |
| Folium | Separate 56-record geographic dataset; site map, color-coded outcomes, and approximate coastline/road distances |
| Dash | Separate 56-record dashboard dataset; site counts/ratios and interactive payload range |
| Models | Four classifiers; five-fold stratified training CV; separate stratified 18-row holdout |

These sources have different coverage. Their counts and success rates must not be combined. Mission outcome and landing outcome are distinct concepts.

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/collect_api.py
python src/scrape_wikipedia.py
python src/analyze_model.py
python src/sql_lab.py
python src/build_folium_map.py
python src/build_template_aligned.py
python src/dash_app.py
```

Open http://127.0.0.1:8050 for Dash. Open the three `outputs/launch_*_folium.html` maps in a browser; external map tiles require internet access. Browser screenshots used by the PDF are committed under `outputs/figures/`. The PDF builder uses those verified screenshots rather than creating new browser captures.

The seven notebooks in `notebooks/` use local data and display executed outputs. `src/build_project_artifacts.py` is a historical draft generator and should not be used to recreate these notebooks.

## Geographic measurement

The map uses the course dataset coordinates. Approximate points were selected on visible OpenStreetMap tiles using Folium MousePosition on 23 October 2026: coastline (28.56268, -80.56789), Samuel C. Phillips Parkway (28.56268, -80.57077). Haversine distances from CCAFS LC-40 are 0.925 km and 0.645 km. These are straight-line distances to selected points, not surveyed nearest distances or driving routes.

## Primary sources

IBM source base: https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/

- `datasets/API_call_spacex_api.json`
- `datasets/dataset_part_2.csv`
- `datasets/spacex_launch_geo.csv`
- `datasets/spacex_launch_dash.csv`
- `labs/module_2/data/Spacex.csv`
- `labs/module_5/ds-capstone-template-coursera.pptx`
- `labs/module_5/Submission_Overview_and_Instructions.pdf`
- Wikipedia: https://en.wikipedia.org/w/index.php?oldid=987426997

## Results

Decision Tree selected by CV accuracy (0.877); holdout accuracy 0.833, precision 0.846, recall 0.917 and F1 0.880. Confusion matrix: `[[4, 2], [1, 11]]`. The holdout contains only 18 observations, so the ranking is tentative.
