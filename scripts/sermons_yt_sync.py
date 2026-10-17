# 라파 유튜브(@rafa0191) 새 영상을 sermons/index.html 의 DATA 에 더한다.
# GitHub Actions 에서 매일 실행된다 (.github/workflows/sermons-yt-sync.yml).
import json, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

HANDLE = 'rafa0191'
PAGE = 'sermons/index.html'
SW = 'sermons/sw.js'
MUST = ('이동진', '라파')  # 제목에 이 말이 있는 영상만 설교로 본다
UA = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8')


def channel_id():
    m = re.search(r'"(?:channelId|externalId)":"(UC[\w-]{22})"', get('https://www.youtube.com/@' + HANDLE))
    if not m:
        sys.exit('채널 ID를 찾지 못했습니다')
    return m.group(1)


def feed(cid):
    ns = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
    root = ET.fromstring(get('https://www.youtube.com/feeds/videos.xml?channel_id=' + cid))
    for e in root.findall('a:entry', ns):
        yield e.find('yt:videoId', ns).text, e.find('a:title', ns).text or '', e.find('a:published', ns).text


def date_of(title, published):
    for m in re.finditer(r'(20\d{2})(\d{2})(\d{2})', title):
        try:
            return datetime(int(m[1]), int(m[2]), int(m[3])).date()
        except ValueError:
            pass
    return (datetime.fromisoformat(published.replace('Z', '+00:00')) + timedelta(hours=9)).date()


def kind(t):
    if re.search('부흥회|집회|성경학교|캠프|세미나|헌신예배', t):
        return '집회'
    for k in ('새벽', '수요', '금요'):
        if k in t:
            return k
    return ''


def role(t):
    if '설교' in t:
        return '설교'
    return '찬양' if '찬양' in t else '예배'


def main():
    src = open(PAGE, encoding='utf-8').read()
    lines = src.split('\n')
    idx = next(i for i, l in enumerate(lines) if l.startswith('var DATA = '))
    body = lines[idx][len('var DATA = '):].rstrip()
    semi = body.endswith(';')
    data = json.loads(body.rstrip(';'))
    have = {y['i'] for r in data for y in r.get('y', [])}

    added = 0
    for vid, title, pub in reversed(list(feed(channel_id()))):
        if vid in have or not any(w in title for w in MUST):
            continue
        d = date_of(title, pub)
        ds = d.isoformat()
        x = 0 if '영광교회' in title else 1
        y = {'i': vid, 't': title, 'r': role(title), 'x': x, 'ch': 'yt_' + HANDLE}
        same = next((r for r in data if r.get('src') == 'yt' and r['d'] == ds), None)
        if same:
            same['y'].append(y)
        else:
            e = {'d': ds, 'md': '', 'w': '월화수목금토일'[d.weekday()], 'k': kind(title), 't': '', 'ti': title,
                 'b': '', 'c': '', 'm': [], 'v': [], 'y': [y], 'src': 'yt', 'ext': x, 'rel': ''}
            pos = next((i for i, r in enumerate(data) if r.get('src') == 'yt' and r['d'] < ds), len(data))
            data.insert(pos, e)
        have.add(vid)
        added += 1
        print('추가:', ds, title)

    if not added:
        print('새 영상 없음')
        return
    lines[idx] = 'var DATA = ' + json.dumps(data, ensure_ascii=False) + (';' if semi else '')
    open(PAGE, 'w', encoding='utf-8').write('\n'.join(lines))
    sw = open(SW, encoding='utf-8').read()
    sw = re.sub(r"sermons-v(\d+)", lambda m: 'sermons-v%d' % (int(m[1]) + 1), sw, count=1)
    open(SW, 'w', encoding='utf-8').write(sw)


if __name__ == '__main__':
    main()
