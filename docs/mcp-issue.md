# Claude Code MCP 설정 관리 문제

## 문제 요약

Claude Code의 MCP(Model Context Protocol) 서버 설정을 **유저 전역으로 멱등하게 관리할 공식적인 방법이 없다.**

Terraform처럼 선언적으로 "desired state"를 정의하고 적용하는 방식이 불가능하며, `~/.claude.json` 파일의 구조적 한계로 인해 설정 관리가 까다롭다.

## ~/.claude.json의 구조적 한계

`~/.claude.json`은 MCP 설정 외에도 다양한 런타임 상태를 저장한다:

| 카테고리 | 예시 | 특징 |
|---------|------|------|
| 사용자 설정 | `theme`, `editorMode` | 선언적 관리 가능 |
| 런타임 상태 | `numStartups`, `tipsHistory`, 캐시 | Claude Code가 자동 관리 |
| 인증 정보 | `oauthAccount`, `userID` | 덮어쓰면 안 됨 |
| 프로젝트 상태 | `projects.{path}.*` | 프로젝트별 자동 관리 |

**핵심 문제:**
- MCP 설정이 `projects.{path}.mcpServers`에 **프로젝트별로** 저장됨 (local scope)
- 전역 `mcpServers` 키를 추가해도 다른 런타임 데이터와 혼재
- 단순 파일 복사/덮어쓰기 시 OAuth, 통계 등 중요 데이터 손실 위험
- `jq`로 부분 병합 가능하지만, 멱등성 보장 어려움

## MCP 설정 스코프

| 스코프 | 저장 위치 | 용도 |
|-------|----------|------|
| Project | `.mcp.json` (프로젝트 루트) | 팀 공유, Git 버전 관리 |
| Local | `~/.claude.json` 내 프로젝트별 | 개인용, 현재 프로젝트만 |
| User | `~/.claude.json` 전역 | 모든 프로젝트에서 사용 |

**주의:** `~/.claude/settings.json`에 MCP 설정을 넣어도 **무시된다.**

## `claude mcp add` 명령어의 한계

Claude Code는 MCP 서버 추가를 위한 CLI 명령어를 제공한다:

```bash
claude mcp add <server-name> --scope user
claude mcp add-json <server-name> '{"command": "npx", "args": [...]}' --scope user
```

### 명령형(Imperative) 방식의 문제

| 문제 | 설명 |
|-----|------|
| **상태 추적 불가** | 어떤 서버가 추가되었는지 `~/.claude.json`을 직접 열어봐야 확인 가능 |
| **버전 관리 불가** | 변경 이력이 남지 않음. 언제, 왜 추가했는지 알 수 없음 |
| **재현성 없음** | 새 머신에서 동일한 환경 구성 시 명령어를 일일이 다시 실행해야 함 |
| **멱등성 없음** | 같은 명령어 재실행 시 중복 추가되거나 에러 발생 가능 |
| **롤백 어려움** | 이전 상태로 되돌리기 위한 메커니즘 없음 |

### 선언형(Declarative) 방식과의 비교

```bash
# 명령형 (claude mcp add) - 현재 방식
claude mcp add github --scope user
claude mcp add notion --scope user
claude mcp add jetbrains --scope user
# → 어디에 저장됐지? 다른 머신에서 어떻게 똑같이 설정하지?

# 선언형 (Terraform 스타일) - 원하는 방식
# .mcp.json 파일에 desired state 정의 후:
claude mcp apply  # ← 이런 명령어가 없음!
```

### IaC(Infrastructure as Code) 관점

Terraform, Ansible 등 현대적인 설정 관리 도구는 **선언형 + 멱등성**을 핵심으로 한다:

1. **선언형**: "이 상태가 되어야 한다"를 정의
2. **멱등성**: 몇 번을 실행해도 결과가 같음
3. **버전 관리**: 설정 파일을 Git으로 추적
4. **상태 파일**: 현재 상태와 desired state 비교 가능

`claude mcp add`는 이 중 어느 것도 지원하지 않는다. 이것이 `.mcp.json` 파일과 symlink 방식을 선택한 이유다.

## 관련 GitHub 이슈

### [Issue #4442](https://github.com/anthropics/claude-code/issues/4442) - 통합 계층적 설정 요청
- 현재 user/project 레벨만 존재, system-wide 설정 없음
- 엔터프라이즈 환경에서 정책 강제 불가
- **상태: 🟡 OPEN (미해결)**

