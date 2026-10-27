import apscheduler.events as ev

events = {k: v for k, v in ev.__dict__.items() if isinstance(v, int) and 'JOB' in k}
for k, v in sorted(events.items(), key=lambda x: x[1]):
    print(f"{k} = {v} (hex: {hex(v)})")
