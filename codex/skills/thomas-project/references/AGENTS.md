# Thomas Codex Agent Guide

이 문서는 이 저장소에서 Codex(및 AGENTS.md를 읽는 에이전트)가 따라야 할 기본 작업 규칙이다.

## 1) 프로젝트 요약

- 서비스: KTOWN4U 주문 백엔드 (`thomas`)
- 스택: Java 25, Spring Boot 4, GraphQL, JPA + MyBatis, MySQL, Redis, Kafka
- 구조: `src/main/java/com/ktown4u/thomas/order/*` 중심의 package-by-feature

## 2) 먼저 읽을 파일

- 전반 규칙: `CLAUDE.md`
- 실행/환경: `README.md`
- 마이그레이션 특화: `docs/migration/AGENTS.md`, `docs/migration/CLAUDE.md`
- PR 리뷰 기준: `.claude/pr-review-guide.md`
- 도메인 문서 인덱스: `docs/README.md`

## 3) 자주 쓰는 명령

- 의존 서비스 실행: `docker compose up -d`
- 앱 실행: `./gradlew bootRun`
- 단위 테스트: `./gradlew test`
- 통합 테스트: `./gradlew integrationTest`
- 단일 통합 테스트: `./gradlew integrationTest --tests <ClassOrMethod>`

## 4) 코드 작업 규칙

- 기존 기능 변경 시 동작 보존을 최우선으로 한다.
- Java 코드에서 `final` 사용, guard clause, 명확한 null 처리 원칙을 유지한다.
- 테스트 `@DisplayName`은 한국어를 유지한다.
- GraphQL 변경 시 스키마(`src/main/resources/graphql/*.graphqls`)와 테스트를 같이 갱신한다.
- 불필요한 대규모 리포맷/정렬 변경은 피하고, 필요한 파일만 최소 수정한다.

## 5) 테스트/검증 규칙

- 변경 범위에 맞는 테스트를 직접 실행하고 결과를 보고한다.
- DB 변경(Flyway, MyBatis, JPA) 시 최소 1개 이상의 회귀 테스트를 같이 확인한다.
- 실패한 테스트가 있으면 로그 핵심 원인과 재현 명령을 함께 남긴다.

## 6) 리뷰/PR 작성 규칙

- 기본 언어는 한국어.
- 요약보다 결함 가능성(트랜잭션 누락, NPE, NumberFormatException, 경계값/예외 테스트 부족)을 우선 점검한다.
- "리팩토링" 표현은 기능 변경이 전혀 없을 때만 사용한다.

## 7) 레거시 마이그레이션 작업

- C# BO 대응 작업은 반드시 `docs/migration/AGENTS.md`를 우선 적용한다.
- 핵심 원칙:
  - C#과 1:1 추적 가능한 메서드/흐름 유지
  - 저장 API는 "변경 필드만"이 아니라 "원본 전체 + 변경 필드 덮어쓰기" 패턴 유지
  - SQL 파라미터는 null이어도 반드시 바인딩(조건부 `parms.put` 금지)