### [Issue #4976](https://github.com/anthropics/claude-code/issues/4976) - MCP 설정 파일 위치 문서화 오류
- 문서에서 `~/.claude/settings.json`에 MCP 설정 가능하다고 했으나 실제로는 무시됨
- `~/.claude.json`만 유효
- **상태: ✅ CLOSED** (#3321 중복으로 닫힘, 2025-08-15)

### [Issue #6888](https://github.com/anthropics/claude-code/issues/6888) - MCP 스코프 저장 위치 불일치
- `claude mcp add --scope user` 명령어가 문서와 다른 위치에 저장
- User/Local 스코프 모두 `~/.claude.json`에 저장됨
- **상태: ✅ CLOSED** (문서 수정으로 해결, 2026-01-12)

### [Issue #5350](https://github.com/anthropics/claude-code/issues/5350) - 프로젝트 기반 MCP 설정 요청
- `.claude/` 서브디렉토리를 통한 프로젝트별 MCP 설정 요청
- **Maintainer 응답**: "`.mcp.json` in the root of the project is **already supported**"
- **상태: ✅ CLOSED** (기능 이미 존재, 2025-08-10)
- 📌 **우리의 symlink 방식이 공식 지원 방법과 일치함을 확인**

### [Issue #515](https://github.com/anthropics/claude-code/issues/515) - global.json MCP 서버 미적용
- `~/.claude-code/mcp/global.json`에 정의한 MCP 서버가 프로젝트에 적용 안 됨
- **Maintainer 응답 (ashwin-ant)**: 해당 경로는 **지원되지 않음**, CLI 명령어만 유효
- **상태: ✅ CLOSED** (2025-03-17)

### [Issue #11085](https://github.com/anthropics/claude-code/issues/11085) - 전역 MCP 기본값 설정
- User scope MCP 서버가 모든 프로젝트에서 기본 활성화되는 문제
- 매 프로젝트마다 수동 비활성화 필요 → **토큰 낭비** (전체 활성화 시 62.8k 토큰, 컨텍스트의 31%)
- `claude mcp set-default` 같은 명령어 요청
- **상태: 🟡 OPEN** (👍 8개, 30일 이상 비활성)

### [Issue #5722](https://github.com/anthropics/claude-code/issues/5722) - MCP Enable/Disable 토글
- `claude mcp enable/disable` 명령어 요청
- 현재 remove 시 모든 설정(env, auth) 손실
- **상태: 🟡 OPEN**

### [Issue #14320](https://github.com/anthropics/claude-code/issues/14320) - 서브에이전트별 MCP 설정
- 서브에이전트 레벨에서 MCP 서버 활성화 요청
- 메인 에이전트 컨텍스트 절약 목적
- **상태: 🟡 OPEN**

### [Issue #11903](https://github.com/anthropics/claude-code/issues/11903) - MCP 세션 지속성
- `mcp-add`로 추가한 서버가 세션 종료 시 사라짐
- **상태: ✅ CLOSED** (#3064, #6077 중복)

## Maintainer 입장 및 향후 방향 (2026-01-12 조사)

### Issue별 Maintainer 응답

| 이슈 | Maintainer 응답 | 해결 방식 |
|-----|----------------|----------|
| #4442 | ❌ 공식 답변 없음 | 30일 이상 방치, 진행 미정 |
| #4976 | 문서 오해 인정 | #3321 중복으로 닫음 |
| #6888 | 코드 변경 대신 문서 수정 | 현재 동작을 정식 스펙으로 문서화 |
| #5350 | ✅ **기능 이미 존재** | `.mcp.json` 프로젝트 스코프 공식 지원 확인 |
| #515 | `global.json` 미지원 명시 | CLI 명령어(`--scope global`) 사용 안내 |
| #11085 | "이미 되어야 하는데?" | 실제로는 전역 기본값 설정 불가, 미해결 |

### 핵심 발견: 우리 방식의 공식 지원 확인

**[Issue #5350](https://github.com/anthropics/claude-code/issues/5350)** 에서 Maintainer(jfpedroza)가 명확히 답변:

> "I think you missed that `.mcp.json` in the root of the project is supported."
> — https://docs.anthropic.com/en/docs/claude-code/mcp#project-scope

→ **프로젝트 루트의 `.mcp.json` 파일은 공식 지원 방법**이며, 우리의 symlink 방식이 이와 정확히 일치함.

### Anthropic의 핵심 결정

1. **`~/.claude.json` 구조 유지**: User/Local 스코프가 `~/.claude.json`에 저장되는 것은 **의도된 동작**
2. **하위 호환성 우선**: 새로운 `settings.json` 체계로 마이그레이션하지 않음
3. **문서 정확성 개선**: 코드 변경보다 문서를 현재 동작에 맞게 수정하는 방향 선호

### 향후 전망

| 관점 | Anthropic 입장 |
|-----|---------------|
| **프로젝트 스코프 `.mcp.json`** | ✅ **공식 지원** (우리 방식과 일치) |
| **MCP 전역 설정** | 현재 `~/.claude.json` 방식 유지, 변경 계획 없음 |
| **전역 기본값 (enable/disable)** | 많은 요청 있으나 미구현 (#11085, #5722) |
| **선언적 관리** | 지원 계획 언급 없음 (`claude mcp apply` 같은 명령어 없음) |
| **엔터프라이즈 지원** | 관련 이슈 다수 있으나 우선순위 미공개 |
| **서브에이전트별 MCP** | 요청 있으나 미구현 (#14320) |

### 지원되지 않는 경로 (주의)

| 경로 | 상태 |
|-----|------|
| `~/.claude-code/mcp/global.json` | ❌ 지원 안 함 (#515에서 확인) |
| `~/.claude/settings.json` 내 MCP | ❌ 권한 관리용으로만 사용 |

### 결론

**단기적으로 변화 없음**. 따라서:
- 현재 우리의 **symlink 방식이 공식 지원 방법과 일치**
- `~/.claude/settings.json` 기반 MCP 설정 지원 가능성 낮음
- 전역 기본값 설정 기능은 많은 요청에도 불구하고 미구현

## 커뮤니티 해결책

### [MCP-Config](https://github.com/Yoel-Klein/MCP-Config)
- **Symlink 기반** 중앙 설정 관리
- `.claude/` 디렉토리를 심볼릭 링크로 공유
- Dropbox 동기화 실패 경험 공유: "Claude Code가 계속 작은 파일을 쓰기 때문에 락 충돌"

### [claude-code-settings](https://github.com/feiskyer/claude-code-settings)
- Git 저장소로 설정, 커맨드, 스킬, 에이전트 관리
- 모듈식 설치 지원

## 우리의 해결책: Symlink 방식

### 전략
1. 이 프로젝트(`prompts`)를 MCP 설정의 **단일 진실 공급원**으로 사용
2. `.mcp.json`을 프로젝트 루트에 배치
3. 다른 프로젝트에서 심볼릭 링크로 참조

### 장점
- `~/.claude.json` 건드리지 않음
- Git으로 버전 관리 가능
- 원본 수정 시 모든 프로젝트에 즉시 반영
- 멱등성 보장 (링크 생성은 멱등)

### 단점
- 새 프로젝트마다 symlink 한 번 생성 필요
- 절대 경로 사용으로 머신 간 이식성 제한

### 프로젝트별 선택적 활성화

**MCP 서버 정의와 활성화 상태는 분리 저장된다:**

| 항목 | 저장 위치 | 공유 여부 |
|-----|----------|---------|
| MCP 서버 정의 | `.mcp.json` (symlink) | ✅ 모든 프로젝트 공유 |
| 활성화 상태 | `~/.claude.json` | ❌ 프로젝트별 독립 |

**`~/.claude.json` 내부 구조:**
```json
{
  "projects": {
    "/path/to/project": {
      "enabledMcpjsonServers": [],
      "disabledMcpjsonServers": ["github", "notion"]
    }
  }
}
```

**워크플로우:**
1. symlink로 `.mcp.json` 연결 → 모든 MCP 서버 "정의"가 공유됨
2. 프로젝트에서 `/mcp` 명령어 실행 → 필요한 서버만 선택적 활성화
3. 활성화 상태는 `~/.claude.json`에 프로젝트별로 저장

**효과:**
- 토큰 절약: 불필요한 MCP 도구 스키마 로딩 방지
- 컨텍스트 확보: MCP 전체 활성화 시 62.8k 토큰(31%) 소모 → 필요한 것만 켜면 절약
- [Issue #11085](https://github.com/anthropics/claude-code/issues/11085)에서 요청하는 "전역 기본값"의 수동 버전

### 사용법

```bash
# 다른 프로젝트에서 MCP 설정 연결
ln -sf /Users/jazzbach/projects/prompts/.mcp.json .mcp.json
```

### 파일 구조

```
prompts/                          # 이 프로젝트 (설정 중앙 저장소)
├── .mcp.json                     # MCP 서버 설정 (project scope)
└── docs/
    └── mcp-issue.md              # 이 문서

other-project/                    # 다른 프로젝트
└── .mcp.json -> ~/projects/prompts/.mcp.json  # symlink
```

## 결론

GitHub 이슈 조사 결과 (2026-01-12 기준):

### ✅ 좋은 소식: 우리 방식은 공식 지원됨

[Issue #5350](https://github.com/anthropics/claude-code/issues/5350)에서 Maintainer가 확인:
- **프로젝트 루트의 `.mcp.json`은 공식 지원 방법**
- 우리의 symlink 방식이 이와 정확히 일치
- 공식 문서: https://docs.anthropic.com/en/docs/claude-code/mcp#project-scope

### 우리 방식의 장점

- ✅ **공식 지원 방법** (project scope `.mcp.json`)
- ✅ 중앙 집중식 관리 가능
- ✅ 기존 런타임 데이터(`~/.claude.json`) 보존
- ✅ Git 버전 관리 가능
- ✅ 멱등성 보장

### 기대하기 어려운 것들

- ❌ `~/.claude/settings.json` 기반 MCP 설정 지원
- ❌ `claude mcp apply` 같은 선언적 명령어
- ❌ 시스템 레벨 전역 설정 파일
- ❌ 전역 MCP 기본값 enable/disable (많은 요청에도 미구현)

### 최종 판단

**symlink 방식은 공식 지원 방법을 활용한 최선의 대안**이며, Anthropic의 로드맵 변경 전까지 현재 방식 유지.
