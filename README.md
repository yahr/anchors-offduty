# anchors-offduty

ANCHORS OFF·DUTY — 쉬는 날에도 차려입는 40대를 위한 브랜드 공식 페이지
https://yahr.github.io/anchors-offduty/

## 로컬에서 보기

```bash
git clone https://github.com/yahr/anchors-offduty.git
cd anchors-offduty
python3 -m http.server 8771   # http://localhost:8771
```

## 검사 · 캡처

```bash
python3 scripts/check.py                  # JSON-LD, 태그 균형, 파일 경로, 내부 자료 표현
python3 scripts/capture.py asis <이름>    # 고치기 전 화면 (데스크톱·휴대폰)
python3 scripts/capture.py tobe <이름>    # 고친 뒤 화면
```

캡처에는 Chrome이 필요해요. 작업 규칙은 `CLAUDE.md`에 있어요.
