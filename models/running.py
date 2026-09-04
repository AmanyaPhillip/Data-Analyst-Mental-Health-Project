import joblib
import pandas as pd

model = joblib.load("06_trend_direction_model.joblib")

row = pd.DataFrame([{
    "source": "perceived_mh_annual",
    "geo": "Ontario",
    "geo_level": "province",
    "sex": "Both",
    "age_group": "Total, 18 years and over",
    "indicator": "Perceived mental health, fair or poor",
    "value_t": 16.3,          # the current known % for this series
    "year_t": 2023,
    "year_gap": 2,             # years until the next expected cycle
    "quality_flag_t": "ok",    # or "E" if that reading was flagged use-with-caution
    "ci_width_t": 3.5,         # ci_high - ci_low at time t, if known (else leave NaN)
}])

model.predict(row)          # -> array(['Up'], dtype=object)
model.predict_proba(row)    # -> [[P(Down), P(Up)]]
model.classes_              # -> ['Down' 'Up']  (order for predict_proba columns)