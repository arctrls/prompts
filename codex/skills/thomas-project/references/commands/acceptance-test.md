---
description: GraphQL Query의 Acceptance Test 자동 생성
argument-hint: <query-name>
allowed-tools: Read, Write, Glob, Grep, Bash(mkdir:*)
---

# GraphQL Query Acceptance Test 생성

주어진 GraphQL 쿼리 이름에 대한 Acceptance Test를 자동 생성합니다.

**쿼리 이름**: `$1`

## 작업 절차

### 1단계: GraphQL 스키마 읽기

- `src/main/resources/graphql/query.graphqls` 파일 읽기
- 쿼리가 없으면 `src/main/resources/graphql/mutation.graphqls` 읽기
- 해당 쿼리/뮤테이션의 응답 타입 확인

### 2단계: 응답 타입 판별

- 배열 응답 [Type]: 배열 응답 템플릿 사용
- 객체 응답 Type: 객체 응답 템플릿 사용

### 3단계: 템플릿 기반 코드 생성

- 해당 템플릿의 필드명과 타입만 채워넣기
- 패키지: `com.ktown4u.thomas.order`
- 클래스명: `{QueryName}AcceptanceTest`
- 파일 경로: `src/test/java/com/ktown4u/thomas/order/{QueryName}AcceptanceTest.java`

## 응답 타입 매핑 규칙

### 배열 응답 [Type]

GraphQL 쿼리가 배열을 반환하는 경우:

- `.entityList(Response.class)` 사용
- `Response` record는 응답 타입의 필드를 **직접** 포함
- 별도의 wrapper나 List 필드 없음

**예시**: `code(request: CodeRequest): [CodeResponse]`

```java
.path("code")
.

entityList(Response .class)  // List<Response> 반환
.

get();

record Response(
        String code,      // CodeResponse의 필드
        String name       // CodeResponse의 필드
) {}
```

### 객체 응답 Type

GraphQL 쿼리가 단일 객체를 반환하는 경우:

- `.entity(Response.class)` 사용
- `Response` record는 응답 객체의 필드를 포함
- 중첩된 타입이 있으면 별도 record로 정의

**예시**: `pagedOrders(request: Request): PagedOrders`

```java
.path("pagedOrders")
.entity(Response.class)  // Response 반환
.get();

record Response(
    List<PagedOrderDto> content,  // PagedOrders의 필드
    Integer page,
    Integer size,
    Long totalElements
) {}

record PagedOrderDto(
    Long orderNo,
    String orderId,
    // ...
) {}
```

## 코드 템플릿

### 배열 응답 템플릿

```java
package com.ktown4u.thomas.order;

import com.ktown4u.thomas.utils.IntegrationTest;
import com.ktown4u.utils.YamlPrinter;
import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.graphql.tester.AutoConfigureGraphQlTester;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.graphql.test.tester.GraphQlTester;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@ActiveProfiles("dev-test")
@AutoConfigureGraphQlTester
@IntegrationTest
@SpringBootTest
class {QueryName}AcceptanceTest {
  @Autowired
  private GraphQlTester graphQlTester;

  @Transactional
  @Test
  void case0() {
    final var response = graphQlTester
            .document("""
                    query {queryName}($param: ParamType!) {
                        {queryName}(request: {
                            param: $param
                        }) {
                            field1
                            field2
                        }
                    }
                    """)
            .variable("param", Map.of(
                    "field", value
            ))
            .execute()
            .path("{queryName}")
            .entityList(Response.class)
            .get();

    Approvals.verify(YamlPrinter.print(response));
  }

  record Response(
          Type field1,
          Type field2
  ) {}
}
```

### 객체 응답 템플릿

