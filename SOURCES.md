# Sources and provenance

1. IBM Skills Network archived SpaceX API response: <https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json>. Retrieved 2026-10-22 and saved unchanged at `data/raw/API_call_spacex_api.json` (107 records).
2. IBM Skills Network labeled course table, `dataset_part_2.csv`: <https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv>. Retrieved 2026-10-22 and saved at `data/raw/dataset_part_2.csv` (90 rows, 18 columns).
3. IBM Skills Network prepared model features, `dataset_part_3.csv`: <https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_3.csv>. Supplied by the user and retained at `data/processed/dataset_part_3.csv` (90 rows, 80 columns).
4. Wikipedia, *List of Falcon 9 and Falcon Heavy launches*, revision 987426997, timestamp 2020-11-06 23:51:31 UTC: <https://en.wikipedia.org/w/index.php?oldid=987426997>. Retrieved as `data/raw/wikipedia_falcon_launch_history_2020.html`; the scraper filters dated launches through 2020-11-05. The scrape has 97 unique numbered rows and is not substituted for the IBM 90-row modeling sample.
5. Current Wikipedia page for context: <https://en.wikipedia.org/wiki/List_of_Falcon_9_and_Falcon_Heavy_launches>.

The raw API response, labeled IBM table, and dated Wikipedia snapshot are preserved in `data/raw/`. The feature matrix was supplied separately. Model target labels are read directly from IBM's labeled course table and checked against the feature matrix row order and decoded one-hot categories.
