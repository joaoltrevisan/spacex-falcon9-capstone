# IBM Applied Data Science Capstone - Falcon 9 Landing Prediction

This project analyzes whether a Falcon 9 first stage lands successfully. The final 23-slide presentation is `reports/Relatorio_Capstone.pdf` (editable source: `reports/Relatorio_Capstone.pptx`). The notebooks, scripts, data and analysis outputs are included alongside it.

Public repository: https://github.com/joaoltrevisan/spacex-falcon9-capstone

## Project contents

| Stage | Included work | Verification |
|---|---|---|
| Presentation and executive summary | `reports/Relatorio_Capstone.pdf` and `.pptx` | 23 slides aligned to the Mark criteria, including API, scraping, wrangling, visual and SQL EDA, Folium, Dash, and model results |
| SpaceX API collection | Archived IBM API JSON and `src/collect_api.py` | 107 API launch records normalized into 18 fields |
| Web scraping | Dated Wikipedia revision, scraper, and CSV | 97 dated launch rows through 2020-11-05 |
| Wrangling and target | IBM `dataset_part_2.csv` and supplied `dataset_part_3.csv` | 90 rows aligned by flight number and decoded categories; target comes from the labeled IBM file |
| EDA visualizations | Original course EDA notebook and figures | Original notebook outputs preserved in `outputs/figures/` |
| SQL EDA | SQLite queries and result CSV files | Site, orbit, payload and year-by-year launch/success summaries |
| Folium map | `src/build_folium_map.py` and `outputs/launch_sites_folium.html` | Launch counts, rates, markers and nearest-site distances |
| Plotly Dash | `src/dash_app.py` | Filters drive an outcome pie chart and payload-versus-outcome scatter plot |
| Predictive analysis | `src/analyze_model.py`, notebook, metrics and confusion matrix | Four classifiers tuned with five-fold stratified GridSearchCV; evaluated on a stratified 18-row holdout |
| Conclusion | Final report | Based on the saved analysis results, with sample-size limits stated |

## Data and scope

- `data/processed/dataset_part_3.csv` is the user-supplied 90 x 80 one-hot feature matrix; it does not contain `Class`.
- `data/raw/dataset_part_2.csv` is the matching labeled IBM course table. The analysis checks row order and decoded categories before using its target labels.
- The archived SpaceX API response has 107 records. The archived Wikipedia tables yield 97 numbered launches through 2020-11-05. They have different coverage and are kept separate from IBM's fixed 90-row modeling sample.
- The Wikipedia source is pinned to revision 987426997 (2020-11-06) so future edits do not change the scrape.

## Run the project

Create a virtual environment, install dependencies, then run:

```bash
python -m pip install -r requirements.txt
python src/collect_api.py
python src/scrape_wikipedia.py
python src/analyze_model.py
python src/build_folium_map.py
```

The provided presentation PDF is ready to upload to Mark. The editable PowerPoint is included for changes.

Start the dashboard from the project root with `python src/dash_app.py`, then open `http://127.0.0.1:8050`.

## Mark and GitHub

The Mark rubric asks for both the presentation PDF and a GitHub repository URL. The public repository above contains the completed project files. The PDF has not been submitted to Mark.
