import os
for f in ["rgon_manual_gate_state.json.tmp", "rgon_aon_hydro_state.json.tmp", "rgon_aon_nexus_state.json.tmp"]:
    if os.path.exists(f):
        try:
            os.system(f'attrib -r "{f}"')
            os.remove(f)
            print("Removed:", f)
        except Exception as e:
            print("Error removing", f, e)
print("Done cleaning tmp files")
