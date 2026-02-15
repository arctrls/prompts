---
description: C# Validation 로직을 FE/Java로 동기화
argument-hint: <C# 파일 경로> <대상 파일 경로>
allowed-tools: Read, Grep, Glob, Edit, Write, Task
---

# Validation Sync Workflow

C# Validation 로직을 FE(React) 및 BE(Java)로 동기화합니다.

## 입력 파라미터

| 파라미터 | 변수 | 필수 | 설명 |
|---------|------|-----|------|
| C# 파일 경로 | `$1` | 필수 | 원본 C# Validation 코드 위치 |
| 대상 파일 경로 | `$2` | 필수 | FE(.tsx) 또는 BE(.java) 파일 |

## Validation 매핑 패턴

### 1. 필수값 검증 (Required)

**C# 원본**:
```csharp
if (string.IsNullOrEmpty(rvw["FIELD_NAME"].ToString()))
{
    MessageBox.Show("필드명을 입력해주세요.");
    return false;
}
```

**Java 구현**:
```java
if (null == request.fieldName() || request.fieldName().isBlank()) {
    throw new IllegalArgumentException("필드명을 입력해주세요.");
}
```

**React 구현**:
```tsx
// React Hook Form
const schema = z.object({
  fieldName: z.string().min(1, '필드명을 입력해주세요.'),
});

// 또는 커스텀 Validation
const validate = (): string[] => {
  const errors: string[] = [];
  if (!data.fieldName?.trim()) {
    errors.push('필드명을 입력해주세요.');
  }
  return errors;
};
```

### 2. 숫자 범위 검증 (Range)

**C# 원본**:
```csharp
if (inQty < 0)
{
    if ((inQty * -1) > (requestQty + zeroQty))
    {
        row.SetColumnError("IN_QTY", "취소수량(-)은 배송요청 수량보다 클수 없습니다.");
    }
}
else if (inQty > maxQty)
{
    row.SetColumnError("IN_QTY", "추가수량이 최대 배송요청 가능 수량을 초과했습니다.");
}
```

**Java 구현**:
```java
final int inQty = item.inQty();
final int maxQty = item.maxRequestQty() + item.maxZeroQty();
final int currentQty = item.qty() + item.zeroQty();

if (inQty < 0) {
    final int cancelQty = Math.abs(inQty);
    if (cancelQty > currentQty) {
        throw new IllegalArgumentException(
            "취소수량(-)은 배송요청 수량보다 클 수 없습니다."
        );
    }
} else if (inQty > maxQty) {
    throw new IllegalArgumentException(
        "추가수량이 최대 배송요청 가능 수량을 초과했습니다."
    );
}
```

**React 구현**:
```tsx
const validateInQty = (item: GoodsItem): string | null => {
  const { inQty, qty, zeroQty, maxRequestQty, maxZeroQty } = item;
  const currentQty = (qty ?? 0) + (zeroQty ?? 0);
  const maxQty = (maxRequestQty ?? 0) + (maxZeroQty ?? 0);

  if (inQty < 0) {
    const cancelQty = Math.abs(inQty);
    if (cancelQty > currentQty) {
      return '취소수량(-)은 배송요청 수량보다 클 수 없습니다.';
    }
  } else if (inQty > maxQty) {
    return '추가수량이 최대 배송요청 가능 수량을 초과했습니다.';
  }

  return null;
};
```

### 3. 중복 검증 (Duplicate)

**C# 원본**:
```csharp
// 입력값 내 중복
var duplicates = table.DefaultView
    .Cast<DataRowView>()
    .GroupBy(r => r["TX_ID"].ToString())
    .Where(g => g.Count() > 1)
    .Select(g => g.Key);

if (duplicates.Any())
{
    MessageBox.Show($"거래ID가 중복되었습니다: {string.Join(", ", duplicates)}");
    return false;
}

// DB 중복
if (ActionManager.getTransIDCount(txId) > 0)
{
    MessageBox.Show("이미 존재하는 거래ID입니다.");
    return false;
}
```

