# GraphQL Controller Generator from Acceptance Test

Acceptance Test를 분석하여 GraphQL 컨트롤러 클래스를 자동으로 생성합니다.

## 작업 단계

1. **테스트 클래스 찾기**
    - 파라미터로 받은 테스트 클래스 이름으로 파일 검색
    - `src/test/java` 하위에서 `*AcceptanceTest.java` 패턴으로 검색
    - 찾지 못하면 예외 발생

2. **GraphQL 스키마와 Acceptance Test 분석**
    - GraphQL 쿼리 document에서 쿼리명 추출
    - `src/main/resources/graphql` 에서 해당 쿼리에 대한 Request 타입 추출
    - `.entity()` 호출에서 Response 타입 확인
    - 테스트 파일의 모든 nested record 추출

3. **컨트롤러 클래스 생성**
    - 위치: 테스트와 동일한 패키지의 `src/main/java` 경로
    - 클래스명: 테스트 클래스명에서 `AcceptanceTest` 제거
    - 어노테이션
        - `@Controller`
        - `@RequiredArgsConstructor`,
        - mutation api면 `@Transactional("hmmallTransactionManager")`
        - query api면 `@Transactional(value = "hmmallTransactionManager", readOnly = true)`

4. **Nested Record 생성**
    - `Request` record: GraphQL request 스키마와 타입과 필드가 일치하는 record 생성
    - `Response` record: 테스트의 `Response` 이동
    - 기타 DTO records: 테스트에 정의된 모든 record 이동

5. **메서드 생성**
    - 메서드명: GraphQL 쿼리명과 동일
    - 어노테이션: `@QueryMapping` 또는 `@MutationMapping` (쿼리 document 분석)
    - 파라미터: `@Argument final Request request`
    - 반환값: `Response` (초기값은 빈 리스트나 mock 데이터)
    - `// TODO: implement actual logic` 주석 포함

6. **테스트 파일 수정**
    - 모든 nested record 삭제
    - `.entity()` 호출을 컨트롤러 record 참조로 변경
        - 예: `.entity(Response.class)` → `.entity(PagedOrders.Response.class)`

## 컨트롤러 클래스 템플릿

```java
package com.ktown4u.thomas.order.

{subpackage};

import lombok.RequiredArgsConstructor;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Transactional(value = "hmmallTransactionManager", readOnly = true)
@Controller
@RequiredArgsConstructor
public class {ClassName}{

@QueryMapping
Response {methodName}(
@Argument final Request request){
        // TODO: implement actual logic
        return new

Response(
        List.of(),
            request.{field1}(),
        request.{field2}(),
        0
        );
        }

record Request( {
    Type1
} {field1},
        {Type2}{field2}
        ){}

record Response(
        List< {
    DtoName
}>content,
        {Type}field1,
        {Type}field2
    ){}

record {DtoName}(
        // 테스트 파일에서 추출한 모든 필드
        ){}
        }
```

## 주의사항

- Query는 `@QueryMapping`, Mutation은 `@MutationMapping` 사용
- Query API: `@Transactional(value = "hmmallTransactionManager", readOnly = true)` 사용
- Mutation API: `@Transactional("hmmallTransactionManager")` 사용
- 트랜잭션 매니저는 항상 `"hmmallTransactionManager"` 지정 필수
- 모든 import는 실제 사용되는 타입만 포함
- record의 필드 타입은 테스트와 스키마에 정의된 타입을 정확히 사용

## 예시

입력:

```
/controller PagedOrdersAcceptanceTest
```

출력:

- `src/main/java/com/ktown4u/thomas/order/legacyadmin/PagedOrders.java` 생성
- `src/test/java/com/ktown4u/thomas/order/legacyadmin/PagedOrdersAcceptanceTest.java` 수정
    - nested records 삭제
    - `.entity(PagedOrders.Response.class)` 로 변경

테스트 클래스 이름: $1 에 대한 GraphQL 컨트롤러를 생성합니다.

