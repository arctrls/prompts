# To ActionRunner Migration Command

특정 메서드에서 사용하는 레거시 액션들을 분석하여 ActionRunner에서 직접 처리할 수 있도록 마이그레이션합니다.

## 작업 단계

1. **주어진 메서드 분석**
   - 주어진 메서드 코드를 읽고 사용하는 액션 ID 목록 추출
   - 각 액션의 파라미터 구조 분석

2. **Mapper 메서드 확인**
   - 각 액션 ID에 대응하는 Mapper 메서드가 이미 존재하는지 확인
   - 없으면 액션 ID와 함계 예외 발생

3. **ActionRunInfo에 도우미 메서드 추가**
   - 각 액션의 파라미터를 추출하는 Record 타입 생성
   - `orderNos()` 패턴을 따르는 도우미 메서드 추가
   - 파라미터 이름을 camelCase로 변환

4. **ActionRunner에 액션 처리 로직 추가**
   - 각 액션 ID에 대한 if 블록 추가
   - 도우미 메서드를 활용하여 파라미터 추출
   - forEach를 사용하여 각 항목에 대해 Mapper 메서드 호출

## Record 타입 및 도우미 메서드 패턴

### Record 타입 명명 규칙
- 액션 ID의 핵심 기능을 반영한 이름 사용
- 예: `m_shop_goods_qty_edit` → `ShopGoodsQtyParam`

### 도우미 메서드 명명 규칙
- Record 타입 이름의 복수형 + camelCase
- 예: `ShopGoodsQtyParam` → `shopGoodsQtyParams()`

### 구현 예시

```java
// ActionRunInfo.java에 추가
public record ShopGoodsQtyParam(Long shopNo, Long goodsNo, Integer inQty) {}

public List<ShopGoodsQtyParam> shopGoodsQtyParams() {
    return parmsList.stream()
            .map(p -> new ShopGoodsQtyParam(
                    p.getLong("SHOP_NO"),
                    p.getLong("GOODS_NO"),
                    p.getInteger("IN_QTY")
            ))
            .toList();
}
```

## ActionRunner 처리 로직 패턴

### 기본 패턴 (단순 파라미터)

```java
// ActionRunner.java의 run() 메서드에 추가
if ("m_user_coup_sell_delete".equals(actionRunInfo.queryID)) {
    final List<Long> orderNos = actionRunInfo.orderNos();
    for (final Long orderNo : orderNos) {
        deleteMapper.deleteCouponUsage(orderNo);
    }
}
```

### 복잡한 파라미터 패턴

```java
if ("m_shop_goods_qty_edit".equals(actionRunInfo.queryID)) {
    actionRunInfo.shopGoodsQtyParams().forEach(param ->
            updateMapper.updateShopGoodsQuantity(
                    param.shopNo(),
                    param.goodsNo(),
                    param.inQty(),
                    null  // userId는 null로 전달
            )
    );
}
```

## 파라미터 이름 변환 규칙

- `SELL_NO` → `sellNo` 또는 `orderNo`
- `SELL_GOODS_NO` → `sellGoodsNo` 또는 `orderLineNo`
- `SELL_DADDR_NO` → `sellDaddrNo` 또는 `shippingNo`
- `SHOP_NO` → `shopNo`
- `GOODS_NO` → `goodsNo`
- `IN_QTY` → incomingQty`
- `INOUT_NO` → `inoutNo`
- `INOUT_CD` → `inoutCode`
- `REF_NO` → `referenceNo`
- `CMMT` → `comment`

## 주의사항

1. **기존 로직 검증**
   - ActionRunner에 이미 추가된 액션이 있는지 확인
   - 중복 추가 방지

2. **파라미터 매핑**
   - ActionManager에서 사용하는 파라미터 키와 Mapper 메서드의 파라미터 순서 일치 확인
   - null 처리가 필요한 파라미터 확인 (예: userId, modUserNo)

3. **테스트 고려사항**
   - 마이그레이션 후 기존 메서드를 통한 실행과 동일한 결과 보장
   - 파라미터 추출 로직의 null safety 확인

## 실행 예시

```
/migrate-action-to-runner ActionManager::setSellDeleteNoPaymentB2C
```

위 명령은 `ActionManager.setSellDeleteNoPaymentB2C` 메서드의 모든 액션을 분석하여 ActionRunner로 마이그레이션합니다.

---

메서드명: $1

