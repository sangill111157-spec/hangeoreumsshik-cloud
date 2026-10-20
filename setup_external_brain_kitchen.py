#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_external_brain_kitchen.py

실행:
    python -X utf8 setup_external_brain_kitchen.py
    python -X utf8 setup_external_brain_kitchen.py --approve
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BRAIN = ROOT / "brain_basket"
TAB_TITLE = "RGON_두뇌장바구니_헌법"

SPREADSHEETS = (
    ("SHIN FAMILY COMMAND CENTER",
     "1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY"),
    ("BLOG AUTOMATION COMMAND CENTER",
     "1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw"),
)

TOKEN_CANDIDATES = (
    Path(r"C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation\config\token.pickle"),
    Path(r"C:\Users\sangi\Downloads\shin-agent\config\token.pickle"),
)

PAPER_CORRECTION = (
    "disposable white paper cup, single-use takeaway paper cup, "
    "no handle, no ceramic mug, no saucer"
)

HEADERS = [
    "분류", "항목명", "세계1위_적용도구", "핵심내용_및_복기규칙",
    "작동장소(외부클라우드)", "상태", "업데이트일시",
]


WORKER_SOURCE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""외부 손질 워커. dry-run/check-brain은 표준 라이브러리만 사용합니다."""
from __future__ import annotations

import argparse
import array
import asyncio
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "brain_basket" / "external_brain_manifest.json"
PAPER_RULE = (
    "disposable white paper cup, single-use takeaway paper cup, "
    "no handle, no ceramic mug, no saucer"
)
RATE = 48000
SECONDS = 10
FPS = 30


def log(text):
    print(text, flush=True)


def run(command, timeout=240):
    result = subprocess.run(
        [str(x) for x in command], stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="replace", timeout=timeout, shell=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"외부 작업 실패 ({result.returncode}): "
            + result.stderr[-6000:]
        )
    return result


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(temporary, path)


class BrainState(TypedDict, total=False):
    topic: str
    style: str
    manifest: dict
    memories: list
    recipe: dict
    errors: list
    retries: int
    passed: bool


def load_brain(state):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(manifest.get("core_constitution", [])) != 5:
        raise RuntimeError("중앙 두뇌 헌법 5원칙이 없습니다.")
    if len(manifest.get("self_reflection_rules", [])) != 3:
        raise RuntimeError("실패 복기 규칙 3개가 없습니다.")
    log("[1/5] 기준 확인: 중앙 두뇌 헌법 5원칙 로드")
    return {"manifest": manifest, "retries": 0}


def recall(state):
    memories = state["manifest"]["self_reflection_rules"]
    log("[2/5] 기억 조회: 종이컵→손잡이 달린 도자기 머그컵 오생성 실패 검색")
    log("      기억: 단순 coffee cup 금지; 종이 재질·일회용·손잡이 없음 강제")
    return {"memories": memories}


def build_recipe(state):
    topic, style = state["topic"], state["style"]
    is_paper = "종이컵" in topic.replace(" ", "") or "paper cup" in topic.lower()
    templates = {
        "반전형": (
            "평범한 한 잔?\n분위기는 다르게.",
            "작은 선택으로\n달라지는 순간.",
            "당신의 한 잔을\n골라보세요.",
        ),
        "공감형": (
            "오늘도 바쁜 당신.",
            "잠깐의 한 잔에\n시선을 머물러요.",
            "나만의 순간을\n만나보세요.",
        ),
        "질문형": (
            "당신의 한 잔은\n어떤 모습인가요?",
            "일상의 장면을\n새롭게 바라보세요.",
            "마음에 드는 순간을\n선택하세요.",
        ),
        "비교형": (
            "같은 한 잔,\n다른 분위기.",
            "작은 디테일에\n시선을 더해요.",
            "당신의 취향으로\n골라보세요.",
        ),
        "스토리형": (
            "하루의 작은 시작.",
            "한 잔의 순간이\n장면이 됩니다.",
            "오늘의 순간을\n만나보세요.",
        ),
    }
    hook, body, cta = templates.get(style, templates["반전형"])
    subject = PAPER_RULE if is_paper else (
        "a single unbranded product representing: " + topic
    )
    prompt = (
        "Photorealistic vertical 9:16 commercial product photograph of "
        + subject
        + ". Warm ivory tabletop, soft daylight, realistic material texture, "
          "single hero product, clear upper negative space for Korean text "
          "added later. No generated text, no logos, no watermark."
    )
    catalog = state["manifest"].get("viral_recipes", [])
    matched = [
        item for item in catalog
        if style in str(item.get("style", ""))
        or style in str(item.get("name", ""))
    ]
    recipe = {
        "topic": topic, "style": style,
        "copy_origin": "local_style_template_not_a_live_Grok_call",
        "consulted_memory": matched or catalog,
        "image_prompt": prompt,
        "negative_prompt": "handle, ceramic mug, saucer, logo, watermark",
        "hook": hook, "body": body, "cta": cta,
        "narration": (
            f"평범한 순간도, 다르게. {topic}. "
            "작은 선택으로 달라지는 분위기. "
            "당신의 일상에서, 지금 만나보세요."
        ),
        "voice": "ko-KR-InJoonNeural",
        "bgm_bpm": 62,
        "ducking": True,
        "video": {
            "width": 540, "height": 960, "fps": 30,
            "frames": 300, "duration_seconds": 10.0,
            "video_codec": "h264", "audio_codec": "aac",
        },
        "approval_required": True,
        "remembered_ui_rule": (
            "빌드 쿼리스트링 및 document.body 직속 모달 유지. "
            "이번 워커는 UI 파일을 수정하지 않음."
        ),
    }
    log("[3/5] 창조: 기억을 적용한 프롬프트·스타일 레시피 생성")
    log("      교정 프롬프트: " + prompt)
    return {"recipe": recipe}


def critic(state):
    recipe = state["recipe"]
    errors = []
    if "종이컵" in state["topic"].replace(" ", "") or "paper cup" in state["topic"].lower():
        for token in (
            "disposable white paper cup",
            "single-use takeaway paper cup",
            "no handle", "no ceramic mug", "no saucer",
        ):
            if token not in recipe.get("image_prompt", ""):
                errors.append("누락된 종이컵 교정: " + token)
    if recipe.get("voice") != "ko-KR-InJoonNeural":
        errors.append("성우 규격 오류")
    if recipe.get("bgm_bpm") != 62 or not recipe.get("ducking"):
        errors.append("BGM/덕킹 규격 오류")
    expected = {
        "width": 540, "height": 960, "fps": 30, "frames": 300,
        "duration_seconds": 10.0, "video_codec": "h264", "audio_codec": "aac",
    }
    if recipe.get("video") != expected:
        errors.append("영상 규격 오류")
    log("[4/5] 실패 검수·Critic: " + ("통과" if not errors else "; ".join(errors)))
    return {"errors": errors, "passed": not errors}


def reflect(state):
    recipe = dict(state["recipe"])
    if state.get("errors"):
        recipe["image_prompt"] += ". " + PAPER_RULE
        recipe["voice"] = "ko-KR-InJoonNeural"
        recipe["bgm_bpm"] = 62
        recipe["ducking"] = True
    return {"recipe": recipe, "retries": state.get("retries", 0) + 1}


def finish(state):
    if not state.get("passed"):
        raise RuntimeError("자기검열 실패: " + "; ".join(state.get("errors", [])))
    log("[5/5] 자동 교정·최종 확인: no handle, no ceramic mug / 사고 루프 PASS")
    return {"passed": True}


def brain_loop(topic, style, lightweight=False):
    initial = {"topic": topic, "style": style}
    if not lightweight:
        try:
            from langgraph.graph import StateGraph, START, END
        except ImportError:
            log("[엔진] LangGraph 미설치: 동일한 제한형 상태 머신으로 폴백")
        else:
            graph = StateGraph(BrainState)
            for name, function in (
                ("load", load_brain), ("recall", recall),
                ("create", build_recipe), ("critic", critic),
                ("reflect", reflect), ("finish", finish),
            ):
                graph.add_node(name, function)
            graph.add_edge(START, "load")
            graph.add_edge("load", "recall")
            graph.add_edge("recall", "create")
            graph.add_edge("create", "critic")

            def route(state):
                if state.get("passed"):
                    return "finish"
                if state.get("retries", 0) < 2:
                    return "reflect"
                return "finish"

            graph.add_conditional_edges(
                "critic", route, {"finish": "finish", "reflect": "reflect"}
            )
            graph.add_edge("reflect", "critic")
            graph.add_edge("finish", END)
            return graph.compile().invoke(initial)

    state = dict(initial)
    for step in (load_brain, recall, build_recipe):
        state.update(step(state))
    for attempt in range(3):
        state.update(critic(state))
        if state["passed"]:
            break
        if attempt < 2:
            state.update(reflect(state))
    state.update(finish(state))
    return state


def find_font():
    candidates = [
        Path(r"C:\Windows\Fonts\malgunbd.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ROOT / "fonts" / "NotoSansKR-Bold.ttf",
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise RuntimeError("한글 폰트가 없습니다. fonts-noto-cjk 또는 맑은 고딕이 필요합니다.")


def frames(recipe, stage):
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    font_path = find_font()
    source = ROOT / "ingredients_basket" / "sample_paper_cup.jpg"
    paper = "종이컵" in recipe["topic"].replace(" ", "") or "paper cup" in recipe["topic"].lower()
    if paper and source.is_file():
        with Image.open(source) as original:
            base = ImageOps.fit(
                ImageOps.exif_transpose(original).convert("RGB"),
                (540, 960), method=Image.Resampling.LANCZOS,
            )
        recipe["visual_source"] = "repository_asset:sample_paper_cup.jpg"
        recipe["visual_verification"] = (
            "사용자 제공 원본. 픽셀 기반 손잡이/재질 자동 판별은 수행하지 않음."
        )
    else:
        base = Image.new("RGB", (540, 960), "#f5f0e7")
        draw = ImageDraw.Draw(base)
        if paper:
            draw.ellipse((130, 665, 423, 711), fill="#d9d2c8")
            draw.polygon(
                [(165, 427), (385, 427), (358, 681), (192, 681)],
                fill="#fffefa", outline="#d5d2ca", width=3,
            )
            draw.ellipse((164, 405, 386, 454), fill="#e9e5dc", outline="#c8c5bc", width=3)
            draw.ellipse((177, 414, 373, 443), fill="#d6d0c4")
            recipe["visual_source"] = "explicit_local_paper_cup_illustration_no_handle"
        else:
            draw.rounded_rectangle(
                (140, 420, 400, 675), radius=30, fill="#e0e6df", outline="#a0afa3", width=3
            )
            recipe["visual_source"] = "generic_concept_card_not_a_product_photo"
        recipe["visual_verification"] = (
            "실사 생성 서비스 호출 없음. 대체 일러스트/컨셉 카드이며 실사로 표시하지 않음."
        )

    def wrap(draw, text, font, width):
        result = []
        for paragraph in text.split("\n"):
            line = ""
            for char in paragraph:
                if line and draw.textlength(line + char, font=font) > width:
                    result.append(line)
                    line = char
                else:
                    line += char
            result.append(line)
        return result

    names = []
    for i, key in enumerate(("hook", "body", "cta")):
        image = base.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle((26, 104, 514, 342), radius=22, fill=(249, 247, 242, 235))
        od.rounded_rectangle((28, 727, 512, 848), radius=23, fill=(18, 32, 33, 231))
        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(str(font_path), 47)
        lines = wrap(draw, recipe[key], font, 438)
        while len(lines) > 3 and font.size > 20:
            font = ImageFont.truetype(str(font_path), font.size - 2)
            lines = wrap(draw, recipe[key], font, 438)
        for line_number, text in enumerate(lines[:3]):
            draw.text(
                (48, 143 + line_number * int(font.size * 1.35)),
                text, font=font, fill="#172d2a", anchor="lt"
            )
        subtitle = recipe["topic"] + " · " + recipe["style"]
        subfont = ImageFont.truetype(str(font_path), 25)
        sublines = wrap(draw, subtitle, subfont, 420)
        while len(sublines) > 3 and subfont.size > 12:
            subfont = ImageFont.truetype(str(font_path), subfont.size - 1)
            sublines = wrap(draw, subtitle, subfont, 420)
        for j, text in enumerate(sublines[:3]):
            draw.text((58, 754 + j * int(subfont.size * 1.25)), text,
                      font=subfont, fill="white", anchor="lt")
        draw.rounded_rectangle((40, 882, 500, 890), radius=4, fill="#b7c5bf")
        draw.rounded_rectangle(
            (40, 882, 40 + round(460 * (0.3, 0.7, 1.0)[i]), 890),
            radius=4, fill="#167e69"
        )
        name = stage / ("scene_" + str(i) + "_" + key + ".jpg")
        image.convert("RGB").save(name, quality=94, subsampling=0)
        names.append(name)
    return names


def stats(path):
    with wave.open(str(path), "rb") as handle:
        rate, channels, count = handle.getframerate(), handle.getnchannels(), handle.getnframes()
        if handle.getsampwidth() != 2:
            raise RuntimeError("PCM16 검증 파일이 아닙니다.")
        samples = array.array("h", handle.readframes(count))
    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        raise RuntimeError("빈 오디오")
    rms = math.sqrt(sum(x * x for x in samples) / len(samples)) / 32768
    return {"duration": count / rate, "channels": channels, "frames": count, "rms": rms}


def tempo_chain(factor):
    result = []
    while factor > 2:
        result.append("atempo=2")
        factor /= 2
    while factor < 0.5:
        result.append("atempo=0.5")
        factor /= 0.5
    result.append("atempo=" + format(factor, ".10f"))
    return ",".join(result)


async def tts_save(text, path):
    import edge_tts
    await asyncio.wait_for(
        edge_tts.Communicate(
            text=text, voice="ko-KR-InJoonNeural", rate="+0%"
        ).save(str(path)), timeout=90
    )


def voice(ffmpeg, recipe, stage):
    raw = stage / "narration_original.mp3"
    error = None
    for attempt in range(3):
        try:
            asyncio.run(tts_save(recipe["narration"], raw))
            if raw.stat().st_size < 1000:
                raise RuntimeError("TTS 결과가 비어 있습니다.")
            break
        except Exception as exc:
            error = exc
            if attempt == 2:
                raise RuntimeError(
                    "TTS 생성 실패. 대본과 다른 샘플 음성으로 조용히 대체하지 않습니다: "
                    + str(error)
                ) from exc
            time.sleep(attempt + 1)
    pcm = stage / "voice_original.wav"
    run([ffmpeg, "-v", "error", "-y", "-i", raw, "-vn", "-ac", "1",
         "-ar", RATE, "-c:a", "pcm_s16le", pcm])
    original = stats(pcm)
    if original["duration"] < 0.25 or original["rms"] < 0.0001:
        raise RuntimeError("원본 성우가 무음이거나 지나치게 짧습니다.")
    factor = original["duration"] / 9.35
    if not 0.6 <= factor <= 1.8:
        raise RuntimeError(
            f"10초 광고에 부적합한 대본 길이입니다(atempo={factor:.3f}). "
            "주제를 짧게 줄여 다시 승인해 주세요."
        )
    aligned = stage / "voice_aligned_10s.wav"
    filters = (
        tempo_chain(factor)
        + ",apad,atrim=duration=9.35,asetpts=PTS-STARTPTS,"
          "loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000,"
          "apad,atrim=duration=9.35,"
          "afade=t=in:st=0:d=0.025,afade=t=out:st=9.27:d=0.08,"
          "adelay=150:all=1,apad,atrim=duration=10,asetpts=PTS-STARTPTS"
    )
    run([ffmpeg, "-v", "error", "-y", "-i", pcm, "-af", filters,
         "-ar", RATE, "-ac", "1", "-c:a", "pcm_s16le", aligned])
    aligned_stats = stats(aligned)
    if aligned_stats["frames"] != RATE * SECONDS or aligned_stats["rms"] < 0.0001:
        raise RuntimeError("성우 10초 PCM 검증 실패")
    output = stage / "trimmed_voice_10s.mp3"
    run([ffmpeg, "-v", "error", "-y", "-i", aligned,
         "-c:a", "libmp3lame", "-b:a", "192k", "-write_xing", "1", output])
    check = stage / "voice_mp3_check.wav"
    run([ffmpeg, "-v", "error", "-y", "-i", output, "-ac", "1",
         "-ar", RATE, "-c:a", "pcm_s16le", check])
    if stats(check)["rms"] < 0.0001:
        raise RuntimeError("성우 MP3 재디코딩 검사 실패")
    recipe["voice_processing"] = {
        "source": "new_edge_tts", "matches_script": True,
        "tempo_factor": factor, "aligned_pcm": aligned_stats,
    }
    return output


def bgm(path):
    beat = 60 / 62
    tau = 2 * math.pi
    notes = ((62, 66, 69, 73), (59, 62, 66, 69), (55, 59, 62, 66))
    hz = [[440 * 2 ** ((n - 69) / 12) for n in chord] for chord in notes]
    data = array.array("f")
    peak = 0.0
    for index in range(RATE * SECONDS):
        t = index / RATE
        left = right = 0.0
        for chord_index, tones in enumerate(hz):
            local = t - chord_index * 4 * beat
            if local < 0 or local > 4 * beat + 0.5:
                continue
            envelope = (1 - math.exp(-local / 0.065))
            envelope *= math.exp(-max(0, local - 4 * beat) / 0.12)
            for j, frequency in enumerate(tones):
                tone = 0.065 * envelope * math.sin(tau * frequency * local)
                pan = (0.2, 0.8, 0.4, 0.65)[j]
                left += tone * math.cos(pan * math.pi / 2)
                right += tone * math.sin(pan * math.pi / 2)
        local_beat = t % beat
        pulse = math.sin(tau * 52 * local_beat) * math.exp(-local_beat / 0.07) * 0.055
        left += pulse
        right += pulse
        fade = min(1, t / 0.15) * min(1, max(0, (10 - t) / 0.65))
        left *= fade
        right *= fade
        data.extend((left, right))
        peak = max(peak, abs(left), abs(right))
    gain = 0.63 / max(peak, 1e-9)
    pcm = array.array("h", (max(-32768, min(32767, round(x * gain * 32767))) for x in data))
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(pcm.tobytes())
    return stats(path)


def render(state, output_root):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        candidate = ROOT / "ffmpeg-8.0.1-full_build" / "bin" / "ffmpeg.exe"
        if candidate.is_file():
            ffmpeg = str(candidate)
    ffprobe = shutil.which("ffprobe")
    if not ffprobe and ffmpeg:
        candidate = Path(ffmpeg).with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
        if candidate.is_file():
            ffprobe = str(candidate)
    if not ffmpeg or not ffprobe:
        raise RuntimeError("실제 미디어 작업에는 FFmpeg와 ffprobe가 필요합니다.")
    import tempfile
    output_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="run_", dir=str(output_root)))
    recipe = state["recipe"]
    recipe["approval"] = {"approved": True, "execution_location": "GitHub Actions" if os.environ.get("GITHUB_ACTIONS") else "local"}
    write_json(stage / "recipe.json", recipe)
    try:
        images = frames(recipe, stage)
        narration = voice(ffmpeg, recipe, stage)
        music = stage / "trimmed_bgm_10s.wav"
        recipe["bgm_processing"] = bgm(music)
        output = stage / "trimmed_ad_10s.mp4"
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
        for image, duration in zip(images, (3, 4, 3)):
            command += ["-loop", "1", "-framerate", "30", "-t", str(duration), "-i", str(image)]
        command += ["-i", str(narration), "-i", str(music)]
        filters = (
            "[0:v]trim=duration=3,setpts=PTS-STARTPTS,setsar=1[v0];"
            "[1:v]trim=duration=4,setpts=PTS-STARTPTS,setsar=1[v1];"
            "[2:v]trim=duration=3,setpts=PTS-STARTPTS,setsar=1[v2];"
            "[v0][v1][v2]concat=n=3:v=1:a=0,fps=30,format=yuv420p[v];"
            "[3:a]aresample=48000,aformat=channel_layouts=stereo,"
            "apad,atrim=duration=10,asetpts=PTS-STARTPTS,asplit=2[vo][side];"
            "[4:a]aresample=48000,aformat=channel_layouts=stereo,"
            "atrim=duration=10,asetpts=PTS-STARTPTS,volume=0.23[m];"
            "[m][side]sidechaincompress=threshold=0.025:ratio=4:"
            "attack=15:release=220[duck];"
            "[vo][duck]amix=inputs=2:duration=longest:"
            "dropout_transition=0:normalize=0,"
            "alimiter=limit=0.92:level=0:latency=1,"
            "apad,atrim=duration=10,asetpts=PTS-STARTPTS[a]"
        )
        command += [
            "-filter_complex", filters, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "30", "-frames:v", "300",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", "10.000", "-movflags", "+faststart", str(output),
        ]
        run(command, timeout=360)
        probe = json.loads(run([
            ffprobe, "-v", "error", "-count_frames",
            "-show_streams", "-show_format", "-of", "json", output
        ]).stdout)
        video = next(x for x in probe["streams"] if x["codec_type"] == "video")
        audio = next(x for x in probe["streams"] if x["codec_type"] == "audio")
        if (
            video["codec_name"] != "h264"
            or (video["width"], video["height"]) != (540, 960)
            or int(video["nb_read_frames"]) != 300
            or abs(float(video["duration"]) - 10) > 0.04
            or audio["codec_name"] != "aac"
            or audio["channels"] != 2
            or abs(float(probe["format"]["duration"]) - 10) > 0.08
        ):
            raise RuntimeError("최종 MP4 규격 검증 실패")
        run([ffmpeg, "-v", "error", "-xerror", "-i", output,
             "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"])
        final_pcm = stage / "final_audio_check.wav"
        run([ffmpeg, "-v", "error", "-y", "-i", output,
             "-map", "0:a:0", "-ar", RATE, "-ac", "2",
             "-c:a", "pcm_s16le", final_pcm])
        final_stats = stats(final_pcm)
        if final_stats["rms"] < 0.0001:
            raise RuntimeError("최종 영상 오디오 무음")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        receipt = {
            "success": True, "video": output.name,
            "bytes": output.stat().st_size, "sha256": digest,
            "probe": probe, "final_audio": final_stats,
            "voice_in_mix": True,
            "verification_limit": "성우 입력과 비무음·코덱·전체 디코딩 검증. 음성인식/비전 모델에 의한 의미 검증은 아님.",
        }
        recipe["status"] = "complete"
        write_json(stage / "recipe.json", recipe)
        write_json(stage / "verification_receipt.json", receipt)
        log(f"[완료] {output} / {output.stat().st_size:,} bytes")
        return output
    except Exception as exc:
        recipe["status"] = "failed"
        recipe["error"] = str(exc)
        write_json(stage / "recipe.json", recipe)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="종이컵")
    parser.add_argument("--style", default="반전형")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-brain", action="store_true")
    parser.add_argument("--approved", action="store_true",
                        help="실제 외부 TTS/미디어 실행에 대한 사전 승인")
    parser.add_argument("--output", default="external_kitchen_outputs")
    args = parser.parse_args()
    topic, style = args.topic.strip(), args.style.strip()
    if not topic or len(topic) > 60 or not style or len(style) > 40:
        parser.error("topic은 1~60자, style은 1~40자로 입력하세요.")
    checking = args.dry_run or args.check_brain
    if not checking and not args.approved:
        parser.error("사전 승인 필요: 점검은 --check-brain, 실제 작업은 --approved")
    start = time.perf_counter()
    state = brain_loop(topic, style, lightweight=checking)
    if checking:
        elapsed = time.perf_counter() - start
        log(f"BRAIN_SELF_TEST_PASS / {elapsed:.4f}s / 네트워크·미디어 실행 없음")
        return 0
    render(state, Path(args.output).resolve())
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        raise SystemExit(main())
    except Exception as exc:
        log("[실패] " + str(exc))
        raise SystemExit(1)
'''


WORKFLOW_SOURCE = r'''name: RGON External Brain Kitchen

on:
  workflow_dispatch:
    inputs:
      topic:
        description: "광고 주제"
        required: true
        default: "종이컵"
        type: string
      style:
        description: "광고 스타일"
        required: true
        default: "반전형"
        type: string
      approved:
        description: "이번 외부 TTS·영상 실행을 사전 승인합니다"
        required: true
        default: false
        type: boolean
  schedule:
    - cron: "17 18 * * *"

permissions:
  contents: read

concurrency:
  group: rgon-external-brain-kitchen
  cancel-in-progress: false

jobs:
  kitchen:
    if: >-
      (github.event_name == 'workflow_dispatch' && inputs.approved == true) ||
      (github.event_name == 'schedule' && vars.RGON_SCHEDULE_APPROVED == 'true')
    runs-on: ubuntu-latest
    timeout-minutes: 20
    env:
      PYTHONUTF8: "1"
      PYTHONDONTWRITEBYTECODE: "1"
      PIP_DISABLE_PIP_VERSION_CHECK: "1"
      TOPIC: ${{ inputs.topic || '종이컵' }}
      STYLE: ${{ inputs.style || '반전형' }}

    steps:
      - name: Checkout approved repository files
        uses: actions/checkout@v4
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Check brain before dependency installation
        run: python -B external_kitchen_worker.py --check-brain --topic "$TOPIC" --style "$STYLE"

      - name: Install external media tools and Korean fonts
        run: |
          sudo apt-get update
          sudo apt-get install -y --no-install-recommends ffmpeg fonts-noto-cjk
          python -m pip install "Pillow>=10,<13" "edge-tts>=6,<8"
          if ! python -m pip install "langgraph>=0.2,<2"; then
            echo "::warning::LangGraph installation failed; using bounded state-machine fallback."
          fi

      - name: Execute approved external kitchen
        run: |
          python -B external_kitchen_worker.py \
            --topic "$TOPIC" \
            --style "$STYLE" \
            --approved \
            --output external_kitchen_outputs

      - name: Preserve generated artifacts and failure receipts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: rgon-kitchen-${{ github.run_id }}-${{ github.run_attempt }}
          path: external_kitchen_outputs/
          if-no-files-found: warn
          retention-days: 14

      - name: Write receipt summary
        if: always()
        run: |
          python - <<'PY'
          import json
          import os
          from pathlib import Path
          receipts = sorted(Path("external_kitchen_outputs").glob("*/verification_receipt.json"))
          with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
              handle.write("## RGON External Brain Kitchen\n")
              if not receipts:
                  handle.write("No successful media receipt; inspect logs and failure artifacts.\n")
              for path in receipts:
                  data = json.loads(path.read_text(encoding="utf-8"))
                  handle.write(f"- Verified H.264/AAC / 300 frames / 10 seconds / {data['bytes']:,} bytes\n")
          PY
'''


def say(message: str) -> None:
    print(message, flush=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            prefix=".rgon_", suffix=".tmp", dir=str(path.parent),
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def atomic_json(path: Path, value: dict | list) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_generated(path: Path, content: str) -> None:
    if path.exists():
        old = path.read_text(encoding="utf-8-sig")
        if old == content:
            return
        backups = BRAIN / "generated_file_backups"
        backups.mkdir(parents=True, exist_ok=True)
        suffix = str(time.time_ns())
        atomic_text(backups / f"{path.name}.{suffix}.bak", old)
    atomic_text(path, content)


def read_json_source(relative: str) -> tuple[object | None, dict]:
    path = ROOT / relative
    record = {"path": relative, "exists": path.is_file()}
    if not path.is_file():
        record["status"] = "missing"
        return None, record
    if path.stat().st_size > 8 * 1024 * 1024:
        record["status"] = "skipped_size_limit"
        return None, record
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        record["status"] = "loaded_locally"
        return data, record
    except Exception as exc:
        record["status"] = "invalid_json"
        record["error_type"] = type(exc).__name__
        return None, record


def compact(value, limit: int = 1500) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit - 10] + "…[생략]"


def redact_obvious_secrets(value):
    secret = re.compile(
        r"(password|passwd|secret|api[_-]?key|access[_-]?token|"
        r"refresh[_-]?token|authorization|client[_-]?secret|cookie|credential)",
        re.I,
    )
    if isinstance(value, dict):
        return {
            str(key): ("[REDACTED]" if secret.search(str(key))
                       else redact_obvious_secrets(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_obvious_secrets(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"\bgh[pousr]_[A-Za-z0-9_]+\b", "[REDACTED]", value)
        value = re.sub(r"\bAIza[A-Za-z0-9_-]{20,}\b", "[REDACTED]", value)
        value = re.sub(r"\bsk-[A-Za-z0-9_-]{16,}\b", "[REDACTED]", value)
    return value


def extract_viral_recipes(data) -> list[dict]:
    candidates: list[list] = []

    def visit(node, depth=0):
        if depth > 5:
            return
        if isinstance(node, list):
            if node and all(isinstance(x, (dict, str)) for x in node):
                candidates.append(node)
            for item in node:
                if isinstance(item, (dict, list)):
                    visit(item, depth + 1)
        elif isinstance(node, dict):
            for key in ("recipes", "viral_recipes", "styles", "items", "레시피"):
                if key in node:
                    visit(node[key], depth + 1)
            if node and all(isinstance(x, dict) for x in node.values()):
                candidates.append([
                    {"name": str(key), **value} for key, value in node.items()
                ])
            for key, value in node.items():
                if key not in ("recipes", "viral_recipes", "styles", "items", "레시피"):
                    if isinstance(value, (dict, list)):
                        visit(value, depth + 1)

    visit(data)
    pool = min(candidates, key=lambda x: abs(len(x) - 5)) if candidates else []
    defaults = ("반전형", "공감형", "질문형", "비교형", "스토리형")
    result = []
    for index in range(5):
        if index < len(pool):
            item = redact_obvious_secrets(pool[index])
            if isinstance(item, dict):
                name = next(
                    (str(item[key]) for key in
                     ("style_name", "style", "name", "title", "type", "스타일", "제목")
                     if item.get(key)),
                    f"바이럴 레시피 {index + 1}",
                )
                style = str(item.get("style_name", item.get("style", item.get("스타일", name))))
            else:
                name = f"바이럴 레시피 {index + 1}"
                style = defaults[index]
            result.append({
                "name": name[:100],
                "style": style[:100],
                "summary": compact(item),
                "source": "local_grok_5_viral_recipes.json",
                "status": "원본 로컬 JSON에서 요약",
            })
        else:
            result.append({
                "name": defaults[index] + " / 원본 확인 필요",
                "style": defaults[index],
                "summary": "로컬 폴백 템플릿",
                "source": "explicit_local_fallback",
                "status": "원본 미확보 / 로컬 폴백",
            })
    return result


def make_manifest() -> dict:
    ingredients, ingredients_status = read_json_source("top1_ingredients_basket.json")
    grok, grok_status = read_json_source("ingredients_basket/grok_5_viral_recipes.json")
    evolution, evolution_status = read_json_source("evolution_memory.json")
    del ingredients, evolution

    constitution = [
        {
            "id": "C1", "name": "최우선 목표",
            "text": "소통·연결·만능을 최우선 목표로 삼는다.",
        },
        {
            "id": "C2", "name": "전문 도구 레버리지",
            "text": (
                "직접 어설프게 만들지 않고 각 분야 세계 Top 1 전문 도구"
                "(Claude Opus 5.5, GPT-6.1 Sol, Grok 4.7, Adobe 3대장, "
                "Letta, LangGraph, edge-tts, FFmpeg)를 찾아 최고로 레버리지한다."
            ),
        },
        {
            "id": "C3", "name": "외부 클라우드 우선",
            "text": (
                "무거운 재료 보관과 손질은 노트북이 아닌 외부 클라우드 주방"
                "(Google Sheets + GitHub Actions)에서 처리한다."
            ),
        },
        {
            "id": "C4", "name": "검수·복기·교정",
            "text": (
                "모든 창조물은 사령관께 보고하기 전 스스로 "
                "'기준 확인 -> 기억 조회 -> 창조 -> 실패 검수 및 복기 -> 자동 교정' "
                "루프를 거친다."
            ),
        },
        {
            "id": "C5", "name": "사전 승인",
            "text": "지시서나 코드는 반드시 사령관님의 사전 승인을 받은 후 실행한다.",
        },
    ]

    rules = [
        {
            "id": "R1", "name": "종이컵 머그잔 오생성 복기",
            "failure": "종이컵 주제에 단순 coffee cup을 쓰면 손잡이 달린 도자기 머그컵이 생성됨.",
            "trigger": ["종이컵", "paper cup"],
            "mandatory_prompt": PAPER_CORRECTION,
            "correction": (
                "종이컵 주제에는 mandatory_prompt 전체를 강제 주입한다. "
                "금지어만 추가하는 대신 disposable white paper cup으로 양의 재질 조건도 고정한다."
            ),
        },
        {
            "id": "R2", "name": "영상/음성 분리 실패 복기",
            "failure": "브라우저 TTS와 영상이 분리되어 실제 MP4에 성우가 없던 실패.",
            "correction": (
                "edge-tts (ko-KR-InJoonNeural) + 62BPM ducking BGM + "
                "FFmpeg H.264/AAC 10.000s 완전 합체. "
                "성우 MP3 비무음, 최종 AAC, 300프레임 및 전체 디코딩 검증 필수."
            ),
        },
        {
            "id": "R3", "name": "캐시 및 DOM 증발 복기",
            "failure": "로컬 캐시 및 채팅 DOM 리렌더링으로 UI가 가려지던 실패.",
            "correction": (
                "향후 승인된 UI 작업 시 빌드 쿼리스트링과 document.body 직속 모달 유지. "
                "이번 설치 및 외부 워커는 기존 HTML/대시보드/DOM을 수정하지 않는다."
            ),
        },
    ]

    catalog = [
        {"category": "Memory Top 1", "tool": "Letta Filesystem Memory & Mem0 Architecture",
         "application": "헌법·회상 규칙·구조화 기억의 파일 기반 패키지"},
        {"category": "Reflection/Orchestration Top 1",
         "tool": "LangGraph State-Machine Loop (Plan -> Execute -> Critic -> Reflect -> Retry)",
         "application": "최대 2회 재교정 후 실패 종료; 미설치 시 동일한 제한형 상태 머신"},
        {"category": "Coding/Architecture Top 1", "tool": "Claude Opus 5.5 & GPT-6.1 Sol",
         "application": "사용자 지정 설계·코딩 도구"},
        {"category": "Viral Copy Top 1", "tool": "Grok 4.7 (5 Dopamine Styles)",
         "application": "확보된 로컬 레시피를 기억으로 참조"},
        {"category": "External Cloud Kitchen Top 1",
         "tool": "GitHub Actions Free Runner + Google Sheets Cloud Memory",
         "application": "시트에 구조화 기억, 승인된 Actions에서 외부 미디어 손질"},
    ]

    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "package_name": "RGON external brain and cloud kitchen",
        "core_constitution": constitution,
        "self_reflection_rules": rules,
        "top1_brain_tools_catalog": catalog,
        "viral_recipes": extract_viral_recipes(grok),
        "source_inventory": [ingredients_status, grok_status, evolution_status],
        "memory_architecture": {
            "core_memory": "core_constitution",
            "archival_memory": "self_reflection_rules + viral_recipes",
            "working_memory": "per-run BrainState and recipe.json",
            "filesystem_anchor": "brain_basket/external_brain_manifest.json",
            "cloud_anchor": TAB_TITLE,
        },
        "orchestration": {
            "states": ["Plan", "Execute", "Critic", "Reflect", "Retry"],
            "max_corrections": 2,
            "langgraph_optional": True,
            "fallback": "bounded standard-library state machine",
        },
        "execution_policy": {
            "approval_required": True,
            "actual_worker_flag": "--approved",
            "scheduled_approval_variable": "RGON_SCHEDULE_APPROVED",
            "scheduled_approval_value": "true",
            "ui_changes_allowed": False,
            "upload_credentials_to_github": False,
            "automatic_git_push": False,
        },
        "cloud_kitchen": {
            "sheets": [{"name": name, "id": sid} for name, sid in SPREADSHEETS],
            "tab": TAB_TITLE,
            "runner": "ubuntu-latest",
            "workflow": ".github/workflows/rgon_external_brain_kitchen.yml",
            "worker": "external_kitchen_worker.py",
            "artifact_retention_days": 14,
            "schedule_utc": "17 18 * * *",
            "deployment_status": "files_prepared_not_pushed_or_activated",
        },
    }


def make_rows(manifest: dict) -> list[list[str]]:
    now = manifest["generated_at"]
    rows = [HEADERS[:]]
    location = "Google Sheets 기억 / GitHub Actions 실행"
    for item in manifest["core_constitution"]:
        rows.append([
            "절대 기준", item["name"], "중앙 두뇌 헌법",
            item["text"], location, "적용", now,
        ])

    tools = [
        ("기억", "Letta Filesystem Memory & Mem0 Architecture",
         "파일 기반 헌법·복기 기억 패턴 및 구글 시트 클라우드 영구 해마 연동."),
        ("복기·오케스트레이션", "LangGraph State-Machine Loop",
         "Plan → Execute → Critic → Reflect → Retry. 최대 2회 자동 교정 및 표준 라이브러리 폴백."),
        ("코딩·설계", "Claude Opus 5.5 & GPT-6.1 Sol",
         "세계 1위 정밀 코딩 및 아키텍처 경쟁 입찰 레버리지."),
        ("바이럴 카피", "Grok 4.7 (5 Dopamine Styles)",
         "반전형/감성형/비교형/숫자충격형/ASMR몰입형 5대 도파민 대본 레시피."),
        ("이미지·디자인·음성 정리", "Adobe Firefly / Express / Podcast Enhance + Flux",
         "세계 1위 무료 크리에이티브 도구 직통 및 제품 재질·형태 교정 규칙 적용."),
        ("성우·영상·외부 주방", "edge-tts + FFmpeg + GitHub Actions + Google Sheets",
         "ko-KR-InJoonNeural + 62BPM ducking BGM + 300프레임 H.264/AAC 10초 외부 손질."),
    ]
    for name, tool, text in tools:
        rows.append(["전문 도구", name, tool, text, location, "구성", now])

    for item in manifest["self_reflection_rules"]:
        text = item["failure"] + " → " + item["correction"]
        if item.get("mandatory_prompt"):
            text += " / 강제 주입: " + item["mandatory_prompt"]
        rows.append([
            "실패 복기", item["name"], "Memory + Critic + bounded Retry",
            text, location, "자동 교정 규칙 등록", now,
        ])

    for item in manifest["viral_recipes"]:
        rows.append([
            "바이럴 레시피", item["name"], "Grok 4.7 5대 도파민 레시피",
            item["summary"], location, item["status"], now,
        ])

    if len(rows) != 20 or any(len(row) != 7 for row in rows):
        raise RuntimeError("시트 데이터 규격 오류: 헤더 1행 + 데이터 19행, 7열이어야 합니다.")
    return rows


def ensure_auth_libraries() -> None:
    missing = []
    for module, package in (("google.auth", "google-auth"), ("requests", "requests")):
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(package)
    if not missing:
        return
    say("[인증 준비] 로컬 경량 패키지만 설치: " + ", ".join(missing))
    result = subprocess.run(
        [
            sys.executable, "-m", "pip", "install",
            "--disable-pip-version-check", *missing,
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="replace", timeout=240, shell=False,
    )
    if result.returncode:
        raise RuntimeError(
            "Google 인증 패키지 설치 실패. 직접 google-auth requests를 설치해 주세요.\n"
            + result.stderr[-1500:]
        )
    importlib.invalidate_caches()


def api(session, method: str, url: str, **kwargs) -> dict:
    for attempt in range(5):
        response = session.request(method, url, timeout=60, **kwargs)
        if response.status_code in (429, 500, 502, 503, 504) and attempt < 4:
            time.sleep(min(2 ** attempt, 12))
            continue
        if not response.ok:
            try:
                error = response.json().get("error", {})
                status = error.get("status", "UNKNOWN")
                message = str(error.get("message", ""))[:400]
            except Exception:
                status, message = "UNKNOWN", "응답 내용 생략"
            raise RuntimeError(
                f"Google Sheets API HTTP {response.status_code} / {status}: {message}"
            )
        return response.json() if response.content else {}
    raise RuntimeError("Google Sheets API 재시도 한도 초과")


def connect_sheets():
    ensure_auth_libraries()
    import pickle
    from google.auth.credentials import Credentials
    from google.auth.transport.requests import AuthorizedSession, Request

    errors = []
    unique = []
    for path in TOKEN_CANDIDATES:
        if str(path).lower() not in {str(x).lower() for x in unique}:
            unique.append(path)

    for index, path in enumerate(unique, 1):
        if not path.is_file():
            errors.append(f"토큰 후보 {index}: 파일 없음")
            continue
        session = None
        try:
            with path.open("rb") as handle:
                credentials = pickle.load(handle)
            if not isinstance(credentials, Credentials):
                raise TypeError("지원되는 google-auth Credentials 객체가 아닙니다.")
            if not credentials.valid:
                credentials.refresh(Request())
            session = AuthorizedSession(credentials)
            metadata = {}
            for _, sid in SPREADSHEETS:
                metadata[sid] = api(
                    session, "GET",
                    f"https://sheets.googleapis.com/v4/spreadsheets/{sid}",
                    params={"fields": "spreadsheetId,properties(title),sheets(properties)"},
                )
            say(f"[인증 확인] 토큰 후보 {index}로 Google Sheets 2곳 읽기 성공")
            return session, metadata
        except Exception as exc:
            if session is not None:
                session.close()
            errors.append(
                f"토큰 후보 {index}: {type(exc).__name__}; 접근/만료/권한을 확인하세요."
            )
    raise RuntimeError(
        "두 Google Sheets에 접근 가능한 OAuth 토큰을 찾지 못했습니다.\n"
        + "\n".join(errors)
        + "\n기존 토큰은 수정하지 않았습니다."
    )


def upload_sheet(session, sid: str, metadata: dict, rows: list[list[str]]) -> dict:
    from urllib.parse import quote

    base = f"https://sheets.googleapis.com/v4/spreadsheets/{sid}"
    properties = next(
        (
            sheet["properties"] for sheet in metadata.get("sheets", [])
            if sheet["properties"].get("title") == TAB_TITLE
        ),
        None,
    )
    if properties is None:
        try:
            created = api(
                session, "POST", base + ":batchUpdate",
                json={"requests": [{
                    "addSheet": {"properties": {
                        "title": TAB_TITLE,
                        "gridProperties": {
                            "rowCount": 100, "columnCount": 7,
                            "frozenRowCount": 1,
                        },
                    }},
                }]},
            )
            properties = created["replies"][0]["addSheet"]["properties"]
        except RuntimeError:
            fresh = api(
                session, "GET", base,
                params={"fields": "sheets(properties)"},
            )
            properties = next(
                (
                    sheet["properties"] for sheet in fresh.get("sheets", [])
                    if sheet["properties"].get("title") == TAB_TITLE
                ),
                None,
            )
            if properties is None:
                raise

    sheet_id = properties["sheetId"]
    grid = properties.get("gridProperties", {})
    row_count = max(int(grid.get("rowCount", 100)), len(rows))
    column_count = max(int(grid.get("columnCount", 7)), 7)
    requests = [{
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {
                    "rowCount": row_count, "columnCount": column_count,
                    "frozenRowCount": 1,
                },
            },
            "fields": (
                "gridProperties.rowCount,gridProperties.columnCount,"
                "gridProperties.frozenRowCount"
            ),
        },
    }]
    api(session, "POST", base + ":batchUpdate", json={"requests": requests})

    quoted_tab = "'" + TAB_TITLE.replace("'", "''") + "'"
    all_range = quoted_tab + "!A:G"
    old = api(
        session, "GET", base + "/values/" + quote(all_range, safe=""),
        params={"valueRenderOption": "UNFORMATTED_VALUE"},
    )
    old_length = len(old.get("values", []))
    target = f"{quoted_tab}!A1:G{len(rows)}"
    update = api(
        session, "PUT", base + "/values/" + quote(target, safe=""),
        params={"valueInputOption": "RAW"},
        json={"range": target, "majorDimension": "ROWS", "values": rows},
    )

    if old_length > len(rows):
        tail = f"{quoted_tab}!A{len(rows) + 1}:G{old_length}"
        api(
            session, "POST",
            base + "/values/" + quote(tail, safe="") + ":clear",
            json={},
        )

    api(session, "POST", base + ":batchUpdate", json={"requests": [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0,
                          "endRowIndex": 1, "startColumnIndex": 0,
                          "endColumnIndex": 7},
                "cell": {"userEnteredFormat": {
                    "backgroundColor": {"red": 0.07, "green": 0.20, "blue": 0.20},
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                    },
                }},
                "fields": "userEnteredFormat",
            },
        },
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 1,
                          "endRowIndex": len(rows), "startColumnIndex": 0,
                          "endColumnIndex": 7},
                "cell": {"userEnteredFormat": {
                    "wrapStrategy": "WRAP",
                    "verticalAlignment": "TOP",
                }},
                "fields": "userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment",
            },
        },
        {
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                          "startIndex": 0, "endIndex": 7},
                "properties": {"pixelSize": 190},
                "fields": "pixelSize",
            },
        },
        {
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                          "startIndex": 3, "endIndex": 4},
                "properties": {"pixelSize": 590},
                "fields": "pixelSize",
            },
        },
    ]})

    readback = api(
        session, "GET", base + "/values/" + quote(target, safe=""),
        params={"valueRenderOption": "UNFORMATTED_VALUE"},
    )
    actual = readback.get("values", [])
    if actual != rows:
        raise RuntimeError(f"Google Sheets 업로드 후 재조회 불일치: {sid}")

    return {
        "spreadsheet_id": sid,
        "sheet_id": sheet_id,
        "tab": TAB_TITLE,
        "data_rows": len(rows) - 1,
        "rows_including_header": len(actual),
        "columns": 7,
        "verified_cells": len(rows) * 7,
        "updated_range": update.get("updatedRange", target),
        "verified_range": readback.get("range", target),
        "readback_equal": True,
        "url": f"https://docs.google.com/spreadsheets/d/{sid}/edit#gid={sheet_id}",
        "verified_at": utc_now(),
    }


def self_test(worker_path: Path) -> dict:
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.perf_counter()
    result = subprocess.run(
        [
            sys.executable, "-B", str(worker_path),
            "--check-brain", "--topic", "종이컵", "--style", "반전형",
        ],
        cwd=str(ROOT), env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="replace", timeout=15, shell=False,
    )
    elapsed = time.perf_counter() - start
    say(result.stdout.rstrip())
    if (
        result.returncode != 0
        or "BRAIN_SELF_TEST_PASS" not in result.stdout
        or "no handle, no ceramic mug" not in result.stdout
    ):
        raise RuntimeError("외부 워커 자기검열 셀프 테스트 실패:\n" + result.stderr[-2000:])
    say(f"[셀프 테스트] PASS / 프로세스 시작 포함 {elapsed:.3f}초")
    return {
        "success": True,
        "elapsed_seconds_including_process_start": round(elapsed, 4),
        "under_one_second": elapsed < 1,
        "tested_topic": "종이컵",
        "tested_style": "반전형",
        "paper_cup_correction_verified": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Google Sheets 클라우드 해마와 승인 기반 외부 Actions 주방 파일을 준비합니다."
    )
    parser.add_argument(
        "--approve", action="store_true",
        help="설명된 파일 생성·경량 인증 패키지 설치·Sheets 업로드를 사전 승인",
    )
    args = parser.parse_args()
    if not args.approve:
        say("[중단] --approve 옵션이 필요합니다.")
        return 2

    started = time.monotonic()
    receipt_path = BRAIN / "external_kitchen_setup_receipt.json"
    receipt = {
        "started_at": utc_now(),
        "status": "running",
        "approved": True,
        "ui_modified": False,
        "credentials_exported": False,
        "github_deployment": "not_pushed_or_activated",
        "sheets": [],
    }
    session = None

    try:
        ast.parse(WORKER_SOURCE, filename="external_kitchen_worker.py")
        manifest = make_manifest()
        rows = make_rows(manifest)

        manifest_path = BRAIN / "external_brain_manifest.json"
        worker_path = ROOT / "external_kitchen_worker.py"
        workflow_path = ROOT / ".github" / "workflows" / "rgon_external_brain_kitchen.yml"

        write_generated(
            manifest_path,
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        )
        write_generated(worker_path, WORKER_SOURCE)
        write_generated(workflow_path, WORKFLOW_SOURCE)

        say(f"[1/4] 중앙 두뇌 헌법 생성 확인: {manifest_path}")
        say(f"[2/4] 외부 워커 생성 확인: {worker_path}")
        say(f"      워크플로우 생성 확인: {workflow_path}")

        receipt["self_test"] = self_test(worker_path)
        receipt["generated_files"] = [
            {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size}
            for path in (manifest_path, worker_path, workflow_path)
        ]
        atomic_json(receipt_path, receipt)

        session, metadata = connect_sheets()
        for name, sid in SPREADSHEETS:
            result = upload_sheet(session, sid, metadata[sid], rows)
            result["spreadsheet_name"] = name
            receipt["sheets"].append(result)
            atomic_json(receipt_path, receipt)
            say(f"[3/4] {name}: 실제 업로드 + 재조회 검증 PASS")
            say(
                f"      데이터 {result['data_rows']}행 / "
                f"헤더 포함 {result['rows_including_header']}행 / "
                f"{result['verified_cells']}셀"
            )
            say(f"      범위: {result['verified_range']}")
            say(f"      시트: {result['url']}")

        if len(receipt["sheets"]) != 2 or not all(
            result["readback_equal"] for result in receipt["sheets"]
        ):
            raise RuntimeError("두 Google Sheets의 실업로드 검증이 완료되지 않았습니다.")

        receipt["status"] = "local_package_and_cloud_memory_ready"
        receipt["completed_at"] = utc_now()
        receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
        atomic_json(receipt_path, receipt)

        say(f"[4/4] 검증 영수증: {receipt_path}")
        say("EXTERNAL BRAIN BASKET & CLOUD KITCHEN READY!")
        return 0

    except Exception as exc:
        receipt["status"] = "failed"
        receipt["completed_at"] = utc_now()
        receipt["error"] = {"type": type(exc).__name__, "message": str(exc)}
        try:
            atomic_json(receipt_path, receipt)
        except Exception:
            pass
        say(f"[실패] {type(exc).__name__}: {exc}")
        return 1

    finally:
        if session is not None:
            session.close()


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
