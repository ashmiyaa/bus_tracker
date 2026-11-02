"""Flask backend: trains the delay model from the CSV and serves predictions.
Run:  pip install -r requirements.txt   then   python app.py
Test: http://localhost:5000/predict?stop=Perumbavoor&day=Mon&traffic=Medium&weather=Clear
"""
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.linear_model import Ridge

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
TRAFFIC = {"Low": 0, "Medium": 1, "High": 2}

df = pd.read_csv("bus_arrival_dataset.csv")
STOPS = (df[["stop", "stop_order", "scheduled_min"]]
         .drop_duplicates().sort_values("stop_order").set_index("stop"))

def features(order, traffic, rain, day, stop):
    row = {"order": order, "traffic": traffic, "rain": rain,
           "order_x_traffic": order * traffic, "order_x_rain": order * rain}
    for d in DAYS[1:]:
        row["day_" + d] = int(day == d)
    row["perumbavoor_x_traffic"] = int(stop == "Perumbavoor") * traffic
    return row

X = pd.DataFrame([features(r.stop_order, TRAFFIC[r.traffic], int(r.weather == "Rain"),
                           r.day_of_week, r.stop) for r in df.itertuples()])
model = Ridge(alpha=1).fit(X, df.delay_min)

def fmt(m):
    m = round(m)
    return f"{m // 60}:{m % 60:02d}"

app = Flask(__name__)

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.get("/health")
def health():
    return jsonify(status="ok", records=len(df))

@app.get("/predict")
def predict():
    stop = request.args.get("stop", "ICET")
    day = request.args.get("day", "Mon")
    traffic = request.args.get("traffic", "Medium")
    weather = request.args.get("weather", "Clear")
    if stop not in STOPS.index or day not in DAYS or traffic not in TRAFFIC:
        return jsonify(error="invalid stop, day or traffic"), 400
    s = STOPS.loc[stop]
    x = pd.DataFrame([features(int(s.stop_order), TRAFFIC[traffic],
                               int(weather == "Rain"), day, stop)])
    delay = max(float(model.predict(x)[0]), 0)
    return jsonify(stop=stop, scheduled=fmt(s.scheduled_min),
                   delay_min=round(delay, 1),
                   predicted=fmt(s.scheduled_min + delay))

if __name__ == "__main__":
    app.run(debug=True)
