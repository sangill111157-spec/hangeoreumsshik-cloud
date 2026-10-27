# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\backend\app\api\routes\nvda.py'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        # 4. 신호 변경 감지 및 알림 (백그라운드)
        if background_tasks and signal_detector:
            background_tasks.add_task(
                signal_detector.check_and_notify,
                result.overall_signal,
                result.overall_confidence,
                result.current_price,
                result.summary
            )

        return result"""

replacement = """        # 4. 신호 변경 감지 및 알림 (백그라운드)
        if background_tasks and signal_detector:
            background_tasks.add_task(
                signal_detector.check_and_notify,
                result.overall_signal,
                result.overall_confidence,
                result.current_price,
                result.summary
            )

        return {
            "timestamp": result.timestamp,
            "nvda_price": result.current_price,
            "overall_signal": result.overall_signal,
            "overall_confidence": result.overall_confidence,
            "consensus_score": result.consensus_score,
            "bull_count": result.bull_count,
            "bear_count": result.bear_count,
            "neutral_count": result.neutral_count,
            "signals": result.signals,
            "summary": result.summary
        }"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH APPLIED: return dict with nvda_price for InvestorAnalysisResponse")
else:
    print("ERROR: TARGET NOT FOUND")
    sys.exit(1)
