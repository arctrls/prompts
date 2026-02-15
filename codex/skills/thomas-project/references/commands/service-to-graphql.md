---
description: Service 클래스를 GraphQL Controller로 변환 (테스트 포함)
argument-hint: <Service 클래스 경로>
---

# Service to GraphQL Controller 변환

기존 Service 클래스를 GraphQL Controller로 변환하고, 해당 테스트도 함께 GraphQL 테스트로 변환합니다.

## 입력 파라미터

| 파라미터 | 변수 | 필수 | 설명 |
|---------|------|------|------|
| Service 클래스 경로 | `$1` | 필수 | 변환할 Service 클래스의 전체 경로 |

## 작업 단계

### 1단계: 입력 검증 및 파일 분석

1. `$1` 파일 존재 여부 확인
2. Service 클래스 분석:
   - 클래스명, 패키지 확인
   - 주요 메서드 (save, create, update 등) 확인
   - 의존성 (다른 Service, Repository 등) 확인
   - 내부 Record (Request, Response 등) 확인
3. 해당 테스트 클래스 검색:
   - `src/test/java` 동일 패키지에서 `{클래스명}Test.java` 검색

### 2단계: GraphQL 스키마 확인/생성

1. `src/main/resources/graphql/` 에서 관련 스키마 검색
2. 스키마가 없으면 새로 생성해야 함을 알림:
   - Mutation 이름: 클래스명을 camelCase로 변환 (예: SaveDeliveryWrong → saveDeliveryWrong)
   - **Request 타입: `{MutationName}Request`** (Input이 아닌 Request 사용)
   - 반환 타입: Boolean 또는 Response record 기반

### 3단계: Service 클래스 → GraphQL Controller 변환

**핵심 원칙: 기존 Request record를 그대로 사용하고, 별도의 Input 클래스를 만들지 않는다.**

**변경 사항:**

1. 어노테이션 변경:
   - `@Service` → `@Controller`
   - `@TransactionalForLegacyOrder` → 메서드 레벨로 이동
   - `@RequiredArgsConstructor` 유지

2. GraphQL 메서드 추가 (기존 Request 직접 사용):
   ```java
   @AdminRoleRequired  // 관리자 권한 필요시
   @MutationMapping
   @TransactionalForLegacyOrder  // 트랜잭션 어노테이션은 메서드 레벨로
   public Boolean {mutationName}(@Argument("request") final Request request) {
       save(request);  // 기존 메서드 직접 호출
       return true;
   }
   ```

3. **별도의 Input 클래스나 변환 메서드를 만들지 않는다**
   - 기존 Request, SellCer, CancelProcess 등의 record를 그대로 사용
   - LocalDateTime 필드는 String으로 변경하여 GraphQL과 호환

4. 날짜/시간 타입 처리:
   - 내부 record (SellCer, CancelProcess 등)의 `LocalDateTime` → `String`으로 변경
   - GraphQL에서 String으로 받으면 Java에서도 String으로 처리

**코드 템플릿:**

```java
package com.ktown4u.thomas.order.legacyadmin.{subpackage};

import com.ktown4u.thomas.config.AdminRoleRequired;
import lombok.RequiredArgsConstructor;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.stereotype.Controller;

@Controller
@RequiredArgsConstructor
public class {ClassName} {
    // 기존 의존성 유지

    @AdminRoleRequired
    @MutationMapping
    @TransactionalForLegacyOrder
    public Boolean {mutationName}(@Argument("request") final Request request) {
        save(request);  // 기존 메서드 직접 호출 (변환 없음)
        return true;
    }

    // 기존 비즈니스 로직 메서드들 유지
    // 기존 Request, SellCer, CancelProcess 등 record 유지 (LocalDateTime → String 변경)
}
```

### 4단계: 테스트 클래스 → GraphQL 테스트 변환

**변경 사항:**

1. 어노테이션 추가/변경:
   ```java
   @WithMockUser
   @Transactional("hmmallTransactionManager")
   @ActiveProfiles("dev-test")
   @IntegrationTest
   @SpringBootTest
   @Import(TestConfig.class)
   @AutoConfigureGraphQlTester
   ```

2. GraphQlTester 주입:
   ```java
   @Autowired
   private GraphQlTester graphQlTester;
   ```

3. 테스트 메서드 변환:
   - 직접 서비스 호출 → GraphQL document 실행
   - Request 객체 생성 → Map<String, Object>로 GraphQL 변수 전달
   - **중첩 구조 반영**: Request 내부에 SellCer 등 중첩 record가 있으면 Map 내부에 중첩 Map으로 표현

