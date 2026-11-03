# 시화산노회 유튜브(@시화산노회)에서 제목에 '26년 … 제주 … 수양회'가 들어간 영상을 모아
# jeju-2026/videos.json 에 시간 순으로 더한다. 앱(jeju-2026)이 이 목록을 읽어 영상 칸을 만든다.
# GitHub Actions 에서 매시간 실행된다 (.github/workflows/jeju-videos.yml). 2026-12-31 이후에는 아무것도 하지 않는다.
import json, os, re, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

HANDLE = '시화산노회'
OUT = 'jeju-2026/videos.json'
UNTIL = datetime(2026, 12, 31, tzinfo=timezone.utc)
UA = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ko'}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8')


def wanted(title):
    s = re.sub(r'[\s,.\-_/·|]+', '', title)
    # 11/3: 제목에 '부부수양회'가 들어가면 모두 (예전 기준 '26년+제주+수양회'도 그대로)
    return '부부수양회' in s or ('26년' in s and '제주' in s and '수양회' in s)


# 총무가 링크로 보낸 영상(채널 목록에 안 잡혀도 넣는다)
EXTRA = ['0Sobi93p7ro']


def main():
    if datetime.now(timezone.utc) > UNTIL:
        print('수양회 영상 수집 기간이 끝났습니다'); return
    m = re.search(r'"(?:channelId|externalId)":"(UC[\w-]{22})"', get('https://www.youtube.com/@' + urllib.parse.quote(HANDLE)))
    if not m:
        sys.exit('채널 ID를 찾지 못했습니다')
    ns = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
    root = ET.fromstring(get('https://www.youtube.com/feeds/videos.xml?channel_id=' + m.group(1)))
    old = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else []
    have = {v['id'] for v in old}
    for e in root.findall('a:entry', ns):
        vid, title = e.find('yt:videoId', ns).text, e.find('a:title', ns).text or ''
        if vid in have or not wanted(title):
            continue
        pub = datetime.fromisoformat(e.find('a:published', ns).text.replace('Z', '+00:00')) + timedelta(hours=9)
        old.append({'id': vid, 't': title, 'u': 'https://youtu.be/' + vid, 'd': pub.strftime('%Y-%m-%dT%H:%M'),
                    'th': 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % vid})
        print('새 영상', title)
    for vid in EXTRA:
        if vid in {v['id'] for v in old}:
            continue
        try:
            o = json.loads(get('https://www.youtube.com/oembed?format=json&url=' + urllib.parse.quote('https://youtu.be/' + vid)))
            title = o.get('title') or '부부수양회 영상'
        except Exception as ex:
            print('제목을 못 읽음', vid, ex); title = '부부수양회 영상'
        old.append({'id': vid, 't': title, 'u': 'https://youtu.be/' + vid, 'd': datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%dT%H:%M'),
                    'th': 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % vid})
        print('추가 영상', title)
    old.sort(key=lambda v: v['d'])
    json.dump(old, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


main()
