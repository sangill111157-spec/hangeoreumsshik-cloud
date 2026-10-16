"""
══════════════════════════════════════════════════════════════════
 한걸음씩 통합 스케줄러 래퍼 (크로스 플랫폼: Linux / Windows 지원)
 scheduler_wrapper.py
══════════════════════════════════════════════════════════════════
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# 동적 경로 및 인터프리터 결정 (로컬 Windows Python314 및 클라우드 Linux 러너 호환)
AUTO = Path(__file__).resolve().parent
LOG_DIR = AUTO / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 로컬 Windows에 Python314가 있으면 우선 사용, 없으면 sys.executable 사용
win_py314 = Path(r"C:\Users\sangi\AppData\Local\Programs\Python\Python314\python.exe")
if win_py314.exists():
    PYTHON = str(win_py314)
else:
    PYTHON = sys.executable

AGENT = str(AUTO / 'channel_agent.py')

def run_with_retry(command, max_retries=2):
    """지정된 모듈을 실행하고 실패 시 재시도 (텔레그램 관제탑 연동)"""
    flag_path = AUTO / "BLOCKED_BY_ERROR.flag"
    if flag_path.exists():
        print(f"[{datetime.now()}] [스케줄러 차단] 장애 플래그 존재: {flag_path.name}")
        return 1

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = LOG_DIR / f'{command}_{timestamp}.log'

    for attempt in range(1, max_retries + 1):
        print(f'[{datetime.now().strftime("%H:%M:%S")}] {command} 실행 시작 (시도 {attempt}/{max_retries})')

        try:
            if command == 'report':
                script_path = str(AUTO / 'telegram_morning_report.py')
                run_args = [PYTHON, script_path]
            elif command == 'analytics':
                script_path = str(AUTO / 'update_3channels_analytics.py')
                run_args = [PYTHON, script_path]
            elif command == 'produce_healing':
                script_path = str(AUTO / 'healing_music_producer.py')
                run_args = [PYTHON, script_path]
            else:
                run_args = [PYTHON, AGENT, command]

            result = subprocess.run(
                run_args,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=1800,  # 30분 타임아웃
                cwd=str(AUTO)
            )

            # 로그 기록
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f'=== {command} | 시도 {attempt} | {datetime.now()} ===\n')
                f.write(f'Return code: {result.returncode}\n\n')
                f.write('--- STDOUT ---\n')
                f.write(result.stdout or '(empty)\n')
                f.write('\n--- STDERR ---\n')
                f.write(result.stderr or '(empty)\n')

            if result.returncode == 0:
                print(f'[OK] {command} 성공 완료!')
                # 30일 초과 로그 정리
                cutoff = time.time() - (30 * 86400)
                for old_log in LOG_DIR.glob(f'{command}_*.log'):
                    if old_log.stat().st_mtime < cutoff:
                        old_log.unlink()
                return 0
            else:
                print(f'[FAIL] {command} 실패 (종료 코드 {result.returncode})')
                if result.stderr:
                    print(f' 에러 요약: {result.stderr[-300:]}')
                if attempt < max_retries:
                    print('  30초 후 재시도...')
                    time.sleep(30)

        except subprocess.TimeoutExpired:
            print(f'[TIMEOUT] {command} 30분 초과')
            if attempt < max_retries:
                time.sleep(30)
        except Exception as e:
            print(f'[ERROR] {command}: {e}')
            if attempt < max_retries:
                time.sleep(30)

    # 모든 재시도 실패 시 플래그 생성
    fail_flag = LOG_DIR / f'FAILED_{command}_{timestamp}.flag'
    fail_flag.write_text(f'{command} failed after {max_retries} attempts at {datetime.now()}', encoding='utf-8')
    return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('사용법: python scheduler_wrapper.py <report|analytics|strategy|produce_healing>')
        sys.exit(1)
    cmd = sys.argv[1]
    sys.exit(run_with_retry(cmd))
