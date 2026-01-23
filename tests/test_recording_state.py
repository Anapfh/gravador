from pathlib import Path
import json

STATE_FILE = Path("output/recording_state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"status": "idle"}

def test_idle_state():
    state = load_state()
    assert state["status"] == "idle"

if __name__ == "__main__":
    test_idle_state()
    print("OK — estado idle válido")
