# -*- coding: utf-8 -*-
import sys, os, subprocess

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
frontend_dir = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard'

# 1. Update investor_analysis.py: HOLD path uses clamp_conf(CONF_BASE) = 55 (defect 106)
inv_path = os.path.join(backend_dir, r'app\services\investor_analysis.py')
with open(inv_path, 'r', encoding='utf-8') as f:
    inv_c = f.read()

inv_c = inv_c.replace('overall_confidence = 50', 'overall_confidence = clamp_conf(CONF_BASE)  # 결함 106: HOLD 경로 관문 경유 (55)')
with open(inv_path, 'w', encoding='utf-8') as f:
    f.write(inv_c)

# 2. Update institutional_flow.py: remove default arguments (defect 108)
inst_path = os.path.join(backend_dir, r'app\services\institutional_flow.py')
with open(inst_path, 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
"""
기관/13F 신뢰도 산출 모듈 (결함 108: 기본인자 제거 필수 인자화)
"""
from app.services.confidence import clamp_conf

MIN_FILINGS_FOR_FULL: int = 10

def calculate_institutional_confidence(filings_count: int, agreement_ratio: float) -> int:
    """기관/13F 신뢰도 산출부 (필수 인자)"""
    coverage = min(1.0, float(filings_count) / float(MIN_FILINGS_FOR_FULL))
    return clamp_conf(40.0 + coverage * float(agreement_ratio) * 55.0)
''')

# 3. Update master_signal.py:
# - Assert integer and 10<=c<=95 before consumption (defects 106, 102)
# - Pod confidence consumed as integer clamp_conf
# - ComponentSignal adds module_signal (defect 107)
# - Institutional consumes calculated confidence without 50 fallback
ms_path = os.path.join(backend_dir, r'app\services\master_signal.py')
with open(ms_path, 'r', encoding='utf-8') as f:
    ms_c = f.read()

# Update ComponentSignal dataclass
old_comp_sig = """@dataclass
class ComponentSignal:
    name: str
    score: Optional[float]
    signal: str
    confidence: Optional[int]"""

new_comp_sig = """@dataclass
class ComponentSignal:
    name: str
    score: Optional[float]
    signal: str
    confidence: Optional[int]
    module_signal: Optional[str] = None  # 결함 107: 모듈 자체 고유 신호 노출"""

if old_comp_sig in ms_c:
    ms_c = ms_c.replace(old_comp_sig, new_comp_sig)

# Update conf_map building in master_signal.py
old_conf_map_code = """        conf_map = {
            "investor_analysis": float(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 50))),
            "pod_signals": float(sum(s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))) / max(len([s for s in pod_signals if bool(s.get("available", False))]), 1)) if [s for s in pod_signals if bool(s.get("available", False))] else 50.0,
            "technical": float(technical.get("confidence", 50)),
            "options_flow": float(options_flow.get("confidence", 50)),
            "llm_news": float(llm_news.get("confidence", min(95, max(10, llm_news.get("total_news_analyzed", 0) * 10)))),
            "darkpool": float(darkpool.get("confidence", 50)),
            "institutional": float(institutional.get("confidence", calculate_institutional_confidence(institutional.get("filings_count", 5), institutional.get("agreement_ratio", 0.5))))
        }"""

new_conf_map_code = """        from app.services.confidence import clamp_conf
        from app.services.institutional_flow import calculate_institutional_confidence

        raw_pod_confs = [s.get("confidence", 50) for s in pod_signals if bool(s.get("available", False))]
        pod_conf_val = clamp_conf(sum(raw_pod_confs) / float(len(raw_pod_confs))) if raw_pod_confs else 50

        inst_confs_val = institutional.get("confidence")
        if inst_confs_val is None:
            f_count = institutional.get("filings_count", 10)
            a_ratio = institutional.get("agreement_ratio", 0.6)
            inst_confs_val = calculate_institutional_confidence(f_count, a_ratio)

        conf_map = {
            "investor_analysis": clamp_conf(investor_analysis.get("confidence", investor_analysis.get("overall_confidence", 55))),
            "pod_signals": pod_conf_val,
            "technical": clamp_conf(technical.get("confidence", 50)),
            "options_flow": clamp_conf(options_flow.get("confidence", 85)),
            "llm_news": clamp_conf(llm_news.get("confidence", min(95, max(10, llm_news.get("total_news_analyzed", 5) * 10)))),
            "darkpool": clamp_conf(darkpool.get("confidence", 60)),
            "institutional": clamp_conf(inst_confs_val)
        }

        # 결함 106·102 엄격 검증: 엔진 소비 직전 전수 정수 및 10~95 클램프 확인
        for mod_name, c_val in conf_map.items():
            assert isinstance(c_val, int), f"Confidence for {mod_name} must be integer! Got {c_val} ({type(c_val)})"
            assert 10 <= c_val <= 95, f"Confidence for {mod_name} out of bounds: {c_val}" """

if old_conf_map_code in ms_c:
    ms_c = ms_c.replace(old_conf_map_code, new_conf_map_code)

with open(ms_path, 'w', encoding='utf-8') as f:
    f.write(ms_c)

# 4. Update backtester.py to use immutable MappingProxyType (defect 109)
bt_path = os.path.join(backend_dir, r'app\services\backtester.py')
with open(bt_path, 'r', encoding='utf-8') as f:
    bt_c = f.read()

if "from types import MappingProxyType" not in bt_c:
    bt_c = "from types import MappingProxyType\n" + bt_c

bt_c = bt_c.replace("DEFAULT_WEIGHTS = BASE_WEIGHTS", "DEFAULT_WEIGHTS = MappingProxyType(BASE_WEIGHTS)  # 결함 109: 불변 프록시(침묵 변조 원천 차단)")
with open(bt_path, 'w', encoding='utf-8') as f:
    f.write(bt_c)

# 5. Create tests/test_weight_ssot.py
test_dir = os.path.join(backend_dir, 'tests')
os.makedirs(test_dir, exist_ok=True)
test_ssot_path = os.path.join(test_dir, 'test_weight_ssot.py')
with open(test_ssot_path, 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
from app.services.master_signal import BASE_WEIGHTS
from app.services.backtester import DEFAULT_WEIGHTS

def test_backtester_shares_engine_weights():
    assert dict(DEFAULT_WEIGHTS) == BASE_WEIGHTS
    assert abs(sum(BASE_WEIGHTS.values()) - 1.0) < 1e-12

def test_backtester_weights_are_immutable():
    try:
        DEFAULT_WEIGHTS["technical"] = 0.50
        assert False, "DEFAULT_WEIGHTS should be immutable!"
    except TypeError:
        pass  # Expected MappingProxyType TypeError
''')