**테스트 코드 템플릿:**

```java
@Test
@DisplayName("설명")
void test_name() {
    // Arrange - Mock 설정
    final Map<String, Object> sellCer = new HashMap<>();
    sellCer.put("sellCerNo", 946212L);
    sellCer.put("sellNo", 12345678L);
    // ... 기타 필드

    final Map<String, Object> request = new HashMap<>();
    request.put("sellDaddrNo", 40275137L);
    request.put("sellCer", sellCer);  // 중첩 구조
    // ... 기타 필드

    // Act
    graphQlTester
        .document("""
            mutation {mutationName}($request: {MutationName}Request!) {
                {mutationName}(request: $request)
            }
            """)
        .variable("request", request)
        .execute()
        .errors()
        .verify()
        .path("{mutationName}")
        .entity(Boolean.class)
        .isEqualTo(true);

    // Assert - 추가 검증
}
```

### 5단계: GraphQL 스키마 파일 생성/수정

`src/main/resources/graphql/mutation.graphqls` 에 추가:

**핵심: Java Request 구조를 그대로 반영하고, 이름은 Request로 통일**

```graphql
extend type Mutation {
    {mutationName}(request: {MutationName}Request!): Boolean!
}

# Request 구조를 그대로 반영
input {MutationName}Request {
    sellDaddrNo: ID!
    sellCerNo: ID!
    regUserNo: ID
    # ... 기타 필드
    sellCer: SellCerRequest!  # 중첩 record는 별도 input으로 정의
    goodsList: [DeliveryGoodsRequest!]
    addedCancelProcessList: [CancelProcessRequest!]
    # ... 기타 리스트 필드
}

# 중첩 record도 Request로 명명
input SellCerRequest {
    sellCerNo: ID!
    sellNo: ID!
    # ... 기타 필드 (LocalDateTime → String)
    refundDate: String
    returnDt: String
}

input DeliveryGoodsRequest {
    goodsNo: ID!
    qty: Int!
    sellNo: ID!
    sellGoodsNo: ID!
}

input CancelProcessRequest {
    sellCerNo: ID!
    processNo: ID
    processDate: String
    processComment: String
}

input CancelImageRequest {
    sellCerNo: ID!
    imgNo: ID
    imgPath: String
    dispOrd: Int
}
```

## 주의사항

1. **별도의 Input 클래스를 만들지 않는다**:
   - 기존 Request record를 그대로 GraphQL에서 사용
   - 변환 로직(convertToRequest 등)을 만들지 않음
   - 코드 중복과 유지보수 비용을 줄임

2. **Request 네이밍 규칙**:
   - GraphQL Input 타입명: `{MutationName}Request` (Input 아님)
   - 예: `SaveDeliveryWrongRequest`, `SellCerRequest`, `CancelProcessRequest`

3. **트랜잭션 관리**:
   - `@TransactionalForLegacyOrder`는 메서드 레벨로 이동
   - 클래스 레벨에서 제거

4. **권한 체크**:
   - 관리자 API의 경우 `@AdminRoleRequired` 어노테이션 필수

5. **타입 매핑**:
   - Java `LocalDateTime` → GraphQL `String` (record 내부에서 String으로 변경)
   - Java `BigDecimal` → GraphQL `BigDecimal` (기존 scalar 사용)
   - Java `List<Record>` → GraphQL `[TypeName]`

6. **Nullable 처리**:
   - GraphQL에서 느낌표(!)는 non-null을 의미
   - Java record 필드의 nullable 여부를 확인하여 스키마에 반영

7. **테스트 데이터**:
   - Map<String, Object>로 중첩 구조 표현
   - 헬퍼 메서드로 공통 데이터 생성 추출

## 예시

입력:
```
/service-to-graphql src/main/java/com/ktown4u/thomas/order/legacyadmin/delivery/SaveDeliveryWrong.java
```

출력:
1. `SaveDeliveryWrong.java` → GraphQL Controller로 변환 (Request 직접 사용)
2. `SaveDeliveryWrongTest.java` → GraphQL 테스트로 변환
3. `mutation.graphqls` 에 `SaveDeliveryWrongRequest` 스키마 추가

---

## 워크플로우 시작

**입력:** `$1`

입력이 없으면 변환할 Service 클래스 경로를 요청합니다.
