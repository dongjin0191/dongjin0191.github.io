"""제주 수양회 앱 '안내' 탭: 총무·임원이 올린 GitHub 이슈('[안내] …')를 jeju-2026/notices.json 으로 모은다.

열린 이슈만, 저장소 주인·멤버·협업자가 쓴 것만 넣는다. 이슈를 닫으면 앱에서 사라진다."""
import json, os, urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "dongjin0191/dongjin0191.github.io")
OUT = "jeju-2026/notices.json"
OK = {"OWNER", "MEMBER", "COLLABORATOR"}


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
    tx = (i.get("body") or "").replace("\r\n", "\n").strip() or title[len("[안내]"):].strip()
    notes.append({"id": f"gh-{i['number']}", "at": i["created_at"], "tx": tx})
notes.sort(key=lambda n: n["at"], reverse=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(notes, f, ensure_ascii=False, indent=1)
print(len(notes), "notices")
