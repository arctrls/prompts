# FO-1264 CN 상점 구매제한수량 GraphQL API 개발 진행 과정

## 1. FO-1264 API stub 개발

### 1-1. 초기 개발 요청
**사용자 요청**: FO-1264.md 기반으로 API stub 개발, 테스트 코드 먼저 작성(TDD), 컨벤션 유지, 계획 수립 요청

**수행 작업**: 
- FO-1264.md 파일 분석 및 기존 코드베이스 구조 파악
- 개발 계획 수립 후 사용자 승인 획득

### 1-2. API stub 구현
**사용자 요청**: 계획 승인 후 개발 시작

**수행 작업**:
- GraphQL 스키마 정의 (`query.graphqls`에 checkPurchaseLimitByShop 추가)
- 테스트 코드 작성 (`CheckPurchaseLimitByShopTest.java`)
- Controller 구현 (`CheckPurchaseLimitByShop.java` - stub으로 상점 기본 제한 10개 반환)
- 컴파일 검증 완료

### 1-3. 프로세스 문서 개선
**사용자 요청**: 사용자 명령과 수행 작업을 요약하여 넘버링 구조로 개선

**수행 작업**: 요청-응답 단위로 프로세스 문서 재구성 및 요약

### 1-4. GraphQL 테스트 오류 수정
**사용자 요청**: 테스트 실행 시 GraphQL 변수 타입 오류 발생, API 스펙에서 `request` 네이밍 유지

**수행 작업**: 
- 테스트 코드 변수 전달 방식 수정 (Record 객체 → 직접 값 삽입)
- GraphQL 쿼리에서 변수 사용 대신 직접 값 포맷팅 방식 적용
- 테스트 성공 확인

### 1-5. shopNo 197 상점 전용 로직 추가
**사용자 요청**: CN 상점(197번)이 아니라면 무조건 true 반환하는 로직 필요, @AuthenticationPrincipal UserId 파라미터 추가, 테스트 코드 먼저 작업

**수행 작업**:
- 기존 테스트에 CN 상점(197번) Mock 사용자 설정 추가
- 다른 상점(164번) 테스트 케이스 추가 - 무조건 통과 검증
- Controller에 UserId 파라미터 추가 및 shopNo 검증 로직 구현
- 모든 테스트 통과 확인

---
**현재 상태**: shopNo별 분기 로직 완료, CN 상점(197번)만 실제 검증, 다른 상점은 무조건 통과, 실제 비즈니스 로직 구현 대기