```java
package com.ktown4u.thomas.order;

import com.ktown4u.thomas.utils.IntegrationTest;
import com.ktown4u.utils.YamlPrinter;
import org.approvaltests.Approvals;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.graphql.tester.AutoConfigureGraphQlTester;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.graphql.test.tester.GraphQlTester;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@ActiveProfiles("dev-test")
@AutoConfigureGraphQlTester
@IntegrationTest
@SpringBootTest
class {QueryName}AcceptanceTest {
    @Autowired
    private GraphQlTester graphQlTester;

    @Transactional
    @Test
    void case0() {
        final var response = graphQlTester
                .document("""
                    query {queryName}($param1: Type1, $param2: Type2) {
                        {queryName}(request: {
                            param1: $param1,
                            param2: $param2
                        }) {
                            field1
                            field2
                            nestedField {
                                nestedField1
                                nestedField2
                            }
                        }
                    }
                    """)
                .variable("param1", Map.of(
                        "field", value
                ))
                .variable("param2", defaultValue2)
                .execute()
                .path("{queryName}")
                .entity(Response.class)
                .get();

        Approvals.verify(YamlPrinter.print(response));
    }

    record Response(
            Type field1,
            Type field2,
            NestedType nestedField
    ) {}

    record NestedType(
            Type nestedField1,
            Type nestedField2
    ) {}
}
```

## 테스트 메서드 규칙

- 메서드명: `case0()`
- `@Transactional` 어노테이션 필수
- TODO 주석이나 예시 주석 절대 포함 금지
- 단일 기본 테스트 케이스만 생성

## 변수 바인딩 규칙

### ⚠️ 중요: 변수 타입 규칙

**Spring GraphQL Tester는 변수로 반드시 Map 타입을 요구합니다.**

- ❌ **절대 금지**: Record 객체나 Java 객체를 직접 사용
- ✅ **필수**: `Map.of()` 또는 `new HashMap<>()` 사용

**에러 발생 예시**:
```
Variable 'items' has an invalid value: Expected type 'Map' but was 'Record'.
Variables for input objects must be an instance of type 'Map'.
```

### 변수 전달 방법

#### 단일 객체 변수

```java
// ✅ 올바른 방법 - Map 사용
.variable("request", Map.of(
    "field1", value1,
    "field2", value2
))

// ❌ 잘못된 방법 - Record 객체 직접 사용 (컴파일 에러 발생)
.variable("request", new MyDto(value1, value2))
```

#### 리스트 변수

```java
// ✅ 올바른 방법 - List<Map> 사용
.variable("items", List.of(
    Map.of(
        "shopNo", 164L,
        "goodsId", "GD001",
        "qty", 1
    )
))

// ❌ 잘못된 방법 - List<Record> 사용 (런타임 에러)
.variable("items", List.of(
    new ItemDto(164L, "GD001", 1)
))
```

#### null 값 처리

null 값이 포함된 경우 `Map.of()` 대신 `HashMap` 사용:

```java
// null 값이 있는 경우
final Map<String, Object> item = new HashMap<>();
item.put("shopNo", 164L);
item.put("goodsId", "GD001");
item.put("retailPrice", null);  // null 허용

.variable("item", item)
```

또는 optional 필드는 생략:

```java
// ✅ optional 필드는 생략 가능
.variable("item", Map.of(
    "shopNo", 164L,
    "goodsId", "GD001"
    // retailPrice는 GraphQL 스키마에서 optional이므로 생략
))
```

### 기본값 선택 가이드

- **변수 선언**: GraphQL 쿼리에서 `$paramName: Type` 형식 사용
- **변수 바인딩**: `.variable("paramName", Map.of(...))` 사용
- **기본값 선택**: 합리적인 값 설정
  - 숫자: page=0, size=10
  - 문자열: 의미 있는 값
  - enum: 첫 번째 값 또는 가장 일반적인 값

## 검증 사항

- [ ] GraphQL 쿼리가 `query.graphqls` 또는 `mutation.graphqls`에 존재하는지 확인
- [ ] 응답 타입이 배열인지 객체인지 정확히 판별
- [ ] 올바른 템플릿 사용 (배열 응답 vs 객체 응답)
- [ ] 모든 필드가 response record에 포함되었는지 확인
- [ ] **변수 바인딩이 Map을 사용하는지 확인** (Record 객체 사용 금지)
- [ ] `import java.util.Map` 추가되었는지 확인

쿼리 `$1`에 대한 Acceptance Test를 생성합니다.
