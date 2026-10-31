"""제주 수양회 앱 '안내' 탭: 총무·임원이 올린 GitHub 이슈('[안내] …')를 jeju-2026/notices.json 으로 모은다.

열린 이슈만, 저장소 주인·멤버·협업자가 쓴 것만 넣는다. 이슈를 닫으면 앱에서 사라진다.
이슈 글에 붙인 사진(![..](주소) 또는 <img src=..>)은 jeju-2026/nimg/ 에 내려받아 함께 보여 준다."""
import json, os, re, urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "dongjin0191/dongjin0191.github.io")
OUT = "jeju-2026/notices.json"
OK = {"OWNER", "MEMBER", "COLLABORATOR"}
IMGDIR = "jeju-2026/nimg"
IMG_RE = re.compile(r'!\[[^\]]*\]\((https://[^)\s]+)\)|<img[^>]*?src="(https://[^"]+)"[^>]*>', re.I)
EXT = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp", "image/heic": "heic"}


def fetch_img(url, base):
    """사진을 한 번만 내려받는다(같은 이름이 있으면 그대로 쓴다)."""
    os.makedirs(IMGDIR, exist_ok=True)
    for f in os.listdir(IMGDIR):
        if f.rsplit(".", 1)[0] == base:
            return f"nimg/{f}"
    hdr = {"User-Agent": "jeju-notices"}  # 공개 저장소라 사진 주소는 로그인 없이 열린다
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60)
        data, ct = r.read(), (r.headers.get("Content-Type") or "").split(";")[0].strip()
    except Exception as e:  # 사진 하나 실패해도 안내 글은 올린다
        print("img fail", url, e)
        return None
    if not ct.startswith("image/") or len(data) > 15_000_000:
        return None
    name = f"{base}.{EXT.get(ct, 'jpg')}"
    with open(f"{IMGDIR}/{name}", "wb") as f:
        f.write(data)
    return f"nimg/{name}"


def issues():
    page, out = 1, []
    while True:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&page={page}",
                                     headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"})
        batch = json.load(urllib.request.urlopen(req, timeout=30))
        out += batch
        if len(batch) < 100:
            return out
        page += 1


notes = []
for i in issues():
    title = (i.get("title") or "").strip()
    if "pull_request" in i or i.get("author_association") not in OK or not title.startswith("[안내]"):
        continue
    body = (i.get("body") or "").replace("\r\n", "\n")
    imgs = []
    for k, m in enumerate(IMG_RE.finditer(body)):
        got = fetch_img(m.group(1) or m.group(2), f"gh-{i['number']}-{k + 1}")
        if got:
            imgs.append(got)
    body = re.sub(r"\n{3,}", "\n\n", IMG_RE.sub("", body)).strip()
    tx = body or title[len("[안내]"):].strip()
    n = {"id": f"gh-{i['number']}", "at": i["created_at"], "tx": tx}
    if imgs:
        n["imgs"] = imgs
    notes.append(n)
notes.sort(key=lambda n: n["at"], reverse=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(notes, f, ensure_ascii=False, indent=1)
print(len(notes), "notices")
