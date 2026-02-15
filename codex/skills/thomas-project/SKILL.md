---
name: thomas-project
description: Thomas 프로젝트 전용 규칙/워크플로우(.claude + CLAUDE.md + AGENTS.md)를 Codex에서 사용한다. PR 리뷰, 레거시 마이그레이션, SQL 이관, validation 동기화 요청에 사용.
---

# Thomas Project Skill

이 스킬은 thomas 프로젝트 전용 규칙을 Codex에서 재사용하기 위한 호환 레이어다.

## Load order

1. `references/AGENTS.md`
2. `references/CLAUDE.md`
3. 요청 유형별로 `references/commands/*.md` 또는 `references/pr-review-guide.md`

## Rules

- 리뷰/PR 문맥은 한국어로 작성
- 레거시 마이그레이션 시 C# 대비 동등성 유지
- SQL 파라미터는 null이어도 항상 바인딩
- 통합 테스트는 `./gradlew integrationTest --tests <ClassOrMethod>` 우선 사용
