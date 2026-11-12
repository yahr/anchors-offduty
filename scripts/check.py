#!/usr/bin/env python3
"""페이지 검사: JSON-LD 파싱, HTML 태그 균형, 로컬 파일 경로, 고객용 금지 표현.

사용: python3 scripts/check.py
문제가 하나라도 있으면 종료 코드 1.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "404.html"]
TEXT_FILES = ["index.html", "llms.txt"]

# 고객용 페이지에 다시 들어가면 안 되는 내부 자료 표현
FORBIDDEN = [
    "무신사",
    "anchors-report",
    "기획 리포트",
    "리뷰 779",
    "779건",
    "스펙시트",
    "백킹",
    "양산 샘플",
    "타겟",
]

BLOCK_TAGS = {"html", "head", "body", "main", "header", "footer", "nav", "section",
              "div", "details", "summary", "table", "thead", "tbody", "tr", "figure",
              "blockquote", "ul", "li", "p", "h1", "h2", "h3", "h4", "h5", "a"}

errors = []


class Balance(HTMLParser):
    def __init__(self, name):
        super().__init__()
        self.name, self.stack = name, []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self.stack.append((tag, self.getpos()[0]))
        for key, val in attrs:
            if key in ("src", "href") and val and not re.match(r"^(https?:|mailto:|#|data:|/)", val):
                if not (ROOT / val.split("#")[0].split("?")[0]).exists():
                    errors.append(f"{self.name}:{self.getpos()[0]} 없는 파일 경로: {val}")

    def handle_endtag(self, tag):
        if tag not in BLOCK_TAGS:
            return
        if not self.stack or self.stack[-1][0] != tag:
            errors.append(f"{self.name}:{self.getpos()[0]} 닫는 태그 불일치: </{tag}>")
            return
        self.stack.pop()

    def close(self):
        super().close()
        for tag, line in self.stack:
            errors.append(f"{self.name}:{line} 닫히지 않은 태그: <{tag}>")


for name in PAGES:
    src = (ROOT / name).read_text(encoding="utf-8")
    p = Balance(name)
    p.feed(src)
    p.close()
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError as e:
            errors.append(f"{name} JSON-LD 파싱 실패: {e}")

for name in TEXT_FILES:
    for i, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        for word in FORBIDDEN:
            if word in line:
                errors.append(f"{name}:{i} 내부 자료 표현 '{word}'")

if errors:
    print("\n".join(errors))
    print(f"\n문제 {len(errors)}건")
    sys.exit(1)
print("검사 통과")