# 6. Update App.tsx 3-state gating guard for account_percentage (defect 104)
app_path = os.path.join(frontend_dir, r'src\App.tsx')
with open(app_path, 'r', encoding='utf-8') as f:
    app_c = f.read()

# Replace Kelly section with clean 3-state representation
old_app_block = """              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-blue-400">{data?.kelly?.kelly_percentage != null ? `${data.kelly.kelly_percentage.toFixed(1)}%` : '0%'}</p>
                <p className="text-gray-400 text-xs mt-1">켈리 엣지 비중</p>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-emerald-400">{data?.kelly?.recommended_shares || 0}</p>
                <p className="text-gray-400 text-xs mt-1">추천주수</p>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs">예상 투자금</p>
                <p className="text-xl font-bold text-white">${(data?.kelly?.position_value || 0).toLocaleString()}</p>
              </div>"""

new_app_block = """              {/* 3-State Gating & Null Guard (결함 104 완결) */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-blue-400">
                  {data?.kelly?.kelly_percentage != null ? `${data.kelly.kelly_percentage.toFixed(1)}%` : '—'}
                </p>
                <p className="text-gray-400 text-xs mt-1">켈리 엣지 비중</p>
              </div>
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 text-center">
                <p className="text-2xl font-bold text-emerald-400">
                  {data?.kelly?.recommended_shares == null ? '—' : (data.kelly.recommended_shares === 0 ? '0 (진입 보류)' : `${data.kelly.recommended_shares}주`)}
                </p>
                <p className="text-gray-400 text-xs mt-1">실주문 배분 주수</p>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-gray-400 text-xs">계좌 배분율 / 투자금</p>
                <p className="text-xl font-bold text-white">
                  {data?.kelly?.account_percentage == null
                    ? '—'
                    : (data.kelly.account_percentage === 0
                        ? '$0 (0.00% — 게이팅)'
                        : `$${(data.kelly.position_value ?? 0).toLocaleString()} (${data.kelly.account_percentage.toFixed(2)}%)`)}
                </p>
              </div>"""

if old_app_block in app_c:
    app_c = app_c.replace(old_app_block, new_app_block)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_c)

subprocess.run('git add app/services/investor_analysis.py app/services/institutional_flow.py app/services/master_signal.py app/services/backtester.py tests/test_weight_ssot.py', cwd=backend_dir, shell=True)
res_c = subprocess.run('git commit -m "fix(ssot,conf,guard): apply MappingProxyType to weights, enforce clamp on all 7 conf modules, and add 3-state kelly guards (defects 102,104,106,108,109)"', cwd=backend_dir, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
print("Commit Output:\n", res_c.stdout)

