"""Generate synthetic ICET Aluva-bus dataset and train a delay-prediction model."""
import numpy as np, pandas as pd, json
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

rng = np.random.default_rng(42)
STOPS = [("Vidhya Niketan School Ground","7:30"),("Pump Jn","7:35"),("Thottumugham","7:40"),
 ("Kuttamassery","7:50"),("Marampilly","7:55"),("Manjappetty","8:00"),("Mudikkal","8:10"),
 ("Perumbavoor","8:20"),("Pulluvazhy","8:30"),("Payipra","8:35"),("Ilahia Arts College","8:40"),("ICET","8:45")]
mins = lambda t: int(t.split(":")[0])*60+int(t.split(":")[1])
DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat"]
day_factor = dict(zip(DAYS,[1.2,1.0,1.0,1.0,1.1,0.7]))
rows=[]
for d in pd.bdate_range("2026-06-15", periods=120, freq="C", weekmask="Mon Tue Wed Thu Fri Sat"):
    dow = DAYS[d.dayofweek]
    rain = int(rng.random() < (0.55 if d.month in (6,7,8) else 0.25))
    traffic = int(rng.choice([0,1,2], p=[.3,.45,.25]))        # 0 low, 1 medium, 2 high
    start_delay = rng.normal(0.5,1.0)                           # driver start variation
    delay = start_delay
    prev = mins(STOPS[0][1])
    for i,(s,t) in enumerate(STOPS):
        sched = mins(t)
        if i>0:
            seg = sched-prev
            # delay accumulates per segment minute: traffic, rain, weekday effects
            rate = 0.03 + 0.045*traffic + 0.03*rain
            delay += seg*rate*day_factor[dow] + rng.normal(0,0.6)
            if s=="Perumbavoor": delay += rng.exponential(0.8)*(1+traffic)  # busy town
        prev = sched
        delay = max(delay,-2)
        a = sched+delay
        rows.append(dict(date=d.date(),day_of_week=dow,weather="Rain" if rain else "Clear",
            traffic=["Low","Medium","High"][traffic],stop=s,stop_order=i+1,scheduled_time=t,
            scheduled_min=sched,delay_min=round(delay,1),
            actual_arrival=f"{int(a//60)}:{int(round(a%60))%60:02d}"))
df=pd.DataFrame(rows); df.to_csv("bus_arrival_dataset.csv",index=False)
print(df.shape); print(df.head(3).to_string())

def feats(d):
    X=pd.DataFrame({"order":d.stop_order,"traffic":d.traffic.map({"Low":0,"Medium":1,"High":2}),
        "rain":(d.weather=="Rain").astype(int)})
    X["order_x_traffic"]=X.order*X.traffic; X["order_x_rain"]=X.order*X.rain
    for k in DAYS[1:]: X["day_"+k]=(d.day_of_week==k).astype(int)
    X["perumbavoor_x_traffic"]=(d.stop=="Perumbavoor")*X.traffic
    return X
X,y=feats(df),df.delay_min
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=1)
lin=Ridge(alpha=1).fit(Xtr,ytr); gb=GradientBoostingRegressor(random_state=1).fit(Xtr,ytr)
for n,m in [("Ridge",lin),("GradBoost",gb)]:
    p=m.predict(Xte); print(n,"MAE",round(mean_absolute_error(yte,p),2),"R2",round(r2_score(yte,p),3))
lin=Ridge(alpha=1).fit(X,y)
print(json.dumps({"b":round(lin.intercept_,4),"w":{c:round(v,4) for c,v in zip(X.columns,lin.coef_)}}))
