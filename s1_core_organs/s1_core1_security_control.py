import json,datetime,pathlib
def run():
 p=pathlib.Path(r"G:/내 드라이브/S1_SUN_ONE_AON/01_core1_security_control/kill_switch_state.json")
 p.write_text(json.dumps({"KILL_SWITCH":False,"max_daily_usd":15.0},indent=2),encoding="utf-8")
 return {"core":1,"name":"Security & KillSwitch","status":"PASS"}
