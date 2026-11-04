# 구글 드라이브 1일차·2일차·3일차 폴더 사진을 jeju-2026/days/d1~d3 에 더한다 (11/4 개편).
# 예전처럼 매번 전부 받지 않고, 폴더 목록만 먼저 읽은 뒤 아직 없는 사진만 받아서 번호를 이어 붙인다.
# 그래서 2일차·3일차처럼 새로 올라온 사진이 빨리 들어오고, 이미 올린 사진은 그대로 남는다.
import json, os, sys, tempfile
import gdown
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
register_heif_opener()

OUT = 'jeju-2026/days'
EXT = ('jpg', 'jpeg', 'png', 'heic', 'heif', 'webp')
MAX_NEW = int(os.environ.get('MAX_NEW', '200'))
folders = os.environ['DRIVE_FOLDERS'].split()
path = os.path.join(OUT, 'days.json')
res = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
for k in ('d1', 'd2', 'd3'):
    res.setdefault(k, [])
have = {(k, r['cap']) for k in res for r in res[k]}
todo = []
for F in folders:
    try:
        files = gdown.download_folder(id=F, output='/tmp/list', skip_download=True, quiet=True) or []
    except Exception as e:
        print('목록 실패', F, e); continue
    print('폴더', F, '파일', len(files), [(getattr(x, 'path', ''), getattr(x, 'local_path', '')) for x in files[:2]])
    for f in files:
        full = (getattr(f, 'local_path', '') or '') + '/' + (getattr(f, 'path', '') or '')
        parts = full.replace('\\', '/').split('/')
        day = next((k for k in (1, 2, 3) for p in parts if f'{k}일차' in p), None)
        name = os.path.basename(getattr(f, 'local_path', '') or f.path)
        if not day or name.lower().rsplit('.', 1)[-1] not in EXT:
            continue
        cap = os.path.splitext(name)[0]
        if (f'd{day}', cap) in have:
            continue
        have.add((f'd{day}', cap))
        todo.append((day, f.id, name, cap))
print('새 사진', len(todo), {d: sum(1 for t in todo if t[0] == d) for d in (1, 2, 3)})
todo.sort(key=lambda t: (-t[0], t[2]))   # 최근 날(3일차→2일차→1일차) 먼저
n = 0
for day, fid, name, cap in todo[:MAX_NEW]:
    tmp = os.path.join(tempfile.gettempdir(), 'dl_' + fid + '.' + name.rsplit('.', 1)[-1])
    try:
        gdown.download(id=fid, output=tmp, quiet=True)
        im = ImageOps.exif_transpose(Image.open(tmp)).convert('RGB')
    except Exception as e:
        print('skip', name, e); continue
    im.thumbnail((1280, 1280))
    k = f'd{day}'
    d = os.path.join(OUT, k); os.makedirs(d, exist_ok=True)
    num = max([int(r['src'].split('/')[-1][:3]) for r in res[k]] + [0]) + 1
    fn = '%03d.jpg' % num
    im.save(os.path.join(d, fn), quality=78, optimize=True)
    res[k].append({'src': f'{k}/{fn}', 'cap': cap})
    n += 1
    if n % 20 == 0:
        json.dump(res, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(res, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('추가', n, {k: len(v) for k, v in res.items()})
