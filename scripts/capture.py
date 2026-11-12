#!/usr/bin/env python3
"""화면 캡처: 데스크톱 폭과 휴대폰 폭 전체 페이지를 AS-IS / TO-BE로 저장.

사용:
  python3 scripts/capture.py asis <이름>            # 코드 고치기 전
  python3 scripts/capture.py tobe <이름>            # 고친 뒤 (같은 이름의 마지막 AS-IS 번호를 이어 씀)
  python3 scripts/capture.py asis <이름> --ref main # 특정 git 버전을 찍기 (예: 운영 중인 main)

저장: .agent/captures/YYYY-MM-DD/NN-asis-<이름>-desktop.png, ...-mobile.png
Chrome 위치는 자동으로 찾고, 못 찾으면 CHROME 환경변수로 지정.
"""
import argparse
import datetime
import functools
import http.server
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWPORTS = {"desktop": (1280, 900, 1), "mobile": (390, 844, 2)}  # 폭, 화면 높이, 배율

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]


def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for c in CHROME_CANDIDATES:
        path = c if os.path.isabs(c) else shutil.which(c)
        if path and os.path.exists(path):
            return path
    for p in sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome")):
        return str(p)
    sys.exit("Chrome을 찾지 못했어요. CHROME=/경로/chrome 으로 지정해 주세요.")


def make_handler(site, inject):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path.startswith("/__capture"):
                html = (site / "index.html").read_text(encoding="utf-8")
                body = html.replace("</head>", inject(self.path) + "</head>", 1).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                super().do_GET()
    return functools.partial(Handler, directory=str(site))


def inject(path):
    # 히어로가 100vh라 창을 페이지 높이로 키우면 늘어남 → 실제 화면 높이로 고정
    vh = re.search(r"vh=(\d+)", path).group(1)
    return (f"<style>.hero{{min-height:{vh}px!important}}</style>"
            "<script>addEventListener('load',()=>document.documentElement"
            ".setAttribute('data-h',document.documentElement.scrollHeight))</script>")


def chrome(args, chrome_bin):
    base = [chrome_bin, "--headless=new", "--no-sandbox", "--hide-scrollbars",
            "--disable-gpu", "--no-first-run", "--virtual-time-budget=4000"]
    return subprocess.run(base + args, capture_output=True, text=True, timeout=120)


def next_nn(day_dir, kind, name):
    nums = [int(m.group(1)) for f in day_dir.glob("*.png")
            if (m := re.match(r"(\d+)-", f.name))]
    if kind == "tobe":
        same = [int(m.group(1)) for f in day_dir.glob(f"*-asis-{name}-*.png")
                if (m := re.match(r"(\d+)-", f.name))]
        if same:
            return max(same)
    return max(nums, default=0) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["asis", "tobe"])
    ap.add_argument("name", help="영문 소문자-하이픈, 예: hero-copy")
    ap.add_argument("--ref", help="찍을 git 버전 (생략하면 지금 작업 폴더)")
    ap.add_argument("--nn", type=int, help="번호를 직접 지정")
    a = ap.parse_args()

    day_dir = ROOT / ".agent/captures" / datetime.date.today().isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    nn = a.nn or next_nn(day_dir, a.kind, a.name)

    tmp = None
    site = ROOT
    if a.ref:
        tmp = tempfile.mkdtemp()
        data = subprocess.run(["git", "-C", str(ROOT), "archive", a.ref],
                              capture_output=True, check=True).stdout
        tarfile.open(fileobj=BytesIO(data)).extractall(tmp)
        site = Path(tmp)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), make_handler(site, inject))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    chrome_bin = find_chrome()

    try:
        for label, (w, vh, scale) in VIEWPORTS.items():
            url = f"http://127.0.0.1:{port}/__capture?vh={vh}"
            dom = chrome([f"--window-size={w},{vh}", "--dump-dom", url], chrome_bin).stdout
            m = re.search(r'data-h="(\d+)"', dom)
            height = int(m.group(1)) if m else vh * 8
            out = day_dir / f"{nn:02d}-{a.kind}-{a.name}-{label}.png"
            chrome([f"--window-size={w},{height}", f"--force-device-scale-factor={scale}",
                    f"--screenshot={out}", url], chrome_bin)
            print(out.relative_to(ROOT) if out.exists() else f"실패: {out}")
    finally:
        server.shutdown()
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
