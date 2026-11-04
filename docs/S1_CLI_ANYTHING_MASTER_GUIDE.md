# 🛠️ [S1_CLI_ANYTHING_MASTER_GUIDE] HKUDS CLI-Anything 실전 운용 마스터북

- **패키지**: `cli-anything-hub` (HKUDS GitHub 5만 스타 프로젝트)
- **명령어**: `cli-hub`
- **목적**: GUI 전용 툴 및 다양한 외부 서비스를 고속 네이티브 CLI 도구로 변환하여 에이전트 자율 시공 극대화

---

## 1. `cli-hub --help` 실측 명세
```text
Usage: cli-hub [OPTIONS] [COMMAND] [ARGS]...

  cli-hub — Download and manage CLI-Anything CLIs, public CLIs, and curated
  matrices.

Options:
  --version  Show version.
  --help     Show this message and exit.

Commands:
  can        Find a capability across all matrices for a task (e.g.
  info       Show details for a specific CLI.
  install    Install a CLI by name.
  launch     Launch an installed CLI, passing through any extra arguments.
  list       List all available CLIs.
  matrix     Browse matrices or list CLIs in a matrix.
  uninstall  Uninstall a CLI.
  update     Update installed CLIs or matrices.
  versions   List available versions of a CLI.
```

---

## 2. Solostack 영상 3대 실전 교훈
1. **네이티브 CLI 우선 (Native CLI First)**:
   - 무거운 GUI 브라우저나 복잡한 웹 래퍼 대신 경량화된 네이티브 CLI 도구를 최우선 사용하여 메모리와 토큰 소모를 최소화한다.
2. **작업 폴더 외부 쓰기 금지 & `scratch/` 격리**:
   - 임시 산출물과 가공 파일은 반드시 `scratch/` 디렉터리에 격리하여 소스 코드 루트 위생(Clean Root)을 수호한다.
3. **AI 단독 테스트 맹점 방지를 위한 삼성(三聖) 2단계 물리 비율 검수**:
   - AI의 텍스트 응답에만 의존하지 않고, 실제 물리적 비디오 종횡비(`SAR 1:1`, `DAR 9:16`), 광학 흐름 잔차, 파일 해시를 교차 실측하여 무결성을 검증한다.
