# ANCHORS OFF·DUTY 브랜드 페이지

쉬는 날에도 차려입는 40대 남성을 위한 모자·의류 브랜드의 **고객용** 공식 페이지.
GitHub Pages로 `main` 브랜치 루트를 그대로 배포한다 → https://yahr.github.io/anchors-offduty/

## 구조

| 파일 | 내용 |
|---|---|
| `index.html` | 페이지 전체 (CSS·JSON-LD 인라인). 섹션: concept → story → product → symbol → lookbook → faq |
| `404.html` | GitHub Pages 404 |
| `llms.txt`, `robots.txt`, `sitemap.xml` | AI·검색 크롤러용 |
| `img/` | 제품·착용 이미지(AI 제작), 로고 SVG |
| `scripts/check.py` | 페이지 검사 |
| `scripts/capture.py` | 화면 캡처 (AS-IS / TO-BE) |

빌드 단계 없음. 로컬 미리보기: `python3 -m http.server 8000` → http://localhost:8000

## 콘텐츠 원칙 (고객용)

- 내부 자료를 넣지 않는다: 시장 조사 수치(무신사 랭킹·리뷰), 가격 기준선, 타사 리뷰 인용, 생산 규격(mm 치수·선 굵기·백킹·스티치), 기획 리포트 링크, "타겟" 같은 기획 용어.
  `scripts/check.py`가 이 표현을 잡아낸다. 새 금지 표현이 생기면 스크립트의 `FORBIDDEN`에 더한다.
- 이미지 안내 한 문장은 실제 제품 사진으로 바꾸기 전까지 지우지 않는다 (AI 제작 이미지를 실물로 오해하지 않게).
- 아직 판매 전이다. 구매·가격·출시일을 약속하는 문구를 넣지 않는다.
- 섹션 배경은 밝음(`class="light"`)과 어두움을 번갈아 둔다. 섹션을 넣거나 빼면 순서를 다시 맞춘다.
- 본문을 바꾸면 같은 내용이 들어 있는 JSON-LD(FAQ·라인업), `meta description`, `llms.txt`도 함께 맞춘다.

## 작업 순서

1. 브랜치에서 작업하고 PR로 `main`에 합친다. `main`에 직접 푸시하지 않는다.
2. 화면이 바뀌는 작업이면 고치기 전에 `python3 scripts/capture.py asis <이름>`.
3. 수정.
4. `python3 scripts/check.py` 통과 확인.
5. 화면 작업이면 `python3 scripts/capture.py tobe <이름>`.
6. 커밋·푸시·PR. 보고에 AS-IS / TO-BE 파일 경로를 적는다.

## 화면 변경 캡처 규칙

- 화면을 바꾸는 작업은 **코드를 고치기 전에 AS-IS, 고친 뒤 TO-BE를 찍어 남긴다.**
- 저장 위치: `.agent/captures/YYYY-MM-DD/NN-asis-<이름>.png`, `NN-tobe-<이름>.png` (같은 NN이 한 작업).
  `capture.py`는 데스크톱(1280) `-desktop`, 휴대폰(390) `-mobile` 두 장을 찍는다.
  이 폴더는 git에 올리지 않는다(`.gitignore`). 세션 임시 폴더(scratchpad)에만 두지 않는다.
- 운영 화면이 문제면 운영 버전을 AS-IS로 쓴다: `python3 scripts/capture.py asis <이름> --ref origin/main`.
  사용자가 보낸 변경 전 스크린샷이 있으면 그 파일을 AS-IS로 저장한다.
- 찍지 못했으면 이유를 보고한다.
- **휴대폰 화면 AS-IS / TO-BE는 사용자의 카카오톡 나와의 채팅으로 보낸다.**
  - 도구: PlayMCP `KakaotalkChat-MemoChat`(나에게 보내기). 글자만 200자까지, 이미지 첨부 불가.
  - 그래서 AS-IS와 TO-BE를 나란히 놓은 비공개 Claude 아티팩트 페이지를 만들고, 링크와 한 줄 설명을 보낸다. 같은 날 작업은 한 페이지에 더해 같은 링크를 쓴다.
  - 페이지는 가볍지이지 디자인 시스템(`lightez-design-system`: tokens.css, 카드, 배지, 가로 로고, 에이투지체 제목, 해요체)으로 만든다. 에이투지체는 페이지 글자만 `pyftsubset`으로 뽑아 데이터 URI로 넣고, 한국어는 `word-break: keep-all`.
  - 사진은 누르면 같은 페이지에서 크게(진한 바탕, 한 번 더 누르면 원본 크기, 닫기 버튼·Esc·바깥 누르면 닫힘). 휴대폰 폭에서 가로 넘침이 없는지 확인한 뒤 올린다.
  - 도구가 없거나 실패하면 Claude 화면에 파일로 보내고(SendUserFile) 나챗방 미전송을 보고한다.
- 하위 세션·서브에이전트에 화면 작업을 맡길 때 브리프에 이 규칙을 적는다.

## 답변·문서 말투

존댓말(해요체). 사용자에게 보이는 문서는 짧고 쉬운 한국어로.
