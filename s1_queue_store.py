# -*- coding: utf-8 -*-
import json, os, time, datetime, hashlib, msvcrt
from pathlib import Path
import s1_ego

BASE = Path(__file__).resolve().parent
QUEUE_FILE = BASE / "s1_ask_queue.json"
QUEUE_LOCK = BASE / "s1_ask_queue.lock"
LEDGER_FILE = BASE / "s1_command_ledger.jsonl"

def now_kst():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def compute_Spec_hashes(space, prompt, wait):
    sp_int = int(space)
    wt_int = int(wait)
    chat_id = s1_ego.KNOWN_CHATS.get(sp_int, "")
    if not chat_id:
        raise ValueError(f"UNKNOWN_CHAT_FOR_SPACE_{sp_int}")
    sent = str(prompt or "").strip()
    if not sent.startswith("[S1_HOP="):
        sent = "[S1_HOP=1/2]\n" + sent
    psha = hashlib.sha256(sent.encode("utf-8")).hexdigest()
    tsig = hashlib.sha256(f"{sp_int}|{chat_id}|{wt_int}|{psha}".encode("utf-8")).hexdigest()
    return sent, psha, tsig, chat_id

class InterProcessLock:
    def __enter__(self):
        self.fh = open(QUEUE_LOCK, "a+", encoding="utf-8")
        deadline = time.time() + 15.0
        while True:
            try:
                self.fh.seek(0)
                msvcrt.locking(self.fh.fileno(), msvcrt.LK_NBLCK, 1)
                return self
            except OSError:
                if time.time() > deadline:
                    self.fh.close()
                    raise TimeoutError("QUEUE_LOCK_TIMEOUT")
                time.sleep(0.05)
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.fh.seek(0)
            msvcrt.locking(self.fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        self.fh.close()

def append_ledger(rec):
    rec["ts"] = now_kst()
    with InterProcessLock():
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def read_queue():
    with InterProcessLock():
        if not QUEUE_FILE.exists():
            return {}
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))

def update_queue_item(req_id, mutator_fn):
    with InterProcessLock():
        q = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else {}
        res = mutator_fn(q, q.get(req_id))
        tmp = BASE / f"s1_ask_queue.{os.getpid()}.tmp"
        tmp.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(QUEUE_FILE))
        return res
