---
description: C# XAML UI 로직을 React 컴포넌트로 마이그레이션
argument-hint: <C# 파일 경로> <대상 React 컴포넌트 경로>
allowed-tools: Read, Grep, Glob, Edit, Write, Task
---

# FE Migration Workflow

C# XAML/Code-Behind의 UI 로직을 React 컴포넌트로 마이그레이션합니다.

## 입력 파라미터

| 파라미터 | 변수 | 필수 | 설명 |
|---------|------|-----|------|
| C# 파일 경로 | `$1` | 필수 | 원본 C# XAML 또는 xaml.cs 파일 |
| React 컴포넌트 경로 | `$2` | 필수 | 대상 React 컴포넌트 파일 |

## 마이그레이션 원칙

### 1. UI 요소 매핑

| C# (DevExpress) | React (MUI) |
|-----------------|-------------|
| `TextEdit` | `TextField` |
| `CodeComboBox` | `Select` / `Autocomplete` |
| `CheckEdit` | `Checkbox` / `Switch` |
| `GridControl` | `DataGrid` |
| `DateEdit` | `DatePicker` |
| `SpinEdit` | `TextField type="number"` |
| `ButtonEdit` | `Button` |
| `SimpleButton` | `Button` |
| `GroupBox` | `Box` / `Paper` / `Card` |

### 2. 이벤트 핸들러 매핑

| C# 이벤트 | React 핸들러 |
|----------|-------------|
| `_Click` | `onClick` |
| `_EditValueChanged` | `onChange` |
| `_LostFocus` | `onBlur` |
| `_GotFocus` | `onFocus` |
| `_KeyDown` | `onKeyDown` |
| `_ColumnChanged` | DataGrid `onCellEditCommit` |
| `_InitNewRow` | 별도 초기화 로직 |

### 3. 데이터 바인딩 패턴

**C# (DataRowView)**:
```csharp
rvw["FIELD_NAME"] = value;
txtField.EditValue = BaseRow["FIELD_NAME"];
```

**React (useState + props)**:
```tsx
const [localData, setLocalData] = useState(props.data);
const handleChange = (field: string, value: any) => {
  setLocalData(prev => ({ ...prev, [field]: value }));
};
```

## 작업 단계

### 1단계: C# 파일 분석

`$1` 파일에서 다음 항목 추출:

1. **UI 컴포넌트 목록**: XAML에서 사용된 컨트롤
2. **이벤트 핸들러**: xaml.cs의 이벤트 메서드
3. **데이터 바인딩**: EditValue, SelectedItem 등 바인딩
4. **Validation 로직**: 필드 검증 코드
5. **조건부 렌더링**: Visibility, IsEnabled 로직

### 2단계: 매핑 테이블 생성

```
C# UI 요소                    →  React 컴포넌트
──────────────────────────────────────────────
txtFieldName (TextEdit)       →  <TextField name="fieldName" />
cboCategory (CodeComboBox)    →  <Select name="category" />
chkEnabled (CheckEdit)        →  <Checkbox name="enabled" />
```

### 3단계: React 컴포넌트 구현

1. **Props 인터페이스 정의**: C# 데이터 구조 → TypeScript interface
2. **State 관리**: useState 또는 useForm
3. **이벤트 핸들러 구현**: C# 로직 → TypeScript 함수
4. **조건부 렌더링**: C# Visibility → JSX 조건문
5. **Validation**: C# Validation → React Hook Form 또는 커스텀

### 4단계: 검증

- [ ] 모든 UI 요소가 매핑됨
- [ ] 모든 이벤트 핸들러가 구현됨
- [ ] 데이터 바인딩 정상 동작
- [ ] Validation 로직 동일
- [ ] 조건부 표시/숨김 동일

## 특수 케이스 처리

### GridControl → DataGrid

```tsx
// C#: grdList_CustomUnboundColumnData
// React: DataGrid columns with valueGetter
const columns: GridColDef[] = [
  {
    field: 'rowNum',
    headerName: '순번',
    valueGetter: (params) => params.api.getRowIndexRelativeToVisibleRows(params.row) + 1,
  },
];
```

### CodeComboBox → Select with Options

```tsx
// C#: cboField.ItemsSource = CODE_KIND_XXX
// React: Select with options from props or constants
<Select value={value} onChange={handleChange}>
  {options.map(opt => (
    <MenuItem key={opt.code} value={opt.code}>{opt.name}</MenuItem>
  ))}
</Select>
```

### BaseRow 공유 패턴

```tsx
// C#: 여러 탭이 BaseRow 공유
// React: 부모에서 deliveryDetailRaw를 props로 전달
interface TabProps {
  deliveryDetailRaw: DeliveryDetailRaw;
  onSave: (data: Partial<DeliveryInfo>) => Promise<void>;
}
```

## 체크리스트

- [ ] C# UI 요소 → React 컴포넌트 매핑 완료
- [ ] 이벤트 핸들러 1:1 매핑 완료
- [ ] 데이터 바인딩 패턴 적용
- [ ] Validation 로직 이관
- [ ] 조건부 렌더링 구현
- [ ] TypeScript 타입 정의
- [ ] 저장 API 연동 (mutation)

## 관련 문서

- @docs/migration/CLAUDE.md - Migration 가이드라인
- @docs/migration/delivery-tabs/*.md - 탭별 분석 보고서
