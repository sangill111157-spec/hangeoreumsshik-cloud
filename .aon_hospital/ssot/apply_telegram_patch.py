import re

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\telegram_notifier.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update parse_mode default from Markdown to HTML
code = code.replace('parse_mode: str = "Markdown"', 'parse_mode: str = "HTML"')

# 2. Add format_telegram_alert function
format_alert_func = '''import html

def format_telegram_alert(
    level: str,          # "긴급", "주의", "정보"
    is_paper: bool,      # True: "모의", False: "실전"
    title: str,          # 무슨 일인지 한 줄
    impact: str,         # 지금 무엇이 멈췄는지 (예: "손절 감시가 3분째 멈춤")
    action: str,         # 대표가 해야 할 것, 또는 "조치 불필요, 자동 재시도 중"
    tech_info: str = ""  # 오류 코드/원문 (맨 아래 한 줄)
) -> str:
    """
    정형화된 텔레그램 알림 HTML 서식 생성기 (3단계 등급, 모의/실전 표기, 특수문자 escape 적용)
    """
    level_tag = f"[{level}]"
    mode_tag = "[모의]" if is_paper else "[실전]"

    msg = (
        f"<b>{level_tag}{mode_tag} {html.escape(title)}</b>\\n"
        f"<b>영향:</b> {html.escape(impact)}\\n"
        f"<b>할 일:</b> {html.escape(action)}"
    )
    if tech_info:
        msg += f"\\n<b>기술 정보:</b> <code>{html.escape(tech_info)}</code>"
    return msg
'''

if "def format_telegram_alert" not in code:
    code = format_alert_func + "\n" + code

# 3. Add tracking attributes to __init__
old_init = '''        if not self.enabled:
            logger.warning("Telegram notifier disabled: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        else:
            logger.info("Telegram notifier enabled")'''

new_init = '''        self.last_send_error: Optional[str] = None
        self.last_send_timestamp: float = 0.0
        self.failed_send_count: int = 0

        if not self.enabled:
            logger.warning("Telegram notifier disabled: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        else:
            logger.info("Telegram notifier enabled")'''

code = code.replace(old_init, new_init, 1)

# 4. Update send_message to track errors and success
old_success = '''                if response.status_code == 200:
                    logger.info("Telegram message sent successfully")
                    return True'''

new_success = '''                if response.status_code == 200:
                    logger.info("Telegram message sent successfully")
                    self.last_send_timestamp = datetime.now().timestamp()
                    return True'''

code = code.replace(old_success, new_success, 1)

old_fail = '''            except Exception as e:
                logger.error(f"Failed to send Telegram message: {str(e)}")
                return False'''

new_fail = '''            except Exception as e:
                logger.error(f"Failed to send Telegram message: {str(e)}")
                self.last_send_error = str(e)
                self.failed_send_count += 1
                return False'''

code = code.replace(old_fail, new_fail, 1)

with open(r"C:\trading\package\nvda_trading_system\backend\app\services\telegram_notifier.py", "w", encoding="utf-8") as f:
    f.write(code)

print("telegram_notifier.py patched successfully")
