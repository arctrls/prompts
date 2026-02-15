---
description: Convert Approval Tests to AssertJ custom assertions in a test class
argument-hint: <test-class-name>
---

# Convert Approval Tests to AssertJ Custom Assertions

테스트 클래스 이름: `$1`

이 테스트 클래스에서 Approvals.verify()를 사용하는 테스트들을 AssertJ custom assertion으로 변환해주세요.

## 작업 단계

### 1. 분석 단계
- `$1` 이름으로 테스트 파일 찾기 (src/test/java/**/$1.java)
- 파일에서 Approvals.verify() 사용하는 테스트 메소드 모두 식별
- 각 테스트의 approved text 파일 찾아서 내용 읽기
- 검증 대상 객체의 타입과 필드 분석
- ShippingTest.java 파일에서 custom assertion 패턴 참조

### 2. Custom Assertion 설계
- 검증 대상 객체별로 custom assertion 클래스 설계
- ShippingTest 패턴을 따라:
  - Record 기반 Expected 데이터 클래스 (static factory method 포함)
  - AbstractAssert 확장한 assertion 클래스
  - containsExactly() 메소드로 필드별 검증 구현
  - 명확한 실패 메시지 제공

### 3. 구현 단계
- 테스트 클래스 내부에 custom assertion 클래스들 추가
- 각 테스트 메소드를 다음과 같이 변환:
  - `Approvals.verify(print(object))` → `assertThatXxx(object).containsExactly(...)`
  - Approved text 내용을 기반으로 expected 값 작성
- Static import 추가

### 4. 정리 단계
- Approvals, YamlPrinter 관련 import 제거
- print() 같은 헬퍼 메소드 제거
- 모든 approved text 파일 삭제 (`테스트클래스이름.테스트메소드이름.approved.txt`)

### 5. 추가 수정
- Custom assertion에서 사용하는 getter가 없다면 도메인 클래스에 추가
- 컴파일 에러 확인 및 수정

### 6. 검증
- 테스트 실행하여 모두 통과하는지 확인
- 변경사항을 git commit으로 저장

## 주의사항

- ShippingTest.java의 custom assertion 패턴을 반드시 참고할 것
- Record의 static factory method는 간결한 이름 사용 (예: `stock()`, `item()`)
- AssertJ의 AbstractAssert를 확장하여 fluent API 스타일 유지
- 각 필드 검증마다 명확한 에러 메시지 제공
- 불변 컬렉션 사용 (`.toList()`)
- 모든 테스트가 통과할 때까지 수정

## 참고 패턴 (ShippingTest)

```java
record ExpectedData(Type field1, Type field2) {
    static ExpectedData name(final Type field1, final Type field2) {
        return new ExpectedData(field1, field2);
    }
}

static class CustomAssert extends AbstractAssert<CustomAssert, TargetType> {
    CustomAssert(final TargetType actual) {
        super(actual, CustomAssert.class);
    }

    static CustomAssert assertThatTarget(final TargetType actual) {
        return new CustomAssert(actual);
    }

    CustomAssert containsExactly(final ExpectedData... expected) {
        isNotNull();
        // Size validation
        if (actual.items().size() != expected.length) {
            failWithMessage("Expected <%s> items but was <%s>",
                    expected.length, actual.items().size());
        }
        // Field-by-field validation
        for (int i = 0; i < expected.length; i++) {
            // Compare each field with clear error messages
        }
        return this;
    }
}
```

위 작업을 수행하고, 모든 테스트가 통과하면 변경사항을 커밋해주세요.
