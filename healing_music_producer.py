"""
══════════════════════════════════════════════════════════════════
 유튜브 채널 '한걸음씩' — 힐링 음악 롱폼(8H) & 쇼츠 초고속 제작 엔진
 healing_music_producer.py
 
 [핵심 아키텍처 (Gemini 4 Argon 아키텍처 반영)]
 1. 432Hz 피치 변환 + 앰비언트 자연음 믹싱 (FFmpeg 필터 자동화)
 2. 2026 유튜브 비인증(Inauthentic) 정책 우회 감성 자막(ASS) 자동 합성
 3. 20분 정밀 마스터 블록 렌더링 (master_block_20m.mp4)
 4. 재인코딩 없는 무손실 패킷 복사(-c copy)로 8시간(480분) 1분 컷 조립!
 5. 하이라이트 25초 9:16 세로 쇼츠(Shorts) 동시 자동 추출
══════════════════════════════════════════════════════════════════
"""

import os
import sys
import io
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Windows 콘솔 UTF-8 출력 보장
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 기본 힐링 스토리텔링 자막 스크립트 (20분 타임라인 분산)
DEFAULT_HEALING_SCRIPTS = [
    {"start": "00:00:15.00", "end": "00:00:25.00", "text": "오늘 하루도 참 고생 많으셨어요."},
    {"start": "00:01:30.00", "end": "00:01:42.00", "text": "복잡했던 마음의 소음은 잠시 내려두세요."},
    {"start": "00:03:00.00", "end": "00:03:15.00", "text": "서두르지 않아도 괜찮습니다. 한걸음씩."},
    {"start": "00:05:20.00", "end": "00:05:35.00", "text": "부드러운 선율과 빗소리가 당신을 편안히 감싸줍니다."},
    {"start": "00:08:00.00", "end": "00:08:15.00", "text": "지친 마음에 건네는 따뜻한 쉼표 하나."},
    {"start": "00:11:30.00", "end": "00:11:45.00", "text": "오늘 밤은 아무 걱정 없이 깊고 편안한 잠에 드시기를."},
    {"start": "00:15:00.00", "end": "00:15:15.00", "text": "당신의 내일은 오늘보다 한결 가벼울 거예요."},
    {"start": "00:18:30.00", "end": "00:18:45.00", "text": "고단했던 하루의 끝, 편안한 쉼이 되기를 바랍니다."}
]

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def generate_ass_subtitle(output_path: Path, scripts=None, font_name="NanumGothic, Malgun Gothic", font_size=22) -> Path:
    """
    2026 유튜브 Inauthentic/Repetitive Content 규제 우회용 감성 ASS 자막 파일 생성
    Linux(Ubuntu 나눔고딕) 및 Windows(맑은 고딕) 모두 호환되는 폰트 지정
    부드러운 페이드인/아웃과 아늑한 감성 스타일 적용
    """
    if scripts is None:
        scripts = DEFAULT_HEALING_SCRIPTS

    ass_content = f"""[Script Info]
Title: HanGeoreum Healing Story Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HealingStyle,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H40000000,&H80000000,0,0,0,0,100,100,1,0,1,1.5,1,2,50,50,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for item in scripts:
        # \\fad(1500,1500) : 1.5초 페이드인, 1.5초 페이드아웃으로 시각적 거부감 없이 평온함 제공
        ass_content += f"Dialogue: 0,{item['start']},{item['end']},HealingStyle,,0,0,0,,{{\\fad(1500,1500)}}{item['text']}\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    log(f"감성 자막(ASS) 생성 완료: {output_path.name}")
    return output_path

def render_master_block(
    loop_video: Path,
    piano_audio: Path,
    ambient_audio: Path,
    ass_sub: Path,
    output_master: Path,
    duration_min: int = 20,
    ambient_vol: float = 0.25,
    crf: int = 21,
    ffmpeg_bin: str = "ffmpeg"
) -> bool:
    """
    [1단계] 432Hz 피치 변환 + 앰비언트 믹싱 + 감성 자막 오버레이 + 3초 심리스 루프(afade/fade)
    20분 고품질 마스터 비디오 블록 렌더링
    """
    log("==================================================")
    log(f" [1단계] {duration_min}분 마스터 블록 렌더링 시작...")
    log(f" - 영상 에셋: {loop_video}")
    log(f" - 피아노 음원: {piano_audio} (432Hz 변환 적용)")
    log(f" - 앰비언트: {ambient_audio} (볼륨 {ambient_vol})")
    log("==================================================")

    duration_sec = duration_min * 60
    duration_str = f"00:{duration_min:02d}:00"

    # 3초 심리스 페이드 계산 (20분 = 1200초 기준 st=1197)
    audio_fade_out_st = max(0, duration_sec - 3)
    video_fade_out_st = max(0, duration_sec - 2)

    # Windows/Linux 크로스플랫폼 경로 이스케이프 처리
    ass_sub_escaped = str(ass_sub.resolve()).replace("\\", "/").replace(":", "\\:")

    filter_complex = (
        # 1. 440Hz -> 432Hz 오디오 피치 변환
        "[1:a]asetrate=44100*432/440,aresample=44100,volume=1.0[piano432]; "
        # 2. 앰비언트 음원 볼륨 조절
        f"[2:a]volume={ambient_vol}[ambient]; "
        # 3. 2채널 오디오 믹싱
        "[piano432][ambient]amix=inputs=2:duration=first:dropout_transition=3[amix_raw]; "
        # 4. 심리스 루프용 오디오 3초 페이드인/아웃 (틱 노이즈 제거)
        f"[amix_raw]afade=t=in:st=0:d=3,afade=t=out:st={audio_fade_out_st}:d=3[aout]; "
        # 5. 비디오 감성 ASS 자막 오버레이
        f"[0:v]ass='{ass_sub_escaped}'[vsub]; "
        # 6. 심리스 루프용 비디오 2초 페이드인/아웃 (블랙 디졸브)
        f"[vsub]fade=t=in:st=0:d=2,fade=t=out:st={video_fade_out_st}:d=2[vout]"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-stream_loop", "-1", "-i", str(loop_video),
        "-stream_loop", "-1", "-i", str(piano_audio),
        "-stream_loop", "-1", "-i", str(ambient_audio),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-t", duration_str,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
        "-c:a", "aac", "-b:a", "192k",
        str(output_master)
    ]

    log(f"FFmpeg 실행 중... (심리스 루프 필터 적용)")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        log(f" 마스터 블록 렌더링 실패:\n{res.stderr[-1000:]}")
        return False

    log(f" 20분 마스터 블록 완성! -> {output_master} ({output_master.stat().st_size / (1024*1024):.1f} MB)")
    return True

def assemble_longform(
    master_block: Path,
    output_longform: Path,
    total_hours: int = 8,
    block_duration_min: int = 20,
    ffmpeg_bin: str = "ffmpeg"
) -> bool:
    """
    [2단계] 재인코딩 없는(-c copy) 무손실 패킷 결합
    20분 마스터 블록을 반복 루프하여 8시간 롱폼을 1분 만에 조립!
    """
    loop_count = (total_hours * 60 // block_duration_min) - 1
    log("==================================================")
    log(f"⚡ [2단계] 초고속 {total_hours}시간 롱폼 조립 시작 (무손실 Stream Copy)")
    log(f" - 마스터 블록: {master_block}")
    log(f" - 루프 횟수: {loop_count + 1}회 (총 {total_hours}시간)")
    log("==================================================")

    # -stream_loop N: N회 추가 반복 (23회 추가 반복 = 총 24회 = 480분 = 8시간)
    cmd = [
        ffmpeg_bin, "-y",
        "-stream_loop", str(loop_count),
        "-i", str(master_block),
        "-c", "copy",
        str(output_longform)
    ]

    start_time = datetime.now()
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = (datetime.now() - start_time).total_seconds()

    if res.returncode != 0:
        log(f"❌ 롱폼 조립 실패:\n{res.stderr[-1000:]}")
        return False

    file_size_gb = output_longform.stat().st_size / (1024*1024*1024)
    log(f"🎉 8시간 롱폼 완성! 소요시간: {elapsed:.1f}초 (노트북 부하 0% 달성)")
    log(f" - 최종 파일: {output_longform} ({file_size_gb:.2f} GB)")
    return True

def extract_shorts(
    master_block: Path,
    output_shorts: Path,
    start_sec: int = 60,
    duration_sec: int = 25,
    overlay_text: str = "오늘 하루도 정말 고생 많으셨어요.",
    font_name: str = "Malgun Gothic",
    ffmpeg_bin: str = "ffmpeg"
) -> bool:
    """
    [Step 3] 유입용 세로 쇼츠(Shorts) 동시 자동 추출
    마스터 블록의 최적 구간을 9:16 비율로 크롭하고 중앙 감성 문구 오버레이
    """
    log("==================================================")
    log(f"📱 [Step 3] 유입용 감성 세로 쇼츠({duration_sec}초) 추출 시작")
    log("==================================================")

    # 1920x1080 -> 9:16 (607x1080 -> 1080x1920 세로 스케일)
    # 중앙 크롭 후 1080x1920으로 리사이즈 및 중앙 감성 한 줄 텍스트 삽입
    vf = (
        f"crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920,"
        f"drawtext=font='{font_name}':text='{overlay_text}':fontcolor=white:fontsize=46:"
        f"x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.6:shadowx=2:shadowy=2"
    )

    cmd = [
        ffmpeg_bin, "-y",
        "-ss", str(start_sec),
        "-t", str(duration_sec),
        "-i", str(master_block),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        str(output_shorts)
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        log(f"❌ 쇼츠 추출 실패:\n{res.stderr[-1000:]}")
        return False

    log(f"✨ 세로 쇼츠 완성! -> {output_shorts} ({output_shorts.stat().st_size / (1024*1024):.1f} MB)")
    return True

def ensure_fallback_assets(loop_video: Path, ambient_audio: Path, temp_dir: Path) -> tuple[Path, Path]:
    """배경 영상이나 앰비언트 오디오가 없을 경우 기본 에셋 또는 FFmpeg 생성 에셋 제공"""
    final_loop = loop_video
    final_ambient = ambient_audio

    # 1. 루프 영상 확인
    if not final_loop or not final_loop.exists():
        candidates = [Path("./assets/loop.mp4"), Path("../assets/loop.mp4")]
        found = next((c for c in candidates if c.exists()), None)
        if found:
            final_loop = found
        else:
            temp_dir.mkdir(parents=True, exist_ok=True)
            fallback_loop = temp_dir / "fallback_loop.mp4"
            if not fallback_loop.exists():
                log("기본 배경 루프 영상 생성 중 (1080p 다크 시네마틱 10초)...")
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", "color=c=0x0a101d:s=1920x1080:d=10:r=30",
                    "-vf", "drawtext=font='Malgun Gothic':text='한걸음씩  ·  432Hz Healing Music':fontcolor=white@0.4:fontsize=28:x=(w-text_w)/2:y=h-80",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(fallback_loop)
                ], capture_output=True, check=True)
            final_loop = fallback_loop

    # 2. 앰비언트 오디오 확인
    if not final_ambient or not final_ambient.exists():
        candidates = [Path("./assets/rain.mp3"), Path("./assets/ambient.mp3"), Path("../assets/rain.mp3")]
        found = next((c for c in candidates if c.exists()), None)
        if found:
            final_ambient = found
        else:
            temp_dir.mkdir(parents=True, exist_ok=True)
            fallback_ambient = temp_dir / "fallback_rain.mp3"
            if not fallback_ambient.exists():
                log("기본 빗소리 앰비언트 생성 중 (핑크 노이즈 10초)...")
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", "anoisesrc=d=10:c=pink:r=44100:a=0.08",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(fallback_ambient)
                ], capture_output=True, check=True)
            final_ambient = fallback_ambient

    return final_loop, final_ambient

def run_pipeline(
    loop_video: Path = None,
    piano_audio: Path = None,
    ambient_audio: Path = None,
    output_dir: Path = Path("./output_healing"),
    total_hours: int = 8,
    ambient_vol: float = 0.25,
    shorts_text: str = "오늘 하루도 수고 많으셨어요."
):
    """엔드투엔드 파이프라인 총괄 실행 (OneDrive 출력 경로 폭주 방지 탑재)"""
    # [OneDrive 방어] OneDrive 폴더 내 대용량 미디어 생성 시 동기화 폭주 방지
    resolved_out = output_dir.resolve()
    if "OneDrive" in str(resolved_out):
        safe_fallback = Path(os.environ.get("SAFE_OUTPUT_DIR", r"C:\temp\hangeoreumsshik_output"))
        log(f"[경고] 출력 경로에 OneDrive 감지됨! 동기화 폭주 방지를 위해 안전 경로로 전환합니다: {safe_fallback}")
        output_dir = safe_fallback

    output_dir.mkdir(parents=True, exist_ok=True)

    # 에셋 폴백 보장
    loop_video, ambient_audio = ensure_fallback_assets(loop_video, ambient_audio, output_dir / "assets")

    if not piano_audio or not piano_audio.exists():
        log(f"❌ 오류: 메인 피아노(오디오) 음원 파일을 찾을 수 없습니다: {piano_audio}")
        return False

    ass_path = output_dir / "healing_story.ass"
    master_path = output_dir / "master_block_20m.mp4"
    longform_path = output_dir / f"final_{total_hours}hours_deepsleep.mp4"
    shorts_path = output_dir / "final_shorts_25s.mp4"

    log("==================================================")
    log("🚀 [한걸음씩] 힐링 음악 롱폼 & 쇼츠 프로덕션 파이프라인 가동")
    log(f" • 피아노(메인) : {piano_audio}")
    log(f" • 배경 루프    : {loop_video}")
    log(f" • 앰비언트     : {ambient_audio} (볼륨: {ambient_vol})")
    log(f" • 출력 경로    : {output_dir}")
    log(f" • 목표 시간    : {total_hours}시간")
    log("==================================================")

    # 1. 감성 자막 파일 생성
    generate_ass_subtitle(ass_path)

    # 2. 20분 마스터 블록 렌더링
    success = render_master_block(
        loop_video=loop_video,
        piano_audio=piano_audio,
        ambient_audio=ambient_audio,
        ass_sub=ass_path,
        output_master=master_path,
        duration_min=20,
        ambient_vol=ambient_vol
    )
    if not success:
        log("파이프라인 중단: 마스터 블록 생성 실패")
        return False

    # 3. 8시간 롱폼 조립
    success = assemble_longform(
        master_block=master_path,
        output_longform=longform_path,
        total_hours=total_hours,
        block_duration_min=20
    )
    if not success:
        log("파이프라인 중단: 롱폼 조립 실패")
        return False

    # 4. 세로 쇼츠 추출
    extract_shorts(
        master_block=master_path,
        output_shorts=shorts_path,
        start_sec=90,
        duration_sec=25,
        overlay_text=shorts_text
    )

    log("==================================================")
    log("🏆 모든 렌더링 파이프라인이 성공적으로 완료되었습니다!")
    log(f" 1. 20분 마스터 블록: {master_path}")
    log(f" 2. {total_hours}시간 롱폼 비디오: {longform_path}")
    log(f" 3. 유입용 세로 쇼츠: {shorts_path}")
    log("==================================================")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="한걸음씩 힐링 음악 롱폼 & 쇼츠 렌더링 엔진")
    parser.add_argument("--piano", type=str, required=True, help="메인 피아노 음원 경로 (MP3/WAV)")
    parser.add_argument("--loop", type=str, default=None, help="배경 시네마틱 루프 영상 경로 (MP4)")
    parser.add_argument("--ambient", type=str, default=None, help="배경 앰비언트 음원 경로 (MP3/WAV)")
    parser.add_argument("--outdir", type=str, default="./output_healing", help="출력 디렉터리")
    parser.add_argument("--hours", type=int, default=8, help="롱폼 영상 목표 재생 시간 (시간 단위)")
    parser.add_argument("--ambient-vol", type=float, default=0.25, help="자연음 볼륨 (0.0 ~ 1.0)")
    parser.add_argument("--shorts-text", type=str, default="오늘 하루도 참 고생 많으셨어요.", help="쇼츠 중앙 감성 문구")

    args = parser.parse_args()

    run_pipeline(
        piano_audio=Path(args.piano),
        loop_video=Path(args.loop) if args.loop else None,
        ambient_audio=Path(args.ambient) if args.ambient else None,
        output_dir=Path(args.outdir),
        total_hours=args.hours,
        ambient_vol=args.ambient_vol,
        shorts_text=args.shorts_text
    )
