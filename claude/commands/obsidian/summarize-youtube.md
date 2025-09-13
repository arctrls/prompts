---
argument-hint: "[youtube video url]"
description: "Youtube 영상의 트랜스크립트를 입력받아 번역, 정리해서 obsidian 문서로 저장"
color: yellow
---

# article summarize - $youtube_video_url

제공되는 트랜스크립트를 번역/정리해서 obsidian 문서를 생성합니다.

## 작업 프로세스

1. **메타데이터와 자막 추출**: `yt` 커멘드라인 유틸을 활용하여, 유튜브 URL에서 제목, 채널명, 업로드 날짜, 자막 등 메타데이터 추출
2. **내용 분석**: 자막 내용을 기반으로 번역 및 요약 수행
3. **태그 생성**: 내용과 메타데이터를 분석하여 hierarchical tags 생성 (add-tag.md 규칙 준수)
4. **파일명 자동 생성**: 영문 제목과 한국어 번역을 조합한 파일명 생성
5. **문서 저장**: yaml frontmatter를 포함한 obsidian 파일로 저장

```bash
$ yt --help
usage: yt [-h] [-l LANGUAGE] [-f {json,text}] [-o OUTPUT] [--metadata-only] url

YouTube 동영상의 메타데이터와 자막을 가져옵니다.

positional arguments:
  url                   YouTube 동영상 URL

options:
  -h, --help            show this help message and exit
  -l, --language LANGUAGE
                        자막 언어 코드 (기본값: en)
  -f, --format {json,text}
                        출력 형식 (기본값: text)
  -o, --output OUTPUT   출력 파일 경로 (지정하지 않으면 stdout으로 출력)
  --metadata-only       메타데이터만 가져오기 (자막 제외)

```

### 실행 단계별 설명

- TodoWrite 도구를 사용하여 각 단계의 진행 상황 추적
- 메타데이터 추출 실패 시 자막에서 제목 유추 시도
- 작성자 정보가 없으면 채널명을 author로 사용

## yaml frontmatter 예시

```yaml
id: 10 Essential Software Design Patterns used in Java Core Libraries
aliases: Java 코어 라이브러리에서 사용되는 10가지 필수 소프트웨어 디자인 패턴
tags:
  - patterns/design-patterns/java-implementation
  - patterns/creational/factory-singleton-builder
  - patterns/structural/adapter-facade-proxy
  - patterns/behavioral/observer-strategy-template
  - java/core-libraries/design-patterns
  - frameworks/java/standard-library
  - development/practices/object-oriented-design
  - architecture/patterns/gof-patterns
author: ali-zeynalli
created_at: 2025-09-04 11:39
related: []
source: https://azeynalli1990.medium.com/10-essential-software-design-patterns-used-in-java-core-libraries-bb8156ae279b
```

- id: 문서에서 발견한 제목
- aliases: 문서에서 발견한 제목의 한국어 번역
- author: 채널명 또는 발표자 이름 (소문자, 공백은 '-'로 변경)
- created_at: obsidian 파일 생성 시점 (현재 시각)
- source: 문서 url

## 문서 번역 및 요약 규칙

```
Target Audience:
- Obtained a Computer Science degree and a master's degree in Korea
- Has worked as a software developer for over 25 years, developing and maintaining various services and products
- Cannot quickly read or watch content in English
- Interested in sustainable software system development, OOP, developer capability enhancement, Java, TDD, Design Patterns, Refactoring, DDD, Clean Code, Architecture (MSA, Modulith, Layered, Hexagonal, vertical slicing), Code Review, Agile (Lean) Development, Spring Boot, building development organizations and improving development culture, developer growth, and coaching
- Enjoys studying and organizing related topics for use in work and lectures

Translation Guidelines:
- Translate the input text to Korean
- For technical terms and programming-related concepts, include the original English term in parentheses when first mentioned
- Include as many original English terms as possible
- Prioritize literal translation over free translation, but use natural Korean expressions
- Use technical terminology and include code examples or diagrams when necessary
- Explicitly mark any uncertain parts

Summarization Structure:
1. Highlights/Summary: Summarize the entire content in 2-3 paragraphs
2. Detailed Summary: Divide the content into sections of about 5 minutes each, and summarize each section in 2-3 detailed paragraphs
3. Conclusion and Personal Views: Summarize the entire content in 5-10 statements and provide insights on why this information is important

Precautions:
- Explicitly mark any uncertainties in the translation and summarization process
- Use accurate and professional terminology as much as possible
- Balance the content of each section to avoid being too short or too long
- Include actual code examples or pseudocode to make explanations more concrete
- Explain complex concepts using analogies or examples for easier understanding
- Clearly state when you don't know certain information
- Self-verify the final information before responding
- Include all example codes in the document without omission

## 메타데이터 추출 가이드

WebFetch 사용 시 다음 프롬프트로 유튜브 페이지에서 메타데이터를 추출하세요:
```

이 유튜브 페이지에서 다음 정보를 추출해주세요:

1. 영상 제목 (정확한 원문)
2. 채널명 (업로더)
3. 업로드 날짜
4. 영상 길이
5. 조회수
6. 영상 설명 (처음 2-3줄)

JSON 형태로 정리해서 반환해주세요.

```

## 파일명 생성 규칙

- 형식: `{영문제목} - {한국어번역}.md`
- 영문제목이 너무 길면 핵심 키워드로 축약
- 특수문자는 공백이나 하이픈으로 변경
- 예시: `Teaching Event Sourcing is Hard - Event Sourcing 교육의 어려움.md`

## 태그 가이드라인

- 6-10개 내외 (내용의 복잡성에 따라 조정)
- add-tag.md의 hierarchical tagging 규칙 준수
- 영상의 주요 주제, 기술 스택, 도메인, 패턴 등을 포괄

When you have completed the translation and summarization, present your work in the following artifact style format:

<translation_and_summary>
<highlights>
[Insert 2-3 paragraphs summarizing the entire content]
</highlights>

<detailed_summary>
[Insert detailed summary divided into sections, with 2-3 paragraphs for each section]
</detailed_summary>

<conclusion_and_views>
[Insert 5-10 summary statements and insights on the importance of the information]
</conclusion_and_views>
</translation_and_summary>

Remember to adhere to all the guidelines and precautions mentioned above throughout your translation and summarization
process.
```
