---
name: aon-vibe3d-movie-director
version: v11.49-AON-IMPECCABLE-SHIELD
antibody: R49
organ: 제25기관 · rgon_aon_vibe3d_director
description: "유튜브 2대 3D AI(Blender MCP 결정론적 Scene-as-Code 영화 세트장 + 국산 VARCO 3D 다중 에셋 분리·PBR ORM·AI 자동 리깅) 통합 흡수 제25기관 스킬"
hexagrams: ["#22 산화비 ☶☲", "#14 화천대유 ☲☰"]
---

# 🎬 아온 바이브 3D 시네마틱 디렉터 & VARCO 플로우 스튜디오 (aon-vibe3d-movie-director)

## 📌 개요
제25기관 `rgon_aon_vibe3d_director.py`에서 제공하는 3D 시네마틱 영화 세트장 및 VARCO 3D Flow 자동화 스킬.

## 🛠️ 핵심 기능
1. **결정론적 `Scene-as-Code` 씬 그래프 (`build_scene`, `scene_hash`)**:
   - 동일 입력 -> 동일 `scene_hash` 100% 보장.
2. **국산 VARCO 3D 핵심 기술 3종**:
   - `scene_to_props_isolate`: 1장 스케치/이미지 -> 다중 3D 에셋 자동 분리 Flow 파이프라인.
   - `pbr_orm_material`: Roughness/Metallic/AO 실시간 표면 광택 및 젤리 투명도 제어.
   - `ai_auto_rig_motion`: 2족/4족 + 손가락 3관절 AI 자동 뼈대 및 4대 시네마틱 모션(총총걷기, 전력질주, 부리부리댄스, 우주유영).
3. **4대 시네마틱 3D 세트장 프리셋**:
   - `haesang_aon_shortfilm`, `blueprint_to_3d_building`, `product_3d_commercial`, `simulator_digital_twin`
4. **듀얼 출력 렌더러**:
   - 외부 CDN 0% HTML5 Canvas 3D 플레이어 + WebM 즉시 녹화.
   - 오픈소스 `mcp-for-blender` 호환 표준 `import bpy` 스크립트.
