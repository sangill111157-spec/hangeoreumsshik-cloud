import json

SCHEMA_KEYS = {"id", "section", "tc_in", "tc_out", "model_img", "model_vid", "char", "img_prompt", "motion_prompt", "note"}

def validate_shots():
    with open("shots.json", "r", encoding="utf-8") as f:
        shots = json.load(f)

    print(f"Total Shots: {len(shots)}")

    for idx, s in enumerate(shots, 1):
        missing_keys = SCHEMA_KEYS - set(s.keys())
        assert not missing_keys, f"Shot {s.get('id')} missing keys: {missing_keys}"
        assert s["tc_in"] is not None, f"Shot {s.get('id')} tc_in must not be null"
        assert s["tc_out"] is not None, f"Shot {s.get('id')} tc_out must not be null"
        assert s["char"] in ["Y", "N"], f"Shot {s.get('id')} char must be Y or N"

    print("[SUCCESS] shots.json Soundmap Schema Validation Passed Successfully!")

if __name__ == "__main__":
    validate_shots()
