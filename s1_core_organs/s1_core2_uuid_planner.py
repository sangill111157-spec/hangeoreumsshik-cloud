import json,datetime,pathlib
def run():
 uid="S1-"+datetime.datetime.now().strftime("%Y%m%d")+"-HGS-CH1-001"
 p=pathlib.Path(r"G:/내 드라이브/S1_SUN_ONE_AON/02_core2_uuid_planning/s1_uuid_ledger.json")
 p.write_text(json.dumps([{"uuid":uid,"gate1":True}],indent=2),encoding="utf-8")
 return {"core":2,"name":"UUID Planner","uuid":uid,"status":"PASS"}
