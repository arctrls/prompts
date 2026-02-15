---
description: FE 실시간 계산 로직 구현 (합계, 환율, 가격 계산 등)
argument-hint: <React 컴포넌트 경로> <계산 유형>
allowed-tools: Read, Grep, Glob, Edit, Write, Task
---

# Realtime Calculation Implementation

FE에서 실시간으로 값을 계산하는 로직을 구현합니다.

## 입력 파라미터

| 파라미터 | 변수 | 필수 | 설명 |
|---------|------|-----|------|
| React 컴포넌트 경로 | `$1` | 필수 | 대상 React 컴포넌트 |
| 계산 유형 | `$2` | 선택 | sum, exchange, price, weight 등 |

## 계산 유형별 구현 패턴

### 1. 합계 계산 (Sum)

**C# 원본 패턴**:
```csharp
foreach (DataRowView rvw in table.DefaultView)
{
    total += double.Parse(rvw["AMOUNT"].ToString());
}
```

**React 구현**:
```tsx
const total = useMemo(() => {
  return items.reduce((sum, item) => sum + (item.amount ?? 0), 0);
}, [items]);
```

### 2. 환율 계산 (Exchange Rate)

**C# 원본 패턴**:
```csharp
double wonAmt = Math.Round(amt * use_rate / baseAmt);
```

**React 구현**:
```tsx
const calculateWonAmount = useCallback((
  amount: number,
  useRate: number,
  baseAmt: number = 1
): number => {
  if (!amount || !useRate) return 0;
  return Math.round(amount * useRate / baseAmt);
}, []);

// 사용
const wonAmount = useMemo(() =>
  calculateWonAmount(amount, exchangeRate, baseAmount),
  [amount, exchangeRate, baseAmount]
);
```

### 3. 상품 가격 계산 (Price Calculation)

**C# 원본 (Expression)**:
```csharp
// SELL_WON_PRICE = (GD_REAL_WON_DC_PRICE - GD_COUPON_DC_WON_PRICE) * (QTY + ZERO_QTY + IN_QTY)
column.Expression = "(GD_REAL_WON_DC_PRICE - GD_COUPON_DC_WON_PRICE) * (QTY + ZERO_QTY + IN_QTY)";
```

**React 구현**:
```tsx
interface GoodsItem {
  gdRealWonDcPrice: number;
  gdCouponDcWonPrice: number;
  qty: number;
  zeroQty: number;
  inQty: number;
}

const calculateSellWonPrice = (item: GoodsItem): number => {
  const unitPrice = (item.gdRealWonDcPrice ?? 0) - (item.gdCouponDcWonPrice ?? 0);
  const totalQty = (item.qty ?? 0) + (item.zeroQty ?? 0) + (item.inQty ?? 0);
  return unitPrice * totalQty;
};

// DataGrid에서 사용
const columns: GridColDef[] = [
  {
    field: 'sellWonPrice',
    headerName: '판매가(원)',
    valueGetter: (params) => calculateSellWonPrice(params.row),
  },
];
```

### 4. 무게 계산 (Weight Calculation)

**C# 원본**:
```csharp
double tw = weight * (requestQty + zeroQty + inQty) * goodsPackCnt;
totalWeight += tw;
```

**React 구현**:
```tsx
const calculateTotalWeight = (item: GoodsItem): number => {
  const totalQty = (item.qty ?? 0) + (item.zeroQty ?? 0) + (item.inQty ?? 0);
  return (item.weight ?? 0) * totalQty * (item.goodsPackCnt ?? 1);
};

const totalWeight = useMemo(() =>
  items.reduce((sum, item) => sum + calculateTotalWeight(item), 0),
  [items]
);
```

## 실시간 업데이트 패턴

### useEffect를 사용한 파생 상태

```tsx
const [items, setItems] = useState<GoodsItem[]>([]);
const [totals, setTotals] = useState({ wonPrice: 0, weight: 0 });

useEffect(() => {
  const wonPrice = items.reduce((sum, item) => sum + calculateSellWonPrice(item), 0);
  const weight = items.reduce((sum, item) => sum + calculateTotalWeight(item), 0);
  setTotals({ wonPrice, weight });
}, [items]);
```

### useMemo를 사용한 계산 (권장)

```tsx
const totals = useMemo(() => ({
  wonPrice: items.reduce((sum, item) => sum + calculateSellWonPrice(item), 0),
  weight: items.reduce((sum, item) => sum + calculateTotalWeight(item), 0),
}), [items]);
```

### DataGrid 셀 편집 시 재계산

```tsx
const handleCellEditCommit = useCallback((params: GridCellEditCommitParams) => {
  const { id, field, value } = params;

  setItems(prev => prev.map(item => {
    if (item.id !== id) return item;

    const updated = { ...item, [field]: value };
    // 파생 필드 재계산
    updated.sellWonPrice = calculateSellWonPrice(updated);
    updated.totWeight = calculateTotalWeight(updated);
    return updated;
  }));
}, []);
```

## 구현 체크리스트

### 필수 항목
- [ ] 계산 함수 순수 함수로 구현
- [ ] useMemo로 불필요한 재계산 방지
- [ ] null/undefined 안전 처리 (nullish coalescing)
- [ ] 숫자 정밀도 처리 (Math.round, toFixed)

### 성능 최적화
- [ ] 대량 데이터 시 가상화 적용 (DataGrid virtualization)
- [ ] 디바운스 적용 (입력 필드)
- [ ] useCallback으로 핸들러 메모이제이션

### 테스트
- [ ] 경계값 테스트 (0, null, undefined)
- [ ] 큰 숫자 테스트 (오버플로우)
- [ ] 소수점 정밀도 테스트

## 에러 처리 패턴

```tsx
const safeCalculate = (value: number | null | undefined): number => {
  if (value == null || isNaN(value)) return 0;
  return value;
};

const calculateWithValidation = (a: number, b: number): number => {
  const safeA = safeCalculate(a);
  const safeB = safeCalculate(b);

  if (safeB === 0) {
    console.warn('Division by zero attempted');
    return 0;
  }

  return safeA / safeB;
};
```

## 관련 문서

- @docs/migration/delivery-tabs/04-goods/comparison-report.md - 배송상품 계산 로직
- @docs/migration/delivery-tabs/06-after-care/comparison-report.md - 환율 계산 로직
