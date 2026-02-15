# Project Description

- Java backend system for shopping cart and order domains

# PR Review Guide

- PR 리뷰 시 [.claude/pr-review-guide.md](./.claude/pr-review-guide.md) 참조

# Language Requirement

- All PR reviews must be written in Korean (한글).
- `@"IntegrationTest` annotation이 붙은 테스트는 다음과 같이 실행해. 기억해.

./gradlew integrationTest --tests {{test-class-or-method}}

# C# BO Reference

- `bo/` (심볼릭 링크) — C# BO의 SQL 쿼리가 실행되는 Java 웹 백오피스 프로젝트
- 기술 스택: Spring 3.2 / MyBatis 3.2 / Java 8 / MariaDB
- SQL 매퍼: `bo/src/main/resources/sql/mybatis/mapper/*.xml`
- Action 시스템: `bo/src/main/java/com/hm/action/`
  - **Action** → 단일 DB 작업 (actionID = MyBatis 쿼리 ID)
  - **ActionSet** → 여러 Action의 트랜잭션 단위
  - **ActionRunner** → MyBatis로 Action 실행
- Action ID 규칙: `m_xxx_merge`(upsert), `m_xxx_find_paging`(조회), `m_xxx_edit`(수정), `m_xxx_delete`(삭제)
- C# → Java 타입: `DataSet`→`ResultSet`, `DataTable`→`ResultTable`, `DataRow`→`MapExt`

# SQL 파라미터 바인딩 규칙 (MUST)

Action 기반 코드에서 SQL 쿼리를 호출할 때 반드시 지켜야 할 규칙:

1. **파라미터 대조 필수**: SQL 쿼리의 모든 `:PARAM`을 Java `parms.put("PARAM", ...)`과 대조할 것
2. **조건문 금지**: `if (value != null) parms.put(...)` 패턴 사용 금지 → SQL 바인딩 실패
3. **null 허용**: SQL에서 사용하는 파라미터는 값이 null이어도 반드시 등록

```java
// ❌ 잘못된 예시 (런타임 오류 발생)
if (request.adminComment() != null) {
    parms.put("ADMIN_COMMENT", request.adminComment());
}

// ✅ 올바른 예시 (null도 등록)
parms.put("ADMIN_COMMENT", request.adminComment());
```

4. **검증 방법**: 컴파일 성공 ≠ 런타임 성공. `/sql-param-verify` 스킬로 파라미터 대조 검증
5. **오류 메시지**: `No value supplied for the SQL parameter 'XXX'` → 해당 파라미터 누락
