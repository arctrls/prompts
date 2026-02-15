# FO-1282: CN 상점 구매 제한 기능 개선 PRD

## 📋 1. 프로젝트 개요

### 1.1 배경 및 목적
현재 CN 상점(197번)의 구매 제한 기능이  상점 제한 수량 기능만 구현되어 있습니다.
상품 그룹 제한 수량 기능을 추가하여 다양한 상품 그룹에 대한 유연한 제한 처리를 가능하게 합니다.

### 1.2 스코프 및 제약사항
- **스코프**: CN 상점(197) + 중국 배송지 + bros(yto) 배송방법 조건에서의 구매 제한
- **제약사항**: 기존 API 인터페이스 유지, 기존 테스트 케이스 호환성 보장

## 🎯 2. 비즈니스 요구사항

### 2.1 핵심 문제 정의
- 상품 그룹별 제한 처리 불가
- 구매 실패 시 구체적인 실패 사유 및 대안 정보 미제공

### 2.2 사용자 스토리
- **AS-IS**: 단순한 전체 수량 제한 (10개) + 모호한 실패 메시지
- **TO-BE**: 상품 그룹별 세분화된 제한 + 구체적인 실패 정보 (상품정보, 최대 구매 가능 수량)

### 2.3 성공 지표
- 다양한 상품 그룹 조합에 대한 유연한 제한 처리
- CS 문의 감소

## 🔧 3. 기능 명세서

### 3.1 현재 시스템 분석

#### 3.1.1 기존 CheckPurchaseLimitByShop 클래스
```java
// 현재 하드코딩된 로직
if (197L != principal.shopNo()) return Response.pass();
if (!"bros".equals(request.shippingMethodId())) return Response.pass();
final int shopLimit = 10; // 하드코딩된 제한수량
```

#### 3.1.2 현재 제한사항
- 상점별 단일 제한 수량 (10개)
- 상품 그룹별 세분화 불가

### 3.2 신규 기능 요구사항

#### 3.2.1 동적 제한 규칙 관리
- 상품 그룹별 제한 수량 설정 가능
- 상점 기본 제한 + 그룹별 제한 조합 처리

#### 3.2.2 복합 제한 로직 처리
- **상점 제한**: 전체 주문 수량 제한 (기본 10개)
- **그룹 제한**: 특정 상품 그룹 내 수량 제한
- **우선순위**: 단일 그룹 시 그룹 제한만 적용, 다중 그룹 시 상점 제한 적용

### 3.3 API 스펙

#### 3.3.1 기존 API 유지
```java
@QueryMapping("checkPurchaseLimitByShop")
public Response checkPurchaseLimitByShop(
    @Argument final Request request,
    @AuthenticationPrincipal final Principal principal
)
```

#### 3.3.2 Response 구조 확장
```java
public record Response(
    Boolean isPass,           // 통과 여부
    Integer limitQuantity,    // 제한 수량
    String limitType,         // 제한 타입: "SHOP_DEFAULT", "GROUP_LIMIT", "NOT_APPLICABLE"
    String message,           // 실패 시 메시지
    List<GroupLimitInfo> groupLimits, // 그룹별 제한 정보 (신규)
    List<ViolationDetail> violations  // 위반 상세 정보 (신규)
)

public record GroupLimitInfo(
    Long groupNo,            // 그룹 번호
    String groupName,        // 그룹명
    Integer currentQuantity, // 현재 수량
    Integer limitQuantity    // 제한 수량
)

public record ViolationDetail(
    Long goodsNo,                    // 상품 번호
    String goodsName,                // 상품명
    Integer currentQuantity,         // 현재 주문 수량
    Integer maxAllowedQuantity,      // 최대 구매 가능 수량
    String violationType,            // 위반 타입: "SHOP_LIMIT", "GROUP_LIMIT"
    Long groupNo,                    // 그룹 번호 (그룹 제한인 경우, nullable)
    String groupName                 // 그룹명 (그룹 제한인 경우, nullable)
)
```

### 3.4 비즈니스 룰

#### 3.4.1 기본 적용 조건
- CN 상점(197번)
- 배송지가 중국이면서 배송방법이 bros(yto)인 경우
- 알맹이 상품만 계산: `TUBE_YN != 'Y' AND GIFTS_KIND_CD == null`

#### 3.4.2 수량 계산 공식
```
totGoodsCnt = QTY × GOODS_PACK_CNT
GOODS_PACK_CNT: 패키지 안의 실제 상품 개수 (null인 경우 1로 처리)
```

#### 3.4.3 제한 적용 로직
1. **그룹 미설정 상품**: 상점 기본 제한 (10개) 적용
2**단일 그룹 주문**: 그룹 제한 수량만 적용
3**다중 그룹 주문**: 각 그룹별 제한 + 상점 전체 제한 모두 적용

#### 3.4.4 실패 정보 제공 로직
1. **상품별 제한 검증**: 각 상품이 속한 그룹의 제한 수량 확인
2. **최대 구매 가능 수량 계산**: 현재 주문에서 해당 상품의 최대 구매 가능 개수 산출
3. **상품명 조회**: Goods 도메인에서 사용자 친화적인 상품명 조회
4. **위반 정보 수집**: 실패한 상품들의 상세 정보를 ViolationDetail로 구성

## 🗄️ 4. 데이터 모델

### 4.1 테이블 스키마

