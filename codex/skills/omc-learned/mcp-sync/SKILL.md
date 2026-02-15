---
name: mcp-sync
description: "프로젝트 .mcp.json 을 ~/.codex/config.toml의 [mcp_servers]로 동기화"
triggers:
  - mcp sync
  - mcp-sync
  - mcp 설정
  - omx mcp
argument-hint: "[--source <path>] [--target <path>] [--dry-run] [--apply] [--no-backup]"
---

# MCP 설정 동기화 - `mcp-sync`

이 스킬은 프로젝트의 `.mcp.json`(또는 지정한 JSON)에서 MCP 서버 정의를 읽어
`~/.codex/config.toml`의 `[mcp_servers.*]` 블록으로 동기화합니다.

- 기본 소스: 현재 경로 `.mcp.json`
- 기본 대상: `~/.codex/config.toml`
- 기본 동작은 **미리보기** (`--dry-run`), `--apply` 시에만 파일 쓰기
- **기존 MCP 중 동기화 대상(server)가 아닌 항목(예: omx 전용 MCP)** 은 유지

## 실행 워크플로

1. 소스 JSON에서 `mcpServers` 파싱
2. 대상 TOML에서 소스에 포함된 MCP 이름만 기존 섹션 제거
3. 소스 기반 신규 블록 생성
4. `--dry-run` 미리보기/`--apply` 적용
5. `--apply` 시 백업 파일 생성 (`--no-backup`으로 비활성화)

## 변환 규칙

- `command` + `args` → `[mcp_servers.name]`
- `env` → `[mcp_servers.name.env]`
- `url` → `[mcp_servers.name].url`
- `type: sse` + `url`은 `url` + `type`로 유지
- `headers`(또는 `http_headers`) → `[mcp_servers.name.http_headers]`

## 사용 예시

```bash
# 미리보기
~/.codex/skills/omc-learned/mcp-sync/mcp-sync.py --dry-run

# 프로젝트 기본 동기화
~/.codex/skills/omc-learned/mcp-sync/mcp-sync.py --apply

# 특정 파일에서 동기화
~/.codex/skills/omc-learned/mcp-sync/mcp-sync.py --source ../prompts/.mcp.json --apply
```

## 주의사항

- `source`에 없는 MCP는 기본적으로 기존 설정을 유지합니다.
- JSON에 없는 항목을 삭제하려면 대상 파일에서 직접 제거 후 `--apply` 하세요.
