#!/usr/bin/env python3
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



# BEGIN RGON GROK RUNTIME BINDING
_rgon_original_build_recipe = build_recipe

def build_recipe(state):
    result = _rgon_original_build_recipe(state)
    path = ROOT / "brain_basket" / "grok_runtime_binding.json"
    if state.get("style") == "반전형" and path.is_file():
        binding = json.loads(path.read_text(encoding="utf-8"))
        fields = binding.get("fields", {})
        recipe = dict(result["recipe"])
        topic_str = str(state.get("topic", "종이컵"))
        for name in ("hook", "body", "cta", "narration"):
            if isinstance(fields.get(name), str) and fields[name].strip():
                recipe[name] = fields[name].replace("{topic}", topic_str).strip()
        recipe["grok_applied_fields"] = sorted(fields)
        recipe["copy_origin"] = (
            "local_Grok_recipe_structured_fields"
            if fields else "worker_local_style_template"
        )
        result["recipe"] = recipe
        log("[Grok] 반전형 원본 적용 필드: " + (", ".join(sorted(fields)) or "없음: 명시적 로컬 템플릿"))
    return result
# END RGON GROK RUNTIME BINDING

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        raise SystemExit(main())
    except Exception as exc:
        log("[실패] " + str(exc))
        raise SystemExit(1)
