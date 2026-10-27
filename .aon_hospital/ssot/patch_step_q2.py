# -*- coding: utf-8 -*-
import sys

target_file = r'C:\trading\package\nvda_trading_system\nvda-trading-dashboard\src\App.tsx'

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update loadRiskData with useRef guard
t1 = """  // Load risk and rebalance data (STEP 41, STEP 42)
  const loadRiskData = async () => {
    try {
      const [riskResult, rebalanceResult] = (
        await Promise.allSettled([
          api.getRiskScore() as Promise<any>,
          api.getRebalancePlan() as Promise<any>
        ])
      ).map(r => (r.status === 'fulfilled' ? r.value : null));
      setRiskData(riskResult);
      setRebalanceData(rebalanceResult);
    } catch (err) {
      console.error('Failed to load risk data:', err);
    }
  };"""

r1 = """  // Load risk and rebalance data (STEP 41, STEP 42)
  const riskLoadingRef = useRef(false);
  const loadRiskData = async () => {
    if (riskLoadingRef.current) return;
    riskLoadingRef.current = true;
    try {
      const [riskResult, rebalanceResult] = (
        await Promise.allSettled([
          api.getRiskScore() as Promise<any>,
          api.getRebalancePlan() as Promise<any>
        ])
      ).map(r => (r.status === 'fulfilled' ? r.value : null));
      setRiskData(riskResult);
      setRebalanceData(rebalanceResult);
    } catch (err) {
      console.error('Failed to load risk data:', err);
    } finally {
      riskLoadingRef.current = false;
    }
  };"""

# 2. Remove duplicate useEffect
t2 = """  useEffect(() => {
    if (activeTab === 'dashboard' && !riskData) {
      loadRiskData();
    }
  }, [activeTab, riskData]);"""

if t1 not in content:
    print("ERROR: t1 NOT FOUND")
    sys.exit(1)

if t2 not in content:
    print("ERROR: t2 NOT FOUND")
    sys.exit(1)

content = content.replace(t1, r1, 1)
content = content.replace(t2, "", 1)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("PATCH STEP Q-2 APPLIED SUCCESSFULLY")
