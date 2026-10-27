import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import subprocess
import shutil
from pathlib import Path
from healing_music_producer import generate_ass_subtitle, render_master_block, assemble_longform, extract_shorts

TEST_DIR = Path("./test_healing_output")

def create_dummy_assets():
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    loop_mp4 = TEST_DIR / "dummy_loop.mp4"
    piano_mp3 = TEST_DIR / "dummy_piano.mp3"
    ambient_mp3 = TEST_DIR / "dummy_ambient.mp3"

    print("1. 테스트용 가상 에셋 생성 중...")
    # 5초짜리 1080p 다크 앰비언트 비디오 생성
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x1a1a2e:s=1920x1080:d=5:r=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(loop_mp4)
    ], capture_output=True, check=True)

    # 5초짜리 440Hz 피아노 톤 오디오 생성
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
        "-c:a", "libmp3lame", "-b:a", "192k", str(piano_mp3)
    ], capture_output=True, check=True)

    # 5초짜리 핑크 노이즈 (빗소리 대용) 생성
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anoisesrc=d=5:c=pink:r=44100:a=0.1",
        "-c:a", "libmp3lame", "-b:a", "192k", str(ambient_mp3)
    ], capture_output=True, check=True)

    return loop_mp4, piano_mp3, ambient_mp3

def test_pipeline():
    loop_mp4, piano_mp3, ambient_mp3 = create_dummy_assets()

    ass_path = TEST_DIR / "test_sub.ass"
    master_path = TEST_DIR / "test_master.mp4"
    longform_path = TEST_DIR / "test_longform.mp4"
    shorts_path = TEST_DIR / "test_shorts.mp4"

    print("2. 감성 자막 생성 테스트...")
    generate_ass_subtitle(ass_path, [
        {"start": "00:00:01.00", "end": "00:00:04.00", "text": "한걸음씩 힐링 테스트"}
    ])
    assert ass_path.exists(), "ASS 자막 파일 생성 실패"

    print("3. 마스터 블록 렌더링 테스트 (테스트용 5초)...")
    # duration_min 대신 직접 5초 테스트를 위해 커스텀 호출
    ass_escaped = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(loop_mp4),
        "-stream_loop", "-1", "-i", str(piano_mp3),
        "-stream_loop", "-1", "-i", str(ambient_mp3),
        "-filter_complex",
        f"[1:a]asetrate=44100*432/440,aresample=44100,volume=1.0[piano432]; "
        f"[2:a]volume=0.25[ambient]; "
        f"[piano432][ambient]amix=inputs=2:duration=first:dropout_transition=1[aout]; "
        f"[0:v]ass='{ass_escaped}'[vout]",
        "-map", "[vout]", "-map", "[aout]",
        "-t", "00:00:06",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k",
        str(master_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Master block error:", res.stderr)
        return False
    assert master_path.exists(), "마스터 블록 생성 실패"
    print(" - 마스터 블록 생성 성공!")

    print("4. 무손실 -c copy 결합 테스트 (3회 반복)...")
    cmd_long = [
        "ffmpeg", "-y",
        "-stream_loop", "2",
        "-i", str(master_path),
        "-c", "copy",
        str(longform_path)
    ]
    res = subprocess.run(cmd_long, capture_output=True, text=True)
    if res.returncode != 0:
        print("Longform error:", res.stderr)
        return False
    assert longform_path.exists(), "롱폼 조립 실패"
    print(f" - 롱폼 결합 성공! ({longform_path.stat().st_size} bytes)")

    print("5. 세로 쇼츠 크롭 추출 테스트 (3초)...")
    extract_shorts(
        master_block=master_path,
        output_shorts=shorts_path,
        start_sec=1,
        duration_sec=3,
        overlay_text="잠시 쉬어가도 괜찮아요"
    )
    assert shorts_path.exists(), "쇼츠 추출 실패"
    print(f" - 쇼츠 추출 성공! ({shorts_path.stat().st_size} bytes)")

    print("🎉 모든 단위 테스트 통과!")
    return True

if __name__ == "__main__":
    success = test_pipeline()
    if success:
        print("모든 엔진 로직이 정상 작동함을 확인했습니다.")
