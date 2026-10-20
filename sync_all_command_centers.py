# -*- coding: utf-8 -*-
"""
sync_all_command_centers.py — 4개 커맨드 센터 시트 원커맨드 통합 동기화
실행: python sync_all_command_centers.py

[1/4] 👴 한걸음씩 SHIN FAMILY COMMAND CENTER
[2/4] 🎵 부스터 플리 BOOSTER PLAYLIST COMMAND CENTER
[3/4] ☕ Café Hour Command Center
[4/4] 📝 BLOG AUTOMATION COMMAND CENTER
"""
import os, sys, subprocess
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

AUTO = Path(r'C:\Users\sangi\OneDrive\Desktop\hangeoreumsshik\automation')
SHIN_AGENT = Path(r'c:\Users\sangi\Downloads\shin-agent')

def run_script(name, script_path, cwd=None):
    """스크립트 실행 및 결과 반환"""
    print(f"\n{'─' * 60}")
    print(f"  🔄 {name} 실행 중...")
    print(f"{'─' * 60}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(cwd or script_path.parent),
            capture_output=True, text=True, encoding='utf-8',
            timeout=120
        )
        
        if result.returncode == 0:
            # 주요 로그만 출력
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and ('✅' in line or '❌' in line or '⚠️' in line or '완료' in line or '실패' in line):
                    print(f"  {line}")
            return True, ""
        else:
            err = result.stderr[:200] if result.stderr else result.stdout[:200]
            print(f"  ❌ 실행 실패: {err}")
            return False, err
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ 타임아웃 (120초 초과)")
        return False, "타임아웃"
    except Exception as e:
        print(f"  ❌ 예외: {e}")
        return False, str(e)


def main():
    print("=" * 70)
    print(f"🚀 4개 커맨드 센터 시트 통합 동기화")
    print(f"   시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    results = {}
    
    # [1~3] 유튜브 3채널 트래픽 동기화
    analytics_script = AUTO / 'update_3channels_analytics.py'
    if analytics_script.exists():
        print(f"\n[1~3/4] 🎬 유튜브 3채널 트래픽 동기화")
        ok, err = run_script(
            "3채널 통합 (한걸음씩 + 부스터 플리 + Café Hour)",
            analytics_script,
            cwd=AUTO
        )
        results["YouTube 3채널"] = "✅" if ok else f"❌ {err}"
    else:
        print(f"\n  ⚠️ update_3channels_analytics.py를 찾을 수 없습니다")
        results["YouTube 3채널"] = "⚠️ 스크립트 없음"
    
    # [4] 블로그 자동화 시트 동기화
    blog_script = SHIN_AGENT / 'sync_blog_to_sheet.py'
    if blog_script.exists():
        print(f"\n[4/4] 📝 BLOG AUTOMATION COMMAND CENTER 동기화")
        ok, err = run_script(
            "블로그 자동화 파이프라인",
            blog_script,
            cwd=AUTO
        )
        results["블로그 자동화"] = "✅" if ok else f"❌ {err}"
    else:
        print(f"\n  ⚠️ sync_blog_to_sheet.py를 찾을 수 없습니다")
        results["블로그 자동화"] = "⚠️ 스크립트 없음"
    
    # 최종 결과 요약
    print(f"\n{'=' * 70}")
    print(f"📋 동기화 결과 요약")
    print(f"{'=' * 70}")
    for name, status in results.items():
        print(f"  {name}: {status}")
    
    print(f"\n  📊 시트 링크:")
    print(f"  👴 한걸음씩:    https://docs.google.com/spreadsheets/d/1mIu1vXu0luRSDNyjE-WkJaz91otX0OvgaBVrJj6rwnY")
    print(f"  🎵 부스터 플리: https://docs.google.com/spreadsheets/d/19yLh5tIUNg5gm3UpJxbCUmAfEUtotjrlrc7KMvp_KE4")
    print(f"  ☕ Café Hour:   https://docs.google.com/spreadsheets/d/1MqLCJNCdwPV8GrIhp5w3BdIsuVazIC2uREpgypUu9PI")
    print(f"  📝 블로그:      https://docs.google.com/spreadsheets/d/1gYDrCuqM2hKQbYyE3cYEZhJZEhrH_Is6tdUhsw-cgaw")
    
    print(f"\n  완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
