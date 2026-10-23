"""Validate the supplied feature matrix against IBM's labeled course table,
then run SQL summaries and baseline models.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "data/processed/dataset_part_3.csv"
LABELED_DATA = ROOT / "data/raw/dataset_part_2.csv"
LABELS = ROOT / "data/processed/landing_success_labels.csv"
OUT = ROOT / "outputs"


def decode_one_hot(df: pd.DataFrame, prefix: str, output: str, allow_empty=False):
    cols = [c for c in df.columns if c.startswith(prefix)]
    sums = df[cols].sum(axis=1)
    if not (sums.eq(1).all() or (allow_empty and sums.isin([0, 1]).all())):
        raise ValueError(f"Invalid one-hot group {prefix}: {sums.value_counts().to_dict()}")
    values = []
    for row in df[cols].to_numpy():
        hot = np.flatnonzero(row)
        values.append(cols[hot[0]][len(prefix):] if len(hot) else "Unknown")
    return pd.Series(values, name=output)


def make_dataset():
    X = pd.read_csv(FEATURES)
    source = pd.read_csv(LABELED_DATA)
    if len(X) != len(source):
        raise ValueError(f"Feature/source row mismatch: {len(X)} vs {len(source)}")
    if not np.array_equal(X["FlightNumber"].astype(int), source["FlightNumber"].astype(int)):
        raise ValueError("Feature rows do not align with the labeled IBM course table")
    y = source["Class"].astype("int64").rename("Class")
    for col, prefix in [("Orbit", "Orbit_"), ("LaunchSite", "LaunchSite_"), ("LandingPad", "LandingPad_"), ("Serial", "Serial_")]:
        decoded = decode_one_hot(X, prefix, col, allow_empty=(col == "LandingPad"))
        expected = source[col].fillna("Unknown").astype(str)
        if not np.array_equal(decoded.astype(str).to_numpy(), expected.to_numpy()):
            raise ValueError(f"Feature category {col} does not align with the labeled course source")
    LABELS.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"FlightNumber": X["FlightNumber"].astype(int), "Class": y}).to_csv(LABELS, index=False)
    raw = source.copy()
    raw["LandingPad"] = raw["LandingPad"].fillna("Unknown")
    raw.to_csv(ROOT / "data/processed/course_model_dataset.csv", index=False)
    return X, y, raw


def write_svg_bar(path: Path, title: str, labels: list[str], values: list[float], ymax=1.0, suffix=""):
    w, h, left, bottom, top, right = 900, 430, 100, 325, 72, 30
    plotw, ploth = w-left-right, bottom-top
    bw = min(65, plotw / max(1, len(labels)) * .58)
    colors = ["#3366cc", "#dc3912", "#109618", "#ff9900", "#990099", "#0099c6"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{w/2}" y="36" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold">{title}</text>']
    for tick in range(0, 6):
        val = ymax * tick / 5
        ypix = bottom - ploth * tick / 5
        parts += [f'<line x1="{left}" y1="{ypix:.1f}" x2="{w-right}" y2="{ypix:.1f}" stroke="#ddd"/>',
                  f'<text x="{left-12}" y="{ypix+5:.1f}" text-anchor="end" font-family="Arial" font-size="14">{val:.1f}{suffix}</text>']
    for i, (label, val) in enumerate(zip(labels, values)):
        x = left + (i+.5)*plotw/max(1, len(labels)) - bw/2
        bh = max(0, min(ploth, val/ymax*ploth))
        parts += [f'<rect x="{x:.1f}" y="{bottom-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{colors[i%len(colors)]}"/>',
                  f'<text x="{x+bw/2:.1f}" y="{bottom-bh-8:.1f}" text-anchor="middle" font-family="Arial" font-size="13">{val:.2f}</text>',
                  f'<text x="{x+bw/2:.1f}" y="{bottom+24}" text-anchor="middle" font-family="Arial" font-size="12">{label}</text>']
    parts += [f'<text x="24" y="{h/2}" transform="rotate(-90 24 {h/2})" text-anchor="middle" font-family="Arial" font-size="15">Success rate</text>', '</svg>']
    path.write_text('\n'.join(parts), encoding='utf-8')


def sql_analysis(raw: pd.DataFrame):
    db = sqlite3.connect(":memory:")
    raw.to_sql("launches", db, index=False)
    queries = {
        "site_success": "SELECT LaunchSite, COUNT(*) AS launches, ROUND(AVG(Class), 3) AS success_rate FROM launches GROUP BY LaunchSite ORDER BY success_rate DESC",
        "orbit_success": "SELECT Orbit, COUNT(*) AS launches, ROUND(AVG(Class), 3) AS success_rate FROM launches GROUP BY Orbit ORDER BY success_rate DESC",
        "payload_by_success": "SELECT Class, COUNT(*) AS launches, ROUND(AVG(PayloadMass), 1) AS mean_payload_kg FROM launches GROUP BY Class ORDER BY Class",
        "year_success": "SELECT CAST(strftime('%Y', Date) AS INTEGER) AS year, COUNT(*) AS launches, SUM(Class) AS successful_launches, ROUND(AVG(Class), 3) AS success_rate FROM launches GROUP BY year ORDER BY year",
    }
    results = {}
    sql_file = ROOT / "outputs/sql/capstone_queries.sql"
    sql_file.write_text('\n\n'.join(f'-- {name}\n{query};' for name, query in queries.items())+'\n', encoding='utf-8')
    for name, q in queries.items():
        df = pd.read_sql_query(q, db)
        df.to_csv(OUT / "sql" / f"{name}.csv", index=False)
        results[name] = df.to_dict(orient="records")
    db.close()
    return results


def standardize(a, mu=None, sd=None):
    if mu is None:
        mu = a.mean(axis=0)
        sd = a.std(axis=0)
        sd[sd == 0] = 1
    return (a-mu)/sd, mu, sd


def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1/(1+np.exp(-z))


def fit_logistic(X, y):
    w = np.zeros(X.shape[1]); b = 0.0; lr = .08; reg = .02
    for _ in range(1500):
        p = sigmoid(X@w+b)
        w -= lr*((X.T@(p-y))/len(y) + reg*w)
        b -= lr*float(np.mean(p-y))
    return lambda z: (sigmoid(z@w+b) >= .5).astype(int)


def fit_linear_svm(X, y):
    yy = np.where(y == 1, 1.0, -1.0); w = np.zeros(X.shape[1]); b = 0.0
    lr = .006; C = .5
    for epoch in range(1200):
        margin = yy*(X@w+b)
        active = margin < 1
        gradw = w - (C/len(y))*(X[active].T@yy[active])
        gradb = -(C/len(y))*yy[active].sum()
        step = lr/(1+epoch/500)
        w -= step*gradw; b -= step*gradb
    return lambda z: ((z@w+b) >= 0).astype(int)


def fit_knn(X, y, k=5):
    def predict(z):
        out=[]
        for row in z:
            idx=np.argsort(((X-row)**2).sum(axis=1))[:k]
            out.append(int(y[idx].mean() >= .5))
        return np.array(out, dtype=int)
    return predict


def fit_tree(X, y, max_depth=3, min_leaf=3):
    def gini(labels):
        if len(labels)==0: return 0
        p=labels.mean(); return 2*p*(1-p)
    def grow(ids, depth):
        labels=y[ids]; pred=int(labels.mean() >= .5)
        if depth>=max_depth or len(ids)<2*min_leaf or len(np.unique(labels))==1:
            return (pred,)
        parent=gini(labels); best=None
        for j in range(X.shape[1]):
            vals=np.unique(X[ids,j])
            for threshold in (vals[:-1]+vals[1:])/2:
                left=ids[X[ids,j]<=threshold]; right=ids[X[ids,j]>threshold]
                if len(left)<min_leaf or len(right)<min_leaf: continue
                gain=parent-(len(left)*gini(y[left])+len(right)*gini(y[right]))/len(ids)
                if best is None or gain>best[0]: best=(gain,j,threshold,left,right)
        if best is None or best[0]<=1e-12: return (pred,)
        _,j,t,left,right=best
        return (j,t,grow(left,depth+1),grow(right,depth+1))
    tree=grow(np.arange(len(y)),0)
    def predict(z):
        ans=[]
        for row in z:
            node=tree
            while len(node)>1:
                j,t,l,r=node; node=l if row[j]<=t else r
            ans.append(node[0])
        return np.array(ans,dtype=int)
    return predict, tree


def metrics(y, pred):
    tn=int(((y==0)&(pred==0)).sum()); fp=int(((y==0)&(pred==1)).sum())
    fn=int(((y==1)&(pred==0)).sum()); tp=int(((y==1)&(pred==1)).sum())
    acc=(tn+tp)/len(y); precision=tp/(tp+fp) if tp+fp else 0
    recall=tp/(tp+fn) if tp+fn else 0; f1=2*precision*recall/(precision+recall) if precision+recall else 0
    return {"accuracy":acc,"precision":precision,"recall":recall,"f1":f1,"tn":tn,"fp":fp,"fn":fn,"tp":tp}


def run_models(Xdf, yser):
    X = Xdf.to_numpy(dtype=float)
    y = yser.to_numpy(dtype=int)
    train, test = train_test_split(
        np.arange(len(y)), test_size=0.2, random_state=2, stratify=y
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
    scaled = lambda estimator: Pipeline([
        ("scale", StandardScaler()), ("model", estimator)
    ])
    specs = {
        "Logistic Regression": (
            scaled(LogisticRegression(max_iter=3000, random_state=2)),
            {"model__C": [0.01, 0.1, 1, 10]},
        ),
        "SVM": (
            scaled(SVC()),
            [
                {"model__kernel": ["linear"], "model__C": [0.1, 1, 10]},
                {"model__kernel": ["rbf"], "model__C": [0.1, 1, 10],
                 "model__gamma": ["scale", "auto"]},
            ],
        ),
        "KNN": (
            scaled(KNeighborsClassifier()),
            {"model__n_neighbors": [3, 5, 7, 9],
             "model__weights": ["uniform", "distance"]},
        ),
        "Decision Tree": (
            DecisionTreeClassifier(random_state=2),
            {"criterion": ["gini", "entropy"],
             "max_depth": [None, 2, 3, 4, 5, 8],
             "min_samples_leaf": [1, 2, 4]},
        ),
    }
    fitted = {}
    metrics_by_model = {}
    predictions = {}
    for name, (estimator, grid) in specs.items():
        search = GridSearchCV(estimator, grid, scoring="accuracy", cv=cv, n_jobs=1)
        search.fit(X[train], y[train])
        pred = search.best_estimator_.predict(X[test]).astype(int)
        predictions[name] = pred.tolist()
        metrics_by_model[name] = metrics(y[test], pred)
        fitted[name] = {
            "cv_accuracy": float(search.best_score_),
            "test_accuracy": float(metrics_by_model[name]["accuracy"]),
            "best_params": search.best_params_,
        }
    best = max(fitted, key=lambda name: fitted[name]["cv_accuracy"])
    best_cm = metrics_by_model[best]
    return {
        "split": {"train_n": len(train), "test_n": len(test), "random_state": 2,
                  "stratified": True, "test_indices": test.tolist()},
        "test_actual": y[test].tolist(),
        "predictions": predictions,
        "metrics": metrics_by_model,
        "cross_validation": fitted,
        "best_by_cv_accuracy": best,
        "best_confusion_matrix": [[best_cm["tn"], best_cm["fp"]],
                                  [best_cm["fn"], best_cm["tp"]]],
    }


def main():
    (OUT/"sql").mkdir(parents=True,exist_ok=True); (OUT/"figures").mkdir(parents=True,exist_ok=True)
    X,y,raw=make_dataset()
    rates_site=raw.groupby('LaunchSite').agg(launches=('Class','size'),success_rate=('Class','mean')).sort_values('success_rate',ascending=False)
    rates_orbit=raw.groupby('Orbit').agg(launches=('Class','size'),success_rate=('Class','mean')).sort_values('success_rate',ascending=False)
    rates_site.to_csv(OUT/'site_success_rates.csv'); rates_orbit.to_csv(OUT/'orbit_success_rates.csv')
    write_svg_bar(OUT/'figures/site_success_rates.svg','Landing success by launch site',rates_site.index.tolist(),rates_site.success_rate.tolist())
    write_svg_bar(OUT/'figures/orbit_success_rates.svg','Landing success by orbit',rates_orbit.index.tolist(),rates_orbit.success_rate.tolist())
    sql=sql_analysis(raw)
    models=run_models(X,y)
    report={
      "source_features":"user-provided dataset_part_3.csv (90 rows, 80 columns)",
      "target_source":"Class column from downloaded official IBM course dataset_part_2.csv",
      "rows":len(raw),"feature_columns":X.shape[1],"class_counts":y.value_counts().sort_index().to_dict(),
      "site_success":rates_site.reset_index().to_dict(orient='records'),
      "orbit_success":rates_orbit.reset_index().to_dict(orient='records'),
      "sql":sql,"models":models,
    }
    (OUT/'analysis_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    summary = {
        "rows": report["rows"],
        "features": report["feature_columns"],
        "class_counts": report["class_counts"],
        "site_success": report["site_success"],
        "models": {
            name: {
                "cv_accuracy": models["cross_validation"][name]["cv_accuracy"],
                **metrics,
                "best_params": models["cross_validation"][name]["best_params"],
            }
            for name, metrics in models["metrics"].items()
        },
        "selected_model": models["best_by_cv_accuracy"],
        "confusion_matrix": models["best_confusion_matrix"],
    }
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
