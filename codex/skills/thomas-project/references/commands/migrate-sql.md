---
description: MyBatis 레거시 SQL을 현재 프로젝트의 매퍼로 이관
argument-hint: [ 쿼리 ID ]
allowed-tools: Grep, Read, Edit, Write, mcp__serena__*
---

# MyBatis Legacy SQL Migration Command

주어진 쿼리 ID에 해당하는 레거시 SQL을 `./related-projects/bo/src/main/resources/sql/mybatis/mapper` 디렉토리에서 찾아서 현재 프로젝트의
`src/main/resources/sql` 디렉토리로 이관합니다.

## 실행 모드

**자동 실행 모드**: 사용자가 쿼리 ID만 제공하면 모든 단계를 자동으로 실행하고 결과만 보고합니다.

## 입력

- 쿼리 ID: `$ARGUMENTS`
- 쿼리 ID가 제공되지 않은 경우 사용자에게 입력 요청 후 중단

## 작업 단계

모든 단계를 자동으로 실행하고, 완료 후 사용자에게 결과만 보고합니다.

### 1단계: 레거시 SQL 검색 및 XML 파일 결정

1. Grep으로 `bo/src/main/resources/sql/mybatis/mapper` 에서 쿼리 ID 검색 (`id="$ARGUMENTS"` 패턴)
2. 검색 실패 시: "레거시 디렉토리에서 쿼리 ID '$ARGUMENTS'를 찾을 수 없습니다" 알림 후 중단
3. 검색 성공 시: 원본 XML 파일명 확인 (예: `mall.admin.sell.xml`)

### 2단계: 타겟 XML 파일 결정

1. 원본 파일명에서 타겟 XML 파일 경로 생성
   - 원본: `bo/src/main/resources/sql/mybatis/mapper/mall.admin.sell.xml`
   - 타겟: `src/main/resources/sql/mall.admin.sell.xml`
2. 타겟 파일이 없으면 생성, 있으면 기존 파일 사용

### 2.5단계: 타겟 파일에서 중복 확인

1. 타겟 XML 파일에서 동일한 쿼리 ID 검색 (`id="$ARGUMENTS"` 패턴)
2. 중복 발견 시: "타겟 파일에 이미 쿼리 ID '$ARGUMENTS'가 존재합니다" 알림 후 중단
3. 중복이 없으면 3단계로 진행

### 3단계: SQL 쿼리 추출 및 복사

1. 원본 XML에서 쿼리 ID에 해당하는 전체 `<select>`, `<insert>`, `<update>`, 또는 `<delete>` 태그 추출
2. 완전한 시작 태그부터 닫는 태그까지 모든 내용 포함
3. 여러 라인에 걸친 쿼리도 정확하게 추출
4. 타겟 XML 파일의 `</mapper>` 태그 바로 앞에 추가
5. 기존 파일의 들여쓰기 스타일 유지 (탭 사용)

### 4단계: 결과 보고

사용자에게 다음 정보 제공:
- 추가된 쿼리 ID
- 원본 파일 경로
- 타겟 파일 경로
- 추가된 라인 범위

## 주의사항

- **쿼리 내용 변경 금지**: 원본 쿼리를 그대로 복사만 합니다
- **들여쓰기 유지**: 타겟 파일의 기존 들여쓰기 스타일(탭) 유지
- **중복 확인**: 타겟 파일에 동일한 쿼리 ID가 이미 존재하면 사용자에게 알림 후 작업 중단

## 예시

### 실행 예시

```
사용자: /migrate-sql m_sell_by_sell_daddr_id

AI 실행:
1. bo/src/main/resources/sql/mybatis/mapper/mall.admin.sell.xml 에서 쿼리 검색
2. src/main/resources/sql/mall.admin.sell.xml 파일 확인
3. 타겟 파일에서 중복 확인
4. 쿼리 추출 및 추가
5. 결과 보고
```

### 결과 보고 형식

```
쿼리 이관 완료:
- 쿼리 ID: m_sell_by_sell_daddr_id
- 원본: bo/src/main/resources/sql/mybatis/mapper/mall.admin.sell.xml
- 타겟: src/main/resources/sql/mall.admin.sell.xml (188-197라인)
```

---

쿼리 ID: `$ARGUMENTS` 에 대한 이관을 시작합니다.
