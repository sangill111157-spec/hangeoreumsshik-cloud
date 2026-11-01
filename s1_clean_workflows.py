# -*- coding: utf-8 -*-
with open('.github/workflows/rgon_external_brain_kitchen.yml', 'r', encoding='utf-8') as f:
    lines = f.readlines()
out1 = []
in_sched = False
for line in lines:
    if line.strip().startswith('schedule:') or 'SCHEDULE_DISABLED' in line:
        in_sched = True
        out1.append('# [SCHEDULE_DISABLED_FOR_ZERO_SPAM]\n')
        continue
    if in_sched:
        if line.strip().startswith('- cron:'):
            out1.append('# ' + line)
            continue
        elif line.strip().startswith('#'):
            out1.append(line)
            continue
        else:
            in_sched = False
    out1.append(line)

with open('.github/workflows/rgon_external_brain_kitchen.yml', 'w', encoding='utf-8') as f:
    f.writelines(out1)

with open('.github/workflows/hangeoreumsshik_cloud.yml', 'r', encoding='utf-8') as f:
    lines2 = f.readlines()
out2 = []
in_sched2 = False
for line in lines2:
    if line.strip().startswith('schedule:'):
        in_sched2 = True
        out2.append('  # schedule: [SCHEDULE_DISABLED_FOR_ZERO_SPAM]\n')
        continue
    if in_sched2:
        if line.strip().startswith('- cron:'):
            out2.append('  # ' + line)
            continue
        elif line.strip().startswith('#'):
            out2.append('  # ' + line)
            continue
        else:
            in_sched2 = False
    out2.append(line)

with open('.github/workflows/hangeoreumsshik_cloud.yml', 'w', encoding='utf-8') as f:
    f.writelines(out2)

print("All workflow schedules cleanly commented out!")
