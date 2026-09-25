import os
import pandas as pd
from storage import load_orders

LEARNING_FILE=os.path.join("data","trades","learning_feedback.csv")

def record_feedback(order_id, outcome, note=""):
    os.makedirs(os.path.dirname(LEARNING_FILE),exist_ok=True)
    row=pd.DataFrame([{"order_id":order_id,"outcome":outcome,"note":note}])
    if os.path.exists(LEARNING_FILE): row.to_csv(LEARNING_FILE,mode="a",header=False,index=False)
    else: row.to_csv(LEARNING_FILE,index=False)

def learning_report():
    orders=load_orders()
    if orders is None or orders.empty:
        return {"trades":0,"wins":0,"losses":0,"win_rate":None,"avg_pnl":None,"message":"No completed paper trades yet."}
    sells=orders[orders.get("side","")=="SELL"].copy()
    if sells.empty:
        return {"trades":0,"wins":0,"losses":0,"win_rate":None,"avg_pnl":None,"message":"No completed paper exits yet."}
    pnl=pd.to_numeric(sells.get("realized_pnl"),errors="coerce").dropna()
    wins=int((pnl>0).sum()); losses=int((pnl<=0).sum())
    return {"trades":len(pnl),"wins":wins,"losses":losses,"win_rate":round(wins/len(pnl)*100,1),"avg_pnl":round(float(pnl.mean()),2),"message":"Statistics are descriptive; the system does not rewrite its own strategy automatically."}

def mistakes_by_reason():
    orders=load_orders()
    if orders is None or orders.empty or "realized_pnl" not in orders.columns:
        return pd.DataFrame()
    x=orders[orders["side"]=="SELL"].copy()
    if x.empty:return x
    x["realized_pnl"]=pd.to_numeric(x["realized_pnl"],errors="coerce")
    return x.groupby("reason",dropna=False)["realized_pnl"].agg(["count","mean","sum"]).reset_index()
