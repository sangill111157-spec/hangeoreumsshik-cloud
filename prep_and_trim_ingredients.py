#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prep_and_trim_ingredients.py

실행:
    python -X utf8 prep_and_trim_ingredients.py
    python -X utf8 prep_and_trim_ingredients.py --topic "주제"

작업 범위:
    이 스크립트가 있는 폴더의 ingredients_basket/ 안에만 결과물을 만듭니다.
    기존 HTML, 대시보드, 원본 이미지와 원본 MP3는 수정하지 않습니다.
"""

from __future__ import annotations

import argparse
import array
import asyncio
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import wave
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASKET = ROOT / "ingredients_basket"

WIDTH = 540
HEIGHT = 960
FPS = 30
DURATION = 10.0
SAMPLE_RATE = 48000
BPM = 62

SCENES = (
    ("scene_0_hook.jpg", 0.0, 3.0),
    ("scene_1_body.jpg", 3.0, 7.0),
    ("scene_2_cta.jpg", 7.0, 10.0),
)

Image = None
ImageDraw = None
ImageFont = None
ImageOps = None


def say(message: str) -> None:
    print(message, flush=True)


def run_command(
    command: list[str],
    *,
    timeout: int = 240,
    check: bool = True,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [str(item) for item in command],
        cwd=str(ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )
    if check and result.returncode != 0:
        details = (result.stderr or result.stdout or "")[-10000:]
        raise RuntimeError(
            f"명령 실행 실패 / 종료 코드 {result.returncode}\n"
            f"{subprocess.list2cmdline(command)}\n{details}"
        )
    return result


def ensure_package(import_name: str, pip_name: str, *, required: bool):
    try:
        return importlib.import_module(import_name)
    except ImportError:
        say(f"[준비] 패키지 설치 시도: {pip_name}")
        try:
            run_command(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    pip_name,
                ],
                timeout=240,
            )
            importlib.invalidate_caches()
            return importlib.import_module(import_name)
        except Exception as exc:
            if required:
                raise RuntimeError(
                    f"{pip_name} 설치에 실패했습니다.\n"
                    f'직접 실행: "{sys.executable}" -m pip install {pip_name}\n'
                    f"{exc}"
                ) from exc
            say(f"[경고] {pip_name} 사용 불가: {exc}")
            return None


def load_pillow() -> None:
    global Image, ImageDraw, ImageFont, ImageOps
    ensure_package("PIL", "Pillow", required=True)
    Image = importlib.import_module("PIL.Image")
    ImageDraw = importlib.import_module("PIL.ImageDraw")
    ImageFont = importlib.import_module("PIL.ImageFont")
    ImageOps = importlib.import_module("PIL.ImageOps")


def find_ffmpeg() -> tuple[str, str | None, str]:
    candidates = [
        ROOT / "ffmpeg-8.0.1-full_build" / "bin" / "ffmpeg.EXE",
        ROOT / "ffmpeg-8.0.1-full_build" / "bin" / "ffmpeg.exe",
        ROOT / "ffmpeg.exe",
        ROOT / "ffmpeg",
    ]

    env_path = os.environ.get("FFMPEG_BINARY")
    if env_path:
        candidates.insert(0, Path(env_path.strip('"')))

    path_ffmpeg = shutil.which("ffmpeg")
    if path_ffmpeg:
        candidates.append(Path(path_ffmpeg))

    try:
        imageio_ffmpeg = importlib.import_module("imageio_ffmpeg")
        candidates.append(Path(imageio_ffmpeg.get_ffmpeg_exe()))
    except Exception:
        pass

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate).lower()
        if key in seen or not candidate.is_file():
            continue
        seen.add(key)
        try:
            result = run_command([str(candidate), "-version"], timeout=20)
            version = result.stdout.splitlines()[0]
        except Exception:
            continue

        sibling = candidate.with_name(
            "ffprobe.exe" if os.name == "nt" else "ffprobe"
        )
        ffprobe = str(sibling) if sibling.is_file() else shutil.which("ffprobe")
        return str(candidate.resolve()), ffprobe, version

    raise FileNotFoundError(
        "FFmpeg를 찾지 못했습니다.\n"
        f"권장 위치: {ROOT / 'ffmpeg-8.0.1-full_build' / 'bin' / 'ffmpeg.EXE'}\n"
        "또는 FFmpeg를 PATH에 등록하거나 imageio-ffmpeg를 설치하세요."
    )


def atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def safe_topic_name(topic: str) -> str:
    text = unicodedata.normalize("NFC", topic)
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", text)
    text = re.sub(r"\s+", "_", text).strip(" ._")[:60]
    if not text:
        text = "주제"
    if text.upper() in {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }:
        text = "_" + text
    return text


def make_recipe(topic: str, image_path: Path) -> dict:
    is_paper_cup = topic.replace(" ", "") == "종이컵"

    if is_paper_cup:
        hook = "평범한 한 잔,\n다르게."
        body = "한 잔의 순간을\n더 근사하게."
        cta = "당신의 한 잔을\n골라보세요."
        narration = (
            "평범한 한 잔도, 다르게. "
            "종이컵 하나로 완성하는 작은 분위기. "
            "당신의 한 잔을 골라보세요."
        )
        labels = [
            "매일의 한 잔에, 새로운 분위기",
            "종이컵으로 연출하는 작은 순간",
            "마음에 드는 한 잔을 만나보세요",
        ]
        subject_en = "an unbranded premium-looking paper cup"
    else:
        hook = "익숙한 순간,\n다르게."
        body = "오늘의 장면을\n더 근사하게."
        cta = "지금,\n만나보세요."
        narration = (
            f"익숙한 순간도, 다르게. "
            f"{topic}. 오늘의 장면을 새롭게. "
            "당신의 일상에서, 지금 만나보세요."
        )
        labels = [
            "익숙한 일상에 새로운 시선",
            f"{topic}, 오늘의 새로운 장면",
            "당신의 취향으로 선택하세요",
        ]
        subject_en = f"an unbranded product representing the concept: {topic}"

    image_prompt = (
        f"Photorealistic commercial product photograph of {subject_en}. "
        "Vertical 9:16 composition, a single clearly defined hero product "
        "positioned around the lower-middle of the frame, generous clean "
        "negative space in the top 30 percent for a Korean headline added later, "
        "warm ivory seamless background, soft natural window light from upper "
        "left, realistic contact shadow, subtle paper and material texture, "
        "restrained editorial styling, refined neutral color palette, "
        "85mm product photography aesthetic, crisp subject details. "
        "No text, no letters, no watermark, no visible brand logo, no people, "
        "no misleading environmental or product-performance badges."
    )
    video_prompt = (
        f"Vertical 9:16 photorealistic commercial shot of {subject_en}, "
        "a stable hero product on a warm ivory tabletop, gentle slow camera "
        "push-in, subtle parallax, soft daylight and realistic shadows, "
        "consistent product shape and materials across frames, premium "
        "minimal editorial product cinematography. Leave the upper area "
        "clear for typography added in editing. No generated text, no logos, "
        "no hands, no sudden cuts, no object morphing. Generate a short "
        "usable clip and trim or extend in editing to fit a 10-second ad."
    )

    warnings = [
        "대본과 프롬프트는 로컬 규칙 기반 템플릿으로 생성됩니다.",
        "광고 제품의 인증, 친환경성, 내열성, 할인, 가격 등 미확인 사실은 주장하지 않습니다.",
        "Adobe 및 Suno 결과물은 자동 생성하거나 다운로드하지 않습니다.",
        "각 서비스의 무료 제공량과 상업적 이용 조건은 계정 및 당시 약관을 확인해야 합니다.",
    ]
    if not is_paper_cup:
        warnings.append(
            "현재 시범 영상은 확보된 종이컵 원본 사진을 계속 사용합니다. "
            "주제가 종이컵이 아니라면 카피와 실제 제품 이미지가 다를 수 있습니다."
        )

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "status": "preparing",
        "generation_method": "deterministic_local_copy_and_prompt_templates",
        "video_spec": {
            "width": WIDTH,
            "height": HEIGHT,
            "aspect_ratio": "9:16",
            "fps": FPS,
            "frames": int(DURATION * FPS),
            "duration_seconds": DURATION,
            "video_codec": "H.264",
            "pixel_format": "yuv420p",
            "audio_codec": "AAC",
            "audio_sample_rate": SAMPLE_RATE,
            "audio_channels": 2,
        },
        "source_image": str(image_path),
        "script": {
            "hook_0_3s": hook,
            "body_3_7s": body,
            "cta_7_10s": cta,
            "narration_10s": narration,
            "voice": "ko-KR-InJoonNeural",
            "voice_direction": (
                "자연스럽고 선명한 한국어 남성 광고 톤. "
                "목소리의 실제 연령을 보장하지 않으며, InJoon 프리셋을 사용합니다."
            ),
            "timing_method": (
                "TTS를 실제 생성하고 디코딩한 길이를 측정한 뒤, "
                "피치를 유지하는 atempo로 9.35초에 맞춥니다. "
                "앞 0.15초와 끝 0.50초를 포함해 총 10초로 정렬합니다."
            ),
        },
        "scenes": [
            {
                "file": SCENES[index][0],
                "start": SCENES[index][1],
                "end": SCENES[index][2],
                "headline": text,
                "subtitle": labels[index],
            }
            for index, text in enumerate((hook, body, cta))
        ],
        "adobe_firefly": {
            "image_prompt_en": image_prompt,
            "video_prompt_en": video_prompt,
            "negative_prompt": (
                "illegible typography, watermarks, brand logos, distorted "
                "product geometry, duplicate products, exaggerated material "
                "properties, plastic-looking paper, oversharpening"
            ),
            "usage": (
                "프롬프트를 Firefly에 직접 입력합니다. 화면비 9:16을 선택하고, "
                "글자는 생성 이미지에 넣지 말고 후편집으로 추가합니다."
            ),
        },
        "adobe_express": {
            "template_search_keywords_ko": [
                "미니멀 제품 광고 세로",
                "감성 제품 릴스",
                "제품 소개 인스타그램 스토리",
            ],
            "template_search_keywords_en": [
                "minimal product vertical ad",
                "editorial product Instagram story",
                "clean product reel",
            ],
            "layout_guide": {
                "canvas": "540 × 960 px / 9:16",
                "headline": "상단 x=40~500, y=130~340. 굵은 한글, 2~3줄 이내.",
                "hero_product": "중앙 제품을 가리지 않도록 텍스트 영역을 분리.",
                "subtitle": "하단 x=32~508, y=710~844. 반투명 박스, 충분한 대비.",
                "progress": "y=876 부근에 3/10, 7/10, 10/10 정적 진행바.",
                "safe_area": (
                    "상하 여백을 확보하되, 게시 플랫폼의 실제 UI 가림은 "
                    "최종 업로드 미리보기에서 다시 확인."
                ),
                "timeline": "Hook 3초 → Body 4초 → CTA 3초",
                "font": "맑은 고딕 Bold 또는 사용 권한이 있는 한글 고딕",
            },
        },
        "adobe_podcast_enhance": {
            "purpose": "성우 원본의 잡음이나 실내 잔향이 있을 때 선택적으로 정리.",
            "workflow": [
                "필요한 경우 원본 성우 파일만 Adobe Podcast Enhance에 업로드.",
                "처리 전후 발음, 치찰음, 숨소리, 음색 변화를 비교.",
                "배경음악이 합쳐진 최종 영상을 음성 정리용으로 처리하지 않기.",
                "개선된 음성을 원본 대신 사용할 경우 길이 정렬과 합성을 다시 실행.",
            ],
            "note": (
                "본 스크립트는 Adobe 계정에 로그인하거나 업로드하지 않습니다. "
                "이미 깨끗한 TTS에는 추가 처리가 불필요할 수 있습니다."
            ),
        },
        "suno_ai": {
            "prompt_en": (
                "Instrumental only, no vocals, no speech. Refined minimalist "
                "commercial music bed for a 10-second vertical product ad about "
                f"{topic}. 62 BPM, warm electric-piano-style major ninth chords, "
                "soft rounded bass, delicate muted bell accents, sparse soft "
                "percussion, clean stereo image, elegant optimistic mood, "
                "plenty of midrange space for a Korean male voiceover. "
                "Immediate gentle opening, a subtle lift near 7 seconds, "
                "a clean soft ending at 10 seconds, no loud riser or crash. "
                "If exact duration is unsupported, generate and edit a "
                "10-second excerpt with short fades."
            ),
            "requested_bpm": BPM,
            "requested_duration_seconds": DURATION,
            "local_fallback": (
                "외부 음악 생성 없이 wave/math 기반의 오리지널 "
                "62BPM 스테레오 PCM 음악을 생성합니다."
            ),
        },
        "warnings": warnings,
    }


def find_korean_font() -> Path:
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates = [
        Path(r"C:\Windows\Fonts\malgunbd.ttf"),
        windir / "Fonts" / "malgunbd.ttf",
        windir / "Fonts" / "malgun.ttf",
        ROOT / "fonts" / "malgunbd.ttf",
        ROOT / "fonts" / "NotoSansKR-Bold.ttf",
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
    ]
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "한글 폰트를 찾지 못했습니다. "
        r"C:\Windows\Fonts\malgunbd.ttf 또는 "
        "fonts/NotoSansKR-Bold.ttf를 준비해 주세요. "
        "한글이 깨지는 기본 폰트로 대체하지 않습니다."
    )


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    output: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for character in paragraph:
            candidate = line + character
            if line and draw.textlength(candidate, font=font) > max_width:
                output.append(line.rstrip())
                line = character.lstrip()
            else:
                line = candidate
        output.append(line.rstrip())
    return output


def fitted_lines(
    draw,
    text: str,
    font_path: Path,
    width: int,
    max_height: int,
    initial_size: int,
    minimum_size: int = 14,
):
    for size in range(initial_size, minimum_size - 1, -1):
        font = ImageFont.truetype(str(font_path), size=size)
        lines = wrap_text(draw, text, font, width)
        line_height = math.ceil(size * 1.35)
        if len(lines) * line_height <= max_height:
            return font, lines, line_height
    raise ValueError(f"텍스트가 지정 영역에 들어가지 않습니다: {text}")


def draw_lines(draw, position, lines, font, line_height, fill) -> None:
    x, y = position
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill, anchor="lt")
        y += line_height


def render_scenes(image_path: Path, recipe: dict, output_dir: Path) -> None:
    font_path = find_korean_font()
    recipe["font_path"] = str(font_path)

    with Image.open(image_path) as original:
        source = ImageOps.exif_transpose(original).convert("RGB")
        source.load()

    base = ImageOps.fit(
        source,
        (WIDTH, HEIGHT),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    ).convert("RGBA")

    for index, scene in enumerate(recipe["scenes"]):
        canvas = base.copy()

        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        for y in range(HEIGHT):
            if y < 400:
                alpha = round(236 * (1.0 - y / 400.0) ** 0.65)
                overlay_draw.line(
                    (0, y, WIDTH, y), fill=(249, 246, 239, alpha)
                )
            elif y > 660:
                alpha = round(80 * ((y - 660) / 300.0))
                overlay_draw.line((0, y, WIDTH, y), fill=(10, 18, 20, alpha))

        canvas = Image.alpha_composite(canvas, overlay)
        draw = ImageDraw.Draw(canvas)
        ink = (24, 37, 37, 255)
        accent = (16, 111, 100, 255)

        small_font = ImageFont.truetype(str(font_path), 15)
        draw.rounded_rectangle(
            (40, 78, 226, 112),
            radius=17,
            fill=(249, 247, 241, 235),
        )
        draw.text(
            (54, 85),
            ["01  MOMENT", "02  DETAILS", "03  YOUR CHOICE"][index],
            font=small_font,
            fill=accent,
            anchor="lt",
        )

        font, lines, line_height = fitted_lines(
            draw, scene["headline"], font_path, 460, 216, 54
        )
        draw_lines(draw, (40, 142), lines, font, line_height, ink)

        panel = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        panel_draw = ImageDraw.Draw(panel)
        panel_draw.rounded_rectangle(
            (32, 710, 508, 844),
            radius=24,
            fill=(15, 26, 29, 222),
            outline=(255, 255, 255, 55),
            width=1,
        )
        canvas = Image.alpha_composite(canvas, panel)
        draw = ImageDraw.Draw(canvas)

        font, lines, line_height = fitted_lines(
            draw, scene["subtitle"], font_path, 424, 76, 26
        )
        text_y = 710 + (134 - len(lines) * line_height) // 2
        draw_lines(
            draw, (58, text_y), lines, font, line_height, (255, 255, 250, 255)
        )

        progress = scene["end"] / DURATION
        draw.rounded_rectangle(
            (40, 876, 500, 883), radius=3, fill=(255, 255, 255, 105)
        )
        draw.rounded_rectangle(
            (40, 876, 40 + round(460 * progress), 883),
            radius=3,
            fill=(138, 228, 204, 255),
        )

        for boundary in (0.3, 0.7):
            x = 40 + round(460 * boundary)
            draw.rectangle((x - 1, 875, x + 1, 884), fill=(20, 32, 33, 200))

        draw.text(
            (40, 901),
            f'{int(scene["start"]):02d}—{int(scene["end"]):02d} SEC',
            font=small_font,
            fill=(255, 255, 250, 240),
            anchor="lt",
        )

        canvas.convert("RGB").save(
            output_dir / scene["file"],
            format="JPEG",
            quality=95,
            subsampling=0,
            optimize=True,
        )


async def save_tts(edge_tts, text: str, destination: Path) -> None:
    communicator = edge_tts.Communicate(
        text=text,
        voice="ko-KR-InJoonNeural",
        rate="+0%",
        pitch="+0Hz",
        volume="+0%",
    )
    await asyncio.wait_for(
        communicator.save(str(destination)),
        timeout=90,
    )


def acquire_voice(recipe: dict, workdir: Path) -> tuple[Path, dict]:
    edge_tts = ensure_package("edge_tts", "edge-tts", required=False)
    tts_path = workdir / "generated_narration.mp3"
    failures: list[str] = []

    if edge_tts is not None:
        for attempt in range(2):
            try:
                if tts_path.exists():
                    tts_path.unlink()
                asyncio.run(
                    save_tts(edge_tts, recipe["script"]["narration_10s"], tts_path)
                )
                if not tts_path.is_file() or tts_path.stat().st_size < 1000:
                    raise RuntimeError("TTS 결과가 비어 있거나 지나치게 작습니다.")
                return tts_path, {
                    "source": "edge-tts",
                    "voice": "ko-KR-InJoonNeural",
                    "matches_requested_script": True,
                    "source_path": str(tts_path),
                    "errors": failures,
                }
            except Exception as exc:
                failures.append(f"{type(exc).__name__}: {exc}")
                say(f"[경고] TTS 시도 {attempt + 1}/2 실패: {exc}")
                if attempt == 0:
                    time.sleep(1)

    fallback = BASKET / "sample_voice_injoon.mp3"
    if not fallback.is_file():
        raise RuntimeError(
            "새 TTS 생성에 실패했고 sample_voice_injoon.mp3도 없습니다.\n"
            + "\n".join(failures)
        )

    warning = (
        "새 TTS 생성 실패: 확보된 sample_voice_injoon.mp3를 사용합니다. "
        "실제 음성이 요청한 대본과 일치하는지는 확인되지 않았습니다."
    )
    say(f"[경고] {warning}")
    recipe["warnings"].append(warning)
    return fallback, {
        "source": "existing_sample_fallback",
        "source_path": str(fallback),
        "matches_requested_script": False,
        "errors": failures,
    }


def wav_stats(path: Path) -> dict:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        rate = handle.getframerate()
        count = handle.getnframes()
        width = handle.getsampwidth()
        if width != 2:
            raise ValueError("검사용 WAV는 PCM 16-bit 형식이어야 합니다.")
        samples = array.array("h", handle.readframes(count))

    if sys.byteorder != "little":
        samples.byteswap()
    if not samples:
        raise RuntimeError(f"오디오 샘플이 없습니다: {path.name}")

    peak = max(abs(value) for value in samples) / 32768.0
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    rms /= 32768.0

    return {
        "duration_seconds": count / rate,
        "sample_rate": rate,
        "channels": channels,
        "frames": count,
        "peak": round(peak, 6),
        "rms": round(rms, 6),
        "rms_dbfs": round(20 * math.log10(max(rms, 1e-12)), 2),
    }


def atempo_filter(factor: float) -> str:
    if factor <= 0:
        raise ValueError("atempo 배율은 양수여야 합니다.")
    pieces: list[str] = []
    while factor > 2.0:
        pieces.append("atempo=2.0")
        factor /= 2.0
    while factor < 0.5:
        pieces.append("atempo=0.5")
        factor /= 0.5
    pieces.append(f"atempo={factor:.10f}")
    return ",".join(pieces)


def trim_voice(
    ffmpeg: str,
    source: Path,
    workdir: Path,
    recipe: dict,
    provenance: dict,
) -> Path:
    decoded = workdir / "voice_decoded.wav"
    run_command(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source), "-map", "0:a:0", "-vn",
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-c:a", "pcm_s16le", str(decoded),
        ]
    )
    source_stats = wav_stats(decoded)
    if source_stats["duration_seconds"] < 0.25 or source_stats["rms"] < 0.0001:
        raise RuntimeError("성우 원본이 지나치게 짧거나 사실상 무음입니다.")

    target_speech_duration = 9.35
    tempo = source_stats["duration_seconds"] / target_speech_duration
    if not 0.65 <= tempo <= 1.65:
        warning = (
            f"성우 길이 보정 배율이 {tempo:.3f}입니다. "
            "10초 규격에는 맞추지만 발화 자연스러움을 직접 확인하세요."
        )
        recipe["warnings"].append(warning)
        say(f"[경고] {warning}")

    aligned = workdir / "voice_aligned_10s.wav"
    filters = (
        f"{atempo_filter(tempo)},"
        f"apad,atrim=duration={target_speech_duration:.6f},"
        "asetpts=PTS-STARTPTS,"
        "loudnorm=I=-16:TP=-1.5:LRA=7,"
        f"aresample={SAMPLE_RATE},"
        f"apad,atrim=duration={target_speech_duration:.6f},"
        "afade=t=in:st=0:d=0.025,"
        "afade=t=out:st=9.27:d=0.08,"
        "adelay=150:all=1,"
        f"apad,atrim=duration={DURATION:.6f},asetpts=PTS-STARTPTS"
    )
    run_command(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(decoded),
            "-af", filters,
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-c:a", "pcm_s16le", str(aligned),
        ]
    )

    with wave.open(str(aligned), "rb") as r:
        params = r.getparams()
        raw_frames = r.readframes(r.getnframes())
    target_frames = round(DURATION * SAMPLE_RATE)
    frame_bytes = params.sampwidth * params.nchannels
    current_frames = len(raw_frames) // frame_bytes
    if current_frames < target_frames:
        raw_frames += b"\x00" * ((target_frames - current_frames) * frame_bytes)
    elif current_frames > target_frames:
        raw_frames = raw_frames[: target_frames * frame_bytes]
    with wave.open(str(aligned), "wb") as w:
        w.setparams(params)
        w.writeframes(raw_frames)

    aligned_stats = wav_stats(aligned)
    if abs(aligned_stats["duration_seconds"] - DURATION) > 1 / SAMPLE_RATE:
        raise RuntimeError("성우 PCM 길이를 정확히 10초로 정렬하지 못했습니다.")
    if aligned_stats["rms"] < 0.0001:
        raise RuntimeError("길이 보정된 성우 오디오가 무음입니다.")

    output = workdir / "trimmed_voice_10s.mp3"
    run_command(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(aligned),
            "-map_metadata", "-1",
            "-c:a", "libmp3lame", "-b:a", "192k",
            "-ar", str(SAMPLE_RATE), "-ac", "1",
            "-write_xing", "1",
            str(output),
        ]
    )

    decoded_mp3 = workdir / "voice_mp3_check.wav"
    run_command(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(output), "-map", "0:a:0",
            "-ac", "1", "-ar", str(SAMPLE_RATE),
            "-c:a", "pcm_s16le", str(decoded_mp3),
        ]
    )
    mp3_stats = wav_stats(decoded_mp3)
    if mp3_stats["rms"] < 0.0001:
        raise RuntimeError("생성된 성우 MP3를 다시 읽었더니 무음입니다.")

    provenance.update(
        {
            "source_decoded_stats": source_stats,
            "tempo_factor": round(tempo, 6),
            "speech_target_seconds": target_speech_duration,
            "leading_silence_seconds": 0.15,
            "aligned_pcm_stats": aligned_stats,
            "mp3_decoded_stats": mp3_stats,
            "output_file": output.name,
        }
    )
    recipe["voice_processing"] = provenance
    return output


def midi_hz(note: int) -> float:
    return 440.0 * 2.0 ** ((note - 69) / 12.0)


def make_bgm(output: Path) -> dict:
    rate = SAMPLE_RATE
    sample_count = round(DURATION * rate)
    beat_seconds = 60.0 / BPM
    bar_seconds = 4.0 * beat_seconds
    tau = 2.0 * math.pi

    chords = [
        ([62, 66, 69, 73, 76], 38),
        ([59, 62, 66, 69, 73], 35),
        ([55, 59, 62, 66, 69], 31),
    ]

    frequencies = [
        ([midi_hz(note) for note in notes], midi_hz(bass))
        for notes, bass in chords
    ]
    pans = [0.18, 0.78, 0.35, 0.86, 0.50]
    left_gains = [math.cos(pan * math.pi / 2.0) for pan in pans]
    right_gains = [math.sin(pan * math.pi / 2.0) for pan in pans]

    noise_state = 0x13579B
    floats = array.array("f")
    peak = 0.0

    for index in range(sample_count):
        t = index / rate
        left = 0.0
        right = 0.0

        for chord_index, (tones, bass_frequency) in enumerate(frequencies):
            local_t = t - chord_index * bar_seconds
            if local_t < 0 or local_t > bar_seconds + 0.65:
                continue

            attack = 1.0 - math.exp(-local_t / 0.07)
            release = (
                1.0
                if local_t <= bar_seconds
                else math.exp(-(local_t - bar_seconds) / 0.16)
            )
            sustain = 0.73 + 0.27 * math.exp(-local_t / 1.9)
            envelope = attack * release * sustain

            for voice_index, frequency in enumerate(tones):
                detune = 1.0006 if voice_index % 2 else 0.9994
                tone = (
                    math.sin(tau * frequency * local_t)
                    + 0.16
                    * math.sin(tau * frequency * 2.0 * local_t + 0.2)
                )
                tone *= 0.058 * envelope
                left += tone * left_gains[voice_index]
                right += tone * right_gains[voice_index] * detune

            bass = (
                math.sin(tau * bass_frequency * local_t)
                * 0.095 * envelope
            )
            left += bass * 0.707
            right += bass * 0.707

        beat_number = int(t / beat_seconds)
        beat_t = t - beat_number * beat_seconds

        if beat_number % 2 == 0:
            phase = tau * (
                43.0 * beat_t
                + 26.0 * 0.025 * (1.0 - math.exp(-beat_t / 0.025))
            )
            pulse = 0.070 * math.exp(-beat_t / 0.085) * math.sin(phase)
            left += pulse
            right += pulse

        half_beat = beat_seconds / 2.0
        half_t = t % half_beat
        noise_state = (1664525 * noise_state + 1013904223) & 0xFFFFFFFF
        noise = noise_state / 2147483648.0 - 1.0
        shaker = noise * 0.007 * math.exp(-half_t / 0.025)
        left += shaker * 0.45
        right += shaker * 0.70

        if beat_number % 2 == 1:
            bell_frequency = midi_hz([81, 78, 76, 78][(beat_number // 2) % 4])
            bell = (
                0.023
                * math.exp(-beat_t / 0.25)
                * (1.0 - math.exp(-beat_t / 0.006))
                * math.sin(tau * bell_frequency * beat_t)
            )
            left += bell * 0.40
            right += bell * 0.75

        fade_in = min(1.0, t / 0.18)
        fade_out = min(1.0, max(0.0, (DURATION - t) / 0.70))
        envelope = (
            math.sin(fade_in * math.pi / 2.0) ** 2
            * math.sin(fade_out * math.pi / 2.0) ** 2
        )
        left *= envelope
        right *= envelope

        floats.append(left)
        floats.append(right)
        peak = max(peak, abs(left), abs(right))

    if peak <= 0:
        raise RuntimeError("BGM 합성 결과가 무음입니다.")

    gain = 0.66 / peak
    pcm = array.array(
        "h",
        (
            max(-32768, min(32767, round(value * gain * 32767)))
            for value in floats
        ),
    )
    if sys.byteorder != "little":
        pcm.byteswap()

    with wave.open(str(output), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm.tobytes())

    stats = wav_stats(output)
    if stats["frames"] != sample_count or stats["channels"] != 2:
        raise RuntimeError("BGM WAV 규격 검증 실패.")
    stats.update(
        {
            "bpm": BPM,
            "bit_depth": 16,
            "composition": "original mathematical synthesis",
            "beat_interval_seconds": beat_seconds,
        }
    )
    return stats


def compose_video(
    ffmpeg: str,
    workdir: Path,
    voice: Path,
    bgm: Path,
) -> Path:
    output = workdir / "trimmed_ad_paper_cup_10s.mp4"

    command = [
        ffmpeg, "-hide_banner", "-loglevel", "warning", "-y",
        "-loop", "1", "-framerate", str(FPS),
        "-t", "3", "-i", str(workdir / SCENES[0][0]),
        "-loop", "1", "-framerate", str(FPS),
        "-t", "4", "-i", str(workdir / SCENES[1][0]),
        "-loop", "1", "-framerate", str(FPS),
        "-t", "3", "-i", str(workdir / SCENES[2][0]),
        "-i", str(voice),
        "-i", str(bgm),
    ]

    filter_graph = (
        "[0:v]trim=duration=3,setpts=PTS-STARTPTS,setsar=1[v0];"
        "[1:v]trim=duration=4,setpts=PTS-STARTPTS,setsar=1[v1];"
        "[2:v]trim=duration=3,setpts=PTS-STARTPTS,setsar=1[v2];"
        "[v0][v1][v2]concat=n=3:v=1:a=0,"
        "fps=30,trim=duration=10,setpts=PTS-STARTPTS,"
        "format=yuv420p[v];"
        "[3:a]aresample=48000,"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "apad,atrim=duration=10,asetpts=PTS-STARTPTS,"
        "volume=1.0,asplit=2[voice][detector];"
        "[4:a]aresample=48000,"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "apad,atrim=duration=10,asetpts=PTS-STARTPTS,"
        "volume=0.23[music];"
        "[music][detector]sidechaincompress="
        "threshold=0.025:ratio=4:attack=15:release=220[ducked];"
        "[voice][ducked]amix=inputs=2:duration=longest:"
        "dropout_transition=0:normalize=0,"
        "alimiter=limit=0.92:attack=5:release=70:level=0:latency=1,"
        "apad,atrim=duration=10,asetpts=PTS-STARTPTS[a]"
    )

    command += [
        "-filter_complex", filter_graph,
        "-map", "[v]", "-map", "[a]",
        "-map_metadata", "-1",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-frames:v", str(round(DURATION * FPS)),
        "-c:a", "aac", "-b:a", "192k",
        "-ar", str(SAMPLE_RATE), "-ac", "2",
        "-t", "10.000",
        "-movflags", "+faststart",
        "-metadata", "title=Prep & Trim 10-second product ad",
        str(output),
    ]
    run_command(command, timeout=360)

    if not output.is_file() or output.stat().st_size < 20000:
        raise RuntimeError("최종 MP4가 생성되지 않았거나 파일이 비정상적으로 작습니다.")

    return output


def verify_video(
    ffmpeg: str,
    ffprobe: str | None,
    video: Path,
    workdir: Path,
) -> dict:
    result: dict = {
        "file": video.name,
        "bytes": video.stat().st_size,
        "expected_duration_seconds": DURATION,
        "expected_video_frames": int(DURATION * FPS),
    }

    decode = run_command(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-xerror",
            "-i", str(video),
            "-map", "0:v:0", "-map", "0:a:0",
            "-progress", "pipe:1", "-nostats",
            "-f", "null", "-",
        ],
        timeout=240,
    )
    progress: dict[str, str] = {}
    for line in decode.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            progress[key] = value
    decoded_frames = int(progress.get("frame", "0").strip())
    if decoded_frames != round(DURATION * FPS):
        raise RuntimeError(
            f"실제 디코딩 프레임 수 불일치: {decoded_frames} / 300"
        )
    result["decoded_video_frames"] = decoded_frames
    result["full_decode_passed"] = True

    if ffprobe:
        probe = run_command(
            [
                ffprobe, "-v", "error",
                "-show_entries",
                "format=duration,size:"
                "stream=index,codec_type,codec_name,width,height,"
                "avg_frame_rate,duration,sample_rate,channels,nb_frames",
                "-of", "json", str(video),
            ],
            timeout=60,
        )
        metadata = json.loads(probe.stdout)
        videos = [
            item for item in metadata.get("streams", [])
            if item.get("codec_type") == "video"
        ]
        audios = [
            item for item in metadata.get("streams", [])
            if item.get("codec_type") == "audio"
        ]
        if len(videos) != 1 or len(audios) != 1:
            raise RuntimeError("최종 MP4의 영상/오디오 스트림 구성이 잘못되었습니다.")

        video_stream, audio_stream = videos[0], audios[0]
        if (
            video_stream.get("codec_name") != "h264"
            or video_stream.get("width") != WIDTH
            or video_stream.get("height") != HEIGHT
        ):
            raise RuntimeError("최종 MP4의 코덱 또는 해상도가 규격과 다릅니다.")

        if (
            audio_stream.get("codec_name") != "aac"
            or int(audio_stream.get("channels", 0)) != 2
            or int(audio_stream.get("sample_rate", 0)) != SAMPLE_RATE
        ):
            raise RuntimeError("최종 MP4 오디오가 AAC / 48kHz / stereo가 아닙니다.")

        video_duration = float(video_stream.get("duration", DURATION))
        container_duration = float(metadata["format"]["duration"])
        if abs(video_duration - DURATION) > 0.04:
            raise RuntimeError(f"영상 트랙 길이 오류: {video_duration}초")
        if abs(container_duration - DURATION) > 0.08:
            raise RuntimeError(f"MP4 컨테이너 길이 오류: {container_duration}초")

        result["probe"] = metadata
        result["duration_seconds"] = container_duration
    else:
        inspection = run_command(
            [ffmpeg, "-hide_banner", "-i", str(video)],
            timeout=30,
            check=False,
        )
        header = inspection.stderr
        duration_match = re.search(
            r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", header
        )
        if not duration_match:
            raise RuntimeError("최종 MP4 길이를 확인하지 못했습니다.")
        hours, minutes, seconds = duration_match.groups()
        seconds_total = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

        if abs(seconds_total - DURATION) > 0.08:
            raise RuntimeError(f"MP4 길이 오류: {seconds_total}초")
        if not re.search(r"Video:\s*h264\b", header):
            raise RuntimeError("H.264 영상 스트림을 확인하지 못했습니다.")
        if not re.search(r"Audio:\s*aac\b", header):
            raise RuntimeError("AAC 오디오 스트림을 확인하지 못했습니다.")
        if not re.search(r"\b540x960\b", header):
            raise RuntimeError("540×960 영상 해상도를 확인하지 못했습니다.")

        result["duration_seconds"] = seconds_total
        result["probe_method"] = "ffmpeg_header_and_full_decode"

    audio_check = workdir / "final_audio_check.wav"
    run_command(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(video), "-map", "0:a:0", "-vn",
            "-ac", "2", "-ar", str(SAMPLE_RATE),
            "-c:a", "pcm_s16le", str(audio_check),
        ]
    )
    audio_stats = wav_stats(audio_check)
    if audio_stats["rms"] < 0.0001:
        raise RuntimeError("최종 MP4의 오디오 트랙이 사실상 무음입니다.")
    result["final_audio_stats"] = audio_stats
    result["voice_inclusion_verification"] = (
        "성우 MP3의 비무음을 별도 검증하고, 그 파일을 직접 amix 입력으로 "
        "매핑하여 인코딩했습니다. 최종 AAC도 비무음 및 전체 디코딩 검사를 "
        "통과했습니다. 음성 인식에 의한 대본 내용 검증은 수행하지 않습니다."
    )
    result["success"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="장바구니 식재료를 손질하고 성우가 포함된 10초 세로 광고를 생성합니다."
    )
    parser.add_argument("--topic", default="종이컵", help='광고 주제. 기본값: "종이컵"')
    args = parser.parse_args()

    topic = re.sub(r"\s+", " ", args.topic).strip()
    if not topic:
        parser.error("--topic은 빈 문자열일 수 없습니다.")
    if len(topic) > 60:
        parser.error("--topic은 가독성과 자연스러운 10초 발화를 위해 60자 이내로 입력하세요.")

    BASKET.mkdir(parents=True, exist_ok=True)
    recipe_path = BASKET / f"trimmed_recipe_{safe_topic_name(topic)}.json"
    image_path = BASKET / "sample_paper_cup.jpg"
    recipe: dict | None = None
    started = time.monotonic()

    try:
        if not image_path.is_file():
            raise FileNotFoundError(f"실사 원본 이미지가 없습니다: {image_path}")

        say(f"[시작] 주제: {topic}")
        say(f"[작업 폴더] {BASKET}")
        say("[안내] 기존 HTML/대시보드와 원본 식재료는 수정하지 않습니다.")

        recipe = make_recipe(topic, image_path)
        atomic_json(recipe_path, recipe)
        say(f"[1/6] 광고 대본·Adobe·Suno 레시피 생성: {recipe_path.name}")

        ffmpeg, ffprobe, ffmpeg_version = find_ffmpeg()
        recipe["ffmpeg"] = {
            "path": ffmpeg,
            "ffprobe_path": ffprobe,
            "version": ffmpeg_version,
        }
        say(f"[FFmpeg] {ffmpeg_version}")
        if "ffmpeg version 8.0.1" not in ffmpeg_version.lower():
            say("[안내] 8.0.1이 아닌 사용 가능한 FFmpeg 빌드로 진행합니다.")

        load_pillow()

        with tempfile.TemporaryDirectory(
            prefix=".prep_trim_",
            dir=str(BASKET),
        ) as temp:
            workdir = Path(temp)

            say("[2/6] 540×960 한글 타이포그래피 씬 3장 렌더링")
            render_scenes(image_path, recipe, workdir)

            say("[3/6] InJoon 성우 생성·실측·10초 길이 정렬")
            voice_source, provenance = acquire_voice(recipe, workdir)
            voice = trim_voice(
                ffmpeg, voice_source, workdir, recipe, provenance
            )

            say("[4/6] 62BPM / 48kHz / 16-bit / 스테레오 BGM 합성")
            bgm = workdir / "trimmed_bgm_10s.wav"
            recipe["bgm_processing"] = make_bgm(bgm)

            say("[5/6] 씬 + 실제 성우 MP3 + 덕킹 BGM → H.264/AAC MP4 합성")
            video = compose_video(ffmpeg, workdir, voice, bgm)

            say("[6/6] 300프레임·10초·코덱·오디오·전체 디코딩 검증")
            verification = verify_video(ffmpeg, ffprobe, video, workdir)

            filenames = [
                *(scene[0] for scene in SCENES),
                voice.name,
                bgm.name,
                video.name,
            ]
            artifacts = []
            for filename in filenames:
                source = workdir / filename
                destination = BASKET / filename
                os.replace(source, destination)
                artifacts.append(
                    {
                        "file": filename,
                        "path": str(destination),
                        "bytes": destination.stat().st_size,
                    }
                )

            recipe["artifacts"] = artifacts
            recipe["verification"] = verification

        recipe["status"] = "complete"
        recipe["elapsed_seconds"] = round(time.monotonic() - started, 2)
        atomic_json(recipe_path, recipe)

        final_video = BASKET / "trimmed_ad_paper_cup_10s.mp4"
        size = final_video.stat().st_size
        say("")
        say("=" * 64)
        say("[성공] 성우 음성이 포함된 10초 광고 MP4를 생성했습니다.")
        say(f"영상: {final_video}")
        say(f"용량: {size:,} bytes ({size / (1024 * 1024):.2f} MiB)")
        say(
            f"규격: {WIDTH}×{HEIGHT} / {FPS}fps / 300프레임 / "
            f"{recipe['verification']['duration_seconds']:.3f}초 / H.264 + AAC"
        )
        say(f"레시피: {recipe_path}")
        say(f"소요 시간: {recipe['elapsed_seconds']:.2f}초")
        if not recipe["voice_processing"]["matches_requested_script"]:
            say("[주의] 새 대본 TTS 대신 확보된 원본 성우 MP3를 사용했습니다.")
        if topic.replace(" ", "") != "종이컵":
            say("[주의] 카피는 새 주제이지만 시범 영상의 실사 원본은 종이컵입니다.")
        say("=" * 64)
        return 0

    except KeyboardInterrupt:
        say("\n[중단] 사용자 요청으로 실행을 중단했습니다.")
        if recipe is not None:
            recipe["status"] = "interrupted"
            recipe["elapsed_seconds"] = round(time.monotonic() - started, 2)
            try:
                atomic_json(recipe_path, recipe)
            except Exception:
                pass
        return 130

    except Exception as exc:
        say(f"\n[실패] {type(exc).__name__}: {exc}")
        if recipe is not None:
            recipe["status"] = "failed"
            recipe["error"] = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            recipe["elapsed_seconds"] = round(time.monotonic() - started, 2)
            try:
                atomic_json(recipe_path, recipe)
            except Exception as write_error:
                say(f"[경고] 실패 상태 기록도 저장하지 못했습니다: {write_error}")
        say("이번 실행의 성공 여부는 레시피 JSON의 status와 verification을 확인하세요.")
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
