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
- **상태: 미해결**

### [Issue #4976](https://github.com/anthropics/claude-code/issues/4976) - MCP 설정 파일 위치 문서화 오류
- 문서에서 `~/.claude/settings.json`에 MCP 설정 가능하다고 했으나 실제로는 무시됨
- `~/.claude.json`만 유효

### [Issue #6888](https://github.com/anthropics/claude-code/issues/6888) - MCP 스코프 저장 위치 불일치
- `claude mcp add --scope user` 명령어가 문서와 다른 위치에 저장
- User/Local 스코프 모두 `~/.claude.json`에 저장됨

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

공식적인 해결책이 나오기 전까지 **symlink 방식**이 가장 실용적인 대안이다. 완벽하지는 않지만:
- 중앙 집중식 관리 가능
- 기존 런타임 데이터 보존
- 버전 관리 가능

향후 Anthropic에서 `~/.claude/settings.json` 기반의 MCP 설정 지원이나, 별도의 전역 MCP 설정 파일을 제공하면 마이그레이션 예정.