#### 4.1.1 ORDER_QTY_LIMIT (그룹별 제한 마스터)
```sql
CREATE TABLE ORDER_QTY_LIMIT (
    QL_NO BIGINT PRIMARY KEY,           -- 그룹 고유번호
    DELIVERY_KIND_CD VARCHAR(20),       -- 배송방식 코드
    QL_NM VARCHAR(100),                 -- 그룹명
    LIMIT_QTY INT,                      -- 제한수량
    CMMT TEXT,                          -- 설명
    DEL_YN CHAR(1) DEFAULT 'N',         -- 삭제여부
    REG_USER_NO BIGINT,                 -- 등록자
    REG_DT DATETIME,                    -- 등록일시
    MOD_USER_NO BIGINT,                 -- 수정자
    MOD_DT DATETIME                     -- 수정일시
);
```

#### 4.1.2 ORDER_QTY_LIMIT_GOODS (그룹별 상품 매핑)
```sql
CREATE TABLE ORDER_QTY_LIMIT_GOODS (
    QL_NO BIGINT,                       -- 그룹번호 (FK)
    GOODS_NO BIGINT,                    -- 상품번호
    DEL_YN CHAR(1) DEFAULT 'N',         -- 삭제여부
    REG_USER_NO BIGINT,                 -- 등록자
    REG_DT DATETIME,                    -- 등록일시
    MOD_USER_NO BIGINT,                 -- 수정자
    MOD_DT DATETIME,                    -- 수정일시
    PRIMARY KEY (QL_NO, GOODS_NO)
);
```

### 4.2 도메인 모델

#### 4.2.1 핵심 도메인 객체
```java
// 구매 제한 그룹
public class PurchaseLimitGroup {
    private Long groupNo;
    private String deliveryKindCode;
    private String groupName;
    private Integer limitQuantity;
    private List<Long> goodsNumbers;
}

// 구매 제한 검증 결과
public class PurchaseLimitResult {
    private boolean isValid;
    private LimitType limitType;
    private Integer appliedLimit;
    private List<ViolationDetail> violations;
    private List<GroupLimitInfo> groupLimits;
}

// 상품별 위반 상세 정보
public class ViolationDetail {
    private Long goodsNo;
    private String goodsName;
    private Integer currentQuantity;
    private Integer maxAllowedQuantity;
    private ViolationType violationType; // SHOP_LIMIT, GROUP_LIMIT
    private Long groupNo;
    private String groupName;
}
```

### 4.3 데이터 흐름
1. **설정 조회**: 배송방법 코드로 해당 그룹 설정 조회
2. **상품 매핑**: 주문 상품들을 그룹별로 분류
3. **제한 검증**: 각 그룹별 + 상점 전체 제한 검증
4. **결과 반환**: 검증 결과 및 위반 정보 반환

## ⚙️ 5. 기술 구현 방안

## 🧪 6. 테스트 시나리오

### 6.1 단위 테스트

#### 6.1.1 PurchaseLimitService 테스트
```java
@DisplayName("단일 그룹 상품 주문 시 그룹 제한만 적용된다")
@Test
void single_group_order_applies_group_limit_only() {
    // 테스트 시나리오 구현
}

@DisplayName("다중 그룹 상품 주문 시 각 그룹별 제한과 상점 제한이 모두 적용된다")
@Test
void multiple_group_order_applies_both_group_and_shop_limits() {
    // 테스트 시나리오 구현
}

@DisplayName("그룹 제한 초과 시 실패 상품 정보가 반환된다")
@Test
void group_limit_exceeded_returns_violation_details() {
    // Given: 그룹1 제한 5개, 상품A(그룹1) 7개 주문
    // When: 제한 검증 수행
    // Then: 실패 + ViolationDetail 포함 (상품명, 현재 7개, 최대 5개)
}

@DisplayName("상품명 조회 실패 시 상품번호만 반환된다")
@Test
void goods_name_fetch_failure_returns_goods_number_only() {
    // Given: 상품명 조회 서비스 장애
    // When: 제한 검증 실패
    // Then: ViolationDetail에 goodsName null, goodsNo만 포함
}
```

### 6.3 엣지 케이스
- 그룹 설정이 없는 상품 주문
- 삭제된 그룹에 속한 상품 주문
- 제한 수량이 0인 그룹 주문
- 동시성 테스트 (동시 주문 처리)
- **상품명 조회 관련 엣지 케이스**:
  - 상품명 조회 서비스 장애 시 처리
  - 존재하지 않는 상품 번호에 대한 처리
  - 상품명 조회 타임아웃 시 처리
  - 부분적 상품명 조회 실패 시 처리


### 8 비즈니스 시나리오 예시

#### 8.1.1 Case 1: 상점 제한만 적용
```
주문: A1(그룹 미설정) 5개 + A2(그룹 미설정) 3개 = 8개
상점 제한: 10개 ✅ (8 ≤ 10)
결과: ✅ 구매 가능
```

#### 8.1.2 Case 2: 단일 그룹 + 상점 제한
```
주문: A1(그룹1) 3개 + A2(그룹1) 2개 = 5개
그룹1 제한: 7개 ✅ (5 ≤ 7)
결과: ✅ 구매 가능 (상점 제한 적용 안됨)
```

#### 8.1.3 Case 3: 다중 그룹 + 상점 제한
```
주문: A1(그룹1) 3개 + B1(그룹2) 5개 = 8개
그룹1 제한: 15개 ✅ (3 ≤ 15)
그룹2 제한: 20개 ✅ (5 ≤ 20)
상점 제한: 10개 ✅ (8 ≤ 10)
결과: ✅ 구매 가능
```
