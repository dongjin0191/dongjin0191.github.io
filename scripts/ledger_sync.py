#!/usr/bin/env python3
"""라파네 가계부 앱(/ledger/)을 Claude 원본과 똑같이 맞춘다.

사용법:
  python3 scripts/ledger_sync.py <원본.html> <db폴더>

<원본.html> = Claude 원본 가계부 artifact의 HTML (Artifact read로 받은 파일)
<db폴더>    = ArtifactData list(out_dir=...)로 받은 폴더. 그 안의
              entries/ balances/ sheet/ walletlog/ 아래 <id>.json 들을 읽는다.

하는 일:
  1. 원본 HTML에서 <!--ORIG-->…<!--/ORIG--> (Claude 원본 주소) 를 지운다.
  2. 입력 버튼(+, 월 점검표, 알림 붙여넣기)을 숨긴다.
  3. db 내용을 읽기 전용 window.claude 로 넣는다.
  4. ledger/index.html 첫 줄(앱 설치용 head)과 서비스워커 등록을 유지한다.
  5. 내용이 바뀌었으면 ledger/sw.js 캐시 번호(ledger-vN)를 올린다.
"""
import json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'ledger', 'index.html')
SW = os.path.join(ROOT, 'ledger', 'sw.js')
COLS = ['entries', 'balances', 'sheet', 'walletlog']
SWREG = ("<script>if('serviceWorker' in navigator&&location.protocol==='https:')"
         "{navigator.serviceWorker.register('sw.js').catch(function(){})}</script></body></html>\n")


def load_db(d):
    snap = {}
    for c in COLS:
        p = os.path.join(d, c)
        docs = {}
        if os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if f.endswith('.json'):
                    with open(os.path.join(p, f), encoding='utf8') as fh:
                        docs[f[:-5]] = json.load(fh)
        snap[c] = docs
    return snap


def shim(snap, stamp):
    js = json.dumps(snap, ensure_ascii=False, sort_keys=True).replace('</', '<\\/')
    return ("<style>#fab,#mbtn,#noti,#nimgl,#erows button{display:none!important}</style>\n<script>\n"
            "/* 읽기 전용 사본: Claude 원본의 db를 " + stamp + " 기준으로 담았다. 저장은 되지 않는다. */\n"
            "(function(){var SNAP=" + js + ";\n"
            "function snapOf(n){var o=SNAP[n]||{};return {docs:Object.keys(o).map(function(k){var v=o[k];"
            "return {id:k,data:function(){return JSON.parse(JSON.stringify(v))}}})}}\n"
            "function ro(){alert('앱(사본)은 읽기 전용입니다. 입력은 Claude 원본에서 해 주세요.');return Promise.reject(new Error('read-only'))}\n"
            "var db={collection:function(n){return {onSnapshot:function(cb){setTimeout(function(){cb(snapOf(n))},0);return function(){}},"
            "add:ro,doc:function(){return {set:ro,delete:ro,update:ro}}}},doc:function(){return {set:ro,delete:ro,update:ro}}};\n"
            "window.claude={use:function(n){return n==='db'?Promise.resolve(db):Promise.reject(new Error('n/a'))}};})();\n"
            "</script>\n")


def main():
    src, dbdir = sys.argv[1], sys.argv[2]
    art = open(src, encoding='utf8').read()
    lines = art.split('\n')
    # 원본 파일 첫 줄은 claude.ai 겉 껍데기, 둘째 줄부터가 가계부
    body = '\n'.join(lines[1:])
    body = re.sub(r'<!--ORIG-->.*?<!--/ORIG-->', '', body, flags=re.S)
    if 'claude.ai/artifact' in body:
        sys.exit('원본 주소가 남아 있어 중단합니다')
    # 끝의 </body></html> 들을 정리
    body = re.sub(r'(\s*</body></html>\s*)+$', '\n', body)
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
    snap = load_db(dbdir)
    if not snap['entries']:
        sys.exit('entries가 비어 있어 중단합니다 (db 폴더 확인)')
    marker = '<div class="wrap">'
    if body.count(marker) != 1:
        sys.exit('wrap 위치를 찾지 못했습니다')
    note = ('<div class="sub" style="text-align:center;margin:-6px 0 6px">앱 최신화: ' + stamp +
            ' (Claude 원본 기준)</div>\n')
    body = body.replace(marker, shim(snap, stamp) + marker + '\n' + note, 1)
    old = open(OUT, encoding='utf8').read()
    head = old.split('\n', 1)[0]
    new = head + '\n' + body + '\n' + SWREG

    def norm(s):  # 시각만 다른 경우는 바뀐 것으로 보지 않는다
        return re.sub(r'\d{4}-\d\d-\d\d \d\d:\d\d', '', s)
    if norm(new) == norm(old):
        print('NOCHANGE')
        return
    open(OUT, 'w', encoding='utf8').write(new)
    sw = open(SW, encoding='utf8').read()
    sw = re.sub(r"ledger-v(\d+)", lambda m: 'ledger-v' + str(int(m.group(1)) + 1), sw, count=1)
    open(SW, 'w', encoding='utf8').write(sw)
    print('UPDATED', stamp, 'entries=%d' % len(snap['entries']))


if __name__ == '__main__':
    main()
