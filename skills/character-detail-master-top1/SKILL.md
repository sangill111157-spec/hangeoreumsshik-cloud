---
name: character-detail-master-top1
category: character-3d-master
hexagram_tag: "#04-蒙"
version: v11.28-AON-3DDROP
antibody: R29
---
# 💧 전 세계 TOP 1 캐릭터 디테일 & 3D 물방울 졸라맨 마스터 (아온 · A-ON · 芽溫)

R29: 캐릭터 디테일 TOP 1 스킬 마스터 & 아온(A-ON·芽溫) 3D 물방울 졸라맨 육신 — 디즈니 7대 모션 법칙(스쿼시&스트레치·시차·팔로스루) + 8-Stop 3D Liquid-Glass/Claymorphism 입체 필터 + 관절형 졸라맨 팔다리 통합

## 1. 전 세계 TOP 1 캐릭터 디테일 흡수원
- **ChanMeng666/svg-animation-studio**: 디즈니 7대 마이크로 애니메이션 법칙 (Squash & Stretch 15% 슬라임 탄성, Anticipation, Ease-In-Out, Follow-Through, Secondary Action, Staggering 0.15s 시차, Iconic Appeal)
- **nextlevelbuilder/ui-ux-pro-max-skill**: 8-Stop 3D Liquid-Glass & Claymorphism 구체 볼륨 셰이딩 + SVG `feGaussianBlur`/`feComposite` 3D Inner Depth 필터

## 2. 아온(A-ON·芽溫) 3D 물방울 + 졸라맨 팔다리 구조
- **몸통**: 황금비율 3D 물방울(`#aonDropGrad` 8-Stop + `#aonInner3D` 입체 음영 + 3중 유리알 굴절 하이라이트 + 점프 연동 `#aonShadow`)
- **얼굴**: 5겹 보석 눈망울(4.4s 깜빡임 + 쓰다듬기 시 `^ ‿ ^` 반달 눈웃음) + 말랑 핑크 볼터치 + 오물오물 토크 입매
- **졸라맨 팔다리**: 어깨·골반 관절 축(`transform-origin`) 2중 네온 스틱 팔다리 + 동그란 콩알 손/발 + 쓰다듬기 시 두 팔 만세(`🙌`) 점프
- **3D 터치 틸트**: `perspective: 680px` 기반 포인터/터치 3차원 회전 반응

## 3. 실행
```bash
python rgon_k_avatar_engine.py --ensure-index --run --merge --self-test
```