**Java 구현**:
```java
// 입력값 내 중복
final Set<String> txIds = new HashSet<>();
final List<String> duplicates = new ArrayList<>();

for (final RefundItem item : items) {
    if (!txIds.add(item.transId())) {
        duplicates.add(item.transId());
    }
}

if (!duplicates.isEmpty()) {
    throw new IllegalArgumentException(
        "거래ID가 중복되었습니다: " + String.join(", ", duplicates)
    );
}

// DB 중복
final int count = getTransIDCount(txId);
if (count > 0) {
    throw new IllegalArgumentException("이미 존재하는 거래ID입니다.");
}
```

**React 구현**:
```tsx
const validateDuplicateTxId = (items: RefundItem[]): string | null => {
  const txIds = items.map(item => item.transId);
  const duplicates = txIds.filter((id, idx) => txIds.indexOf(id) !== idx);

  if (duplicates.length > 0) {
    return `거래ID가 중복되었습니다: ${[...new Set(duplicates)].join(', ')}`;
  }

  return null;
};

// DB 중복은 서버에서 검증 (mutation 호출 시 에러 반환)
```

### 4. 조건부 검증 (Conditional)

**C# 원본**:
```csharp
if (BaseRow["STATUS_CD"].Equals("delivery_ready"))
{
    // 배송준비중일 때만 특정 Validation
}
```

**Java 구현**:
```java
if (CODE_ID_DELIVERY_STATUS_DELIVERY_READY.equals(delivery.statusCd())) {
    // 조건부 Validation
}
```

**React 구현**:
```tsx
const validate = (data: FormData, status: string): string[] => {
  const errors: string[] = [];

  // 공통 Validation
  if (!data.field1) errors.push('필드1을 입력해주세요.');

  // 조건부 Validation
  if (status === 'delivery_ready') {
    if (!data.invoiceNo) errors.push('송장번호를 입력해주세요.');
  }

  return errors;
};
```

## 작업 단계

### 1단계: C# Validation 추출

`$1` 파일에서 다음 패턴 검색:
- `Validation()` 또는 `Validate()` 메서드
- `MessageBox.Show()` 에러 메시지
- `row.SetColumnError()` 필드 에러
- `return false` 검증 실패

### 2단계: Validation 매핑 테이블 생성

```
C# Validation                 →  대상 구현
──────────────────────────────────────────────────
필수값: FIELD_NAME            →  z.string().min(1)
범위: IN_QTY < 0              →  validateInQty()
중복: TX_ID                   →  validateDuplicateTxId()
조건부: STATUS_CD == 'ready'  →  if (status === 'ready')
```

### 3단계: 구현

대상 파일(`$2`)에 Validation 로직 추가:
- **FE(.tsx)**: 폼 제출 전 클라이언트 검증
- **BE(.java)**: 서비스 레이어에서 서버 검증

### 4단계: 검증

- [ ] 모든 Validation 케이스 매핑됨
- [ ] 에러 메시지 동일
- [ ] 검증 순서 동일 (중요한 경우)
- [ ] 경계값 테스트 통과

## 에러 표시 패턴

### FE (MUI + React Hook Form)

```tsx
<TextField
  {...register('fieldName')}
  error={!!errors.fieldName}
  helperText={errors.fieldName?.message}
/>
```

### FE (커스텀 에러 상태)

```tsx
const [errors, setErrors] = useState<Record<string, string>>({});

const handleSubmit = () => {
  const newErrors: Record<string, string> = {};

  if (!data.fieldName) {
    newErrors.fieldName = '필드명을 입력해주세요.';
  }

  if (Object.keys(newErrors).length > 0) {
    setErrors(newErrors);
    return;
  }

  // 저장 진행
};

return (
  <TextField
    value={data.fieldName}
    error={!!errors.fieldName}
    helperText={errors.fieldName}
  />
);
```

## 체크리스트

### 필수
- [ ] 모든 C# Validation 케이스 식별
- [ ] FE/BE 양쪽 구현 (이중 검증)
- [ ] 에러 메시지 일관성 유지
- [ ] null/undefined 안전 처리

### 권장
- [ ] BE는 최종 방어선 (모든 케이스 검증)
- [ ] FE는 UX 향상 (빠른 피드백)
- [ ] 에러 메시지 국제화 고려

## 관련 문서

- @docs/migration/delivery-tabs/04-goods/comparison-report.md - 수량 Validation
- @docs/migration/delivery-tabs/05-refund/comparison-report.md - 환불 Validation
