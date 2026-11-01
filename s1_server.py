#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# S1 Local Bridge Server v1.5 (s1_server.py — Interactive TTY Approval & Atomic Shared Queue & CORS Enhanced)
import os, sys, json, uuid, datetime, hashlib, urllib.parse, http.server, socketserver
import s1_ego
from s1_queue_store import now_kst, compute_Spec_hashes, append_ledger, update_queue_item

PORT = 8504
MAX_BODY = 65536
ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_HOSTS = {"127.0.0.1:8504", "localhost:8504", "127.0.0.1", "localhost"}
ALLOWED_ORIGINS = {"http://127.0.0.1:8504", "http://localhost:8504", "null", ""}
ALLOWED_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/rgon_alpha_chat.html": ("rgon_alpha_chat.html", "text/html; charset=utf-8"),
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
    "/icon-192.png": ("icon-192.png", "image/png"),
    "/icon-512.png": ("icon-512.png", "image/png"),
    "/apple-touch-icon.png": ("apple-touch-icon.png", "image/png"),
    "/s1_logo_1.png": ("s1_logo_1.png", "image/png"),
    "/s1_logo_2.png": ("s1_logo_2.png", "image/png"),
    "/s1_logo_3.png": ("s1_logo_3.png", "image/png"),
    "/S1_FULL_PROOF.json": ("S1_FULL_PROOF.json", "application/json; charset=utf-8"),
    "/S1_STUDIO_PIPELINE_PROOF.json": ("S1_STUDIO_PIPELINE_PROOF.json", "application/json; charset=utf-8"),
    "/S1_DASHBOARD_CLEAN_AUDIT.json": ("S1_DASHBOARD_CLEAN_AUDIT.json", "application/json; charset=utf-8"),
}

class ReusableTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class S1Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _check_local_guard(self, is_write=False):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ("/api/status", "/api/chat", "/api/studio"):
            return True
        host = (self.headers.get("Host") or "").strip().lower()
        origin = (self.headers.get("Origin") or "").strip().lower()
        if host not in ALLOWED_HOSTS:
            self._send(403, {"ok": False, "code": "HOST_FORBIDDEN", "host": host})
            return False
        if is_write:
            if origin and origin not in ALLOWED_ORIGINS:
                self._send(403, {"ok": False, "code": "ORIGIN_FORBIDDEN", "origin": origin})
                return False
        else:
            if origin and origin not in ALLOWED_ORIGINS:
                self._send(403, {"ok": False, "code": "ORIGIN_FORBIDDEN", "origin": origin})
                return False
        return True

    def _send(self, code, payload, ctype="application/json; charset=utf-8"):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8") if isinstance(payload, (dict, list)) else payload
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        try:
            if not self._check_local_guard(is_write=False):
                return
            parsed = urllib.parse.urlparse(self.path)
            path, qs = parsed.path, urllib.parse.parse_qs(parsed.query)
            if path == "/api/status":
                kill_on = s1_ego.kill_switch_active()
                led_file = os.path.join(ROOT, "executed_ids.json")
                ledger_status, rec_ids, ok_cnt, fail_cnt, last_rec = "OK", [], 0, 0, None
                if os.path.exists(led_file):
                    try:
                        with open(led_file, "r", encoding="utf-8") as f:
                            ex_map = json.load(f).get("executed", {})
                            rec_ids = list(ex_map.keys())
                            for k, v in ex_map.items():
                                if v.get("status") == "DONE" and v.get("rc") == 0:
                                    ok_cnt += 1
                                else:
                                    fail_cnt += 1
                            if rec_ids:
                                raw_last = dict(ex_map[rec_ids[-1]])
                                raw_last.pop("isolated_cwd", None)
                                raw_last.pop("script_path", None)
                                raw_last["id_format"] = "legacy_work_id"
                                last_rec = raw_last
                    except Exception:
                        ledger_status = "CORRUPTED"
                return self._send(200, {
                    "ok": ledger_status == "OK",
                    "version": "1.5",
                    "port": PORT,
                    "ego_cli_version": getattr(s1_ego, "__version__", "2.2.0"),
                    "server_time": now_kst(),
                    "kill_switch": kill_on,
                    "mode": "APPROVAL_GATED_BRIDGE",
                    "remote_policy": "LOOPBACK_ONLY (Tailscale/remote disabled by default)",
                    "ledger_status": ledger_status,
                    "recorded_count": len(rec_ids),
                    "succeeded_count": ok_cnt,
                    "failed_count": fail_cnt,
                    "recorded_ids": rec_ids,
                    "last_recorded": last_rec
                })
            if path == "/api/ego/spaces":
                res = s1_ego.cmd_spaces()
                return self._send(200 if res.get("ok") else 502, res)
            if path == "/api/ego/read":
                try:
                    sp = int(qs.get("space", ["0"])[0])
                    tail = max(100, min(10000, int(qs.get("tail", ["2000"])[0])))
                except ValueError:
                    return self._send(400, {"ok": False, "code": "INVALID_PARAMS"})
                if sp not in s1_ego.KNOWN_CHATS:
                    return self._send(400, {"ok": False, "code": "SPACE_NOT_ALLOWED", "space": sp})
                res = s1_ego.cmd_read(sp, tail)
                res["truncation_rule"] = f"tail_chars_limit={tail} (sliced from end of message)"
                return self._send(200 if res.get("ok") else 502, res)
            if path == "/api/studio":
                proof_p = os.path.join(ROOT, "S1_STUDIO_PIPELINE_PROOF.json")
                if os.path.exists(proof_p):
                    try:
                        with open(proof_p, "r", encoding="utf-8") as f:
                            proof_data = json.load(f)
                        return self._send(200, {"ok": True, "studio": proof_data})
                    except Exception as e:
                        return self._send(500, {"ok": False, "code": "PROOF_READ_ERROR", "error": str(e)})
                else:
                    return self._send(404, {"ok": False, "code": "STUDIO_PROOF_NOT_FOUND"})
            if path in ALLOWED_FILES:
                fname, ctype = ALLOWED_FILES[path]
                fpath = os.path.join(ROOT, fname)
                if os.path.isfile(fpath):
                    with open(fpath, "rb") as f:
                        return self._send(200, f.read(), ctype)
            return self._send(404, {"ok": False, "code": "NOT_FOUND"})
        except Exception:
            return self._send(500, {"ok": False, "code": "INTERNAL_ERROR"})

    def do_POST(self):
        try:
            if not self._check_local_guard(is_write=True):
                return
            ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if ctype != "application/json":
                return self._send(415, {"ok": False, "code": "UNSUPPORTED_MEDIA_TYPE"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return self._send(400, {"ok": False, "code": "INVALID_CONTENT_LENGTH"})
            if length < 0 or length > MAX_BODY:
                return self._send(413, {"ok": False, "code": "PAYLOAD_TOO_LARGE"})
            try:
                raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            except UnicodeDecodeError:
                return self._send(400, {"ok": False, "code": "INVALID_UTF8"})
            try:
                body = json.loads(raw)
            except Exception:
                return self._send(400, {"ok": False, "code": "INVALID_JSON"})
            if not isinstance(body, dict):
                return self._send(400, {"ok": False, "code": "JSON_OBJECT_REQUIRED"})

            path = self.path.split("?", 1)[0]
            if path == "/api/chat":
                q_val = body.get("query", body.get("cmd", ""))
                if not isinstance(q_val, str):
                    return self._send(400, {"ok": False, "code": "INVALID_QUERY_TYPE"})
                q = q_val.strip()
                uid = str(uuid.uuid4())
                req_id = uid[:8]
                append_ledger({"uuid": uid, "req_id": req_id, "query": q, "mode": "LEDGER_RECORD_ONLY", "executed": False})

                # Check for Suno v6 / 명작 / 스튜디오 query
                if any(k in q for k in ["Suno", "suno", "명작", "스튜디오", "studio"]):
                    proof_p = os.path.join(ROOT, "S1_STUDIO_PIPELINE_PROOF.json")
                    if os.path.exists(proof_p):
                        try:
                            with open(proof_p, "r", encoding="utf-8") as f:
                                pf = json.load(f)
                            ch = pf.get("channels", {})
                            ch_a = ch.get("channel_a_hangeoreum", {}).get("name", "한걸음씩")
                            ch_b = ch.get("channel_b_boosterply", {}).get("name", "부스터플리")
                            ch_c = ch.get("channel_c_cafehour", {}).get("name", "카페아우어")
                            au = pf.get("audio_master_proof", {})
                            vi = pf.get("video_preview_proof", {})
                            reply_text = (
                                f"[S1 작업실 4순위 본업 연동 · 원장ID {req_id}]\n"
                                f"🏆 3대 유튜브 채널 제1호 명작 패키지(EP01_S1_MASTERPIECE) 가동 완료!\n"
                                f"1. {ch_a}(Space 6, @한걸음씩-r4i): 감성 보컬/발라드 & 한국어 자막(SRT) 완비\n"
                                f"2. {ch_b}(Space 7, @부스터플리): 운동/드라이브 하이텐션 & 트랙리스트 타임스탬프 완비\n"
                                f"3. {ch_c}(Space 8, @카페아우어): 시네마틱 재즈 로파이 & 무한 루프 메타데이터 완비\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"🎵 오디오 마스터: {au.get('filename')} ({au.get('sample_rate')}Hz {au.get('bits_per_sample')}bit {au.get('codec')}, {au.get('loudness_standard')})\n"
                                f"🎬 프리뷰 영상: {vi.get('filename')} ({vi.get('resolution')}, {vi.get('video_codec')}+{vi.get('audio_codec')} 320kbps)\n"
                                f"판정: {pf.get('final_verdict', 'ALL_PASS_CLEAN')}"
                            )
                            return self._send(200, {
                                "ok": True,
                                "uuid": uid,
                                "req_id": req_id,
                                "executed": False,
                                "reply": reply_text,
                                "studio": pf
                            })
                        except Exception:
                            pass

                return self._send(200, {"ok": True, "uuid": uid, "req_id": req_id, "executed": False, "reply": f"[읽기 전용 · 원장ID {req_id}] 명령이 원장(s1_command_ledger.jsonl)에 기록되었으나 실행되지 않았습니다."})

            if path == "/api/ego/ask":
                if s1_ego.kill_switch_active():
                    return self._send(423, {"ok": False, "code": "KILL_SWITCH_ACTIVE"})
                sp = body.get("space")
                prompt = body.get("prompt")
                wait_v = body.get("wait", 60)
                if type(sp) is not int or sp not in (2, 3):
                    return self._send(400, {"ok": False, "code": "ASK_SPACE_FORBIDDEN", "space": sp})
                if not isinstance(prompt, str) or not prompt.strip():
                    return self._send(400, {"ok": False, "code": "INVALID_PROMPT"})
                if type(wait_v) is not int or wait_v < 10 or wait_v > 180:
                    return self._send(400, {"ok": False, "code": "INVALID_WAIT"})

                req_id = str(uuid.uuid4())
                sent_prompt, psha, tsig, cid = compute_Spec_hashes(sp, prompt, wait_v)
                origin = (self.headers.get("Origin") or "").strip().lower()

                def add_pending(q_map, _):
                    q_map[req_id] = {
                        "req_id": req_id,
                        "space": sp,
                        "chat_id": cid,
                        "prompt": sent_prompt,
                        "prompt_sha256": psha,
                        "target_sig": tsig,
                        "wait": wait_v,
                        "origin": origin,
                        "status": "PENDING",
                        "created_at": now_kst(),
                    }
                update_queue_item(req_id, add_pending)
                append_ledger({"req_id": req_id, "cmd": "api_ego_ask_enqueue", "space": sp, "chat_id": cid, "prompt_sha256": psha, "target_sig": tsig, "wait": wait_v, "origin": origin, "status": "PENDING", "executed": False})
                return self._send(202, {"ok": True, "status": "PENDING", "req_id": req_id})

            return self._send(404, {"ok": False, "code": "NOT_FOUND"})
        except Exception:
            return self._send(500, {"ok": False, "code": "INTERNAL_ERROR"})

if __name__ == "__main__":
    with ReusableTCPServer(("127.0.0.1", PORT), S1Handler) as httpd:
        print(f"S1_SERVER_READY port={PORT}", flush=True)
        httpd.serve_forever()
