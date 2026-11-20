"""rapa-schedule/events.json(일정 원본) → rapa-schedule/events.ics(폰 캘린더 구독용).

깃허브 작업(.github/workflows/rapa-schedule-ics.yml)이 events.json이 바뀔 때마다 실행한다.
직접 실행해도 된다: python scripts/rapa_schedule_ics.py
"""
import json, pathlib, datetime, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "rapa-schedule"
CAT = {"p": "개인일정", "n": "남부시찰·노회", "d": "동기연", "h": "화기총", "g": "경조사"}


def esc(s):
    return str(s).replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")


def fold(line):
    b = line.encode("utf-8")
    out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode())
        b = b[cut:]
    out.append(b.decode())
    return "\r\n ".join(out)


def main():
    data = json.loads((ROOT / "events.json").read_text(encoding="utf-8"))
    stamp = (data.get("updated") or "2026-01-01").replace("-", "") + "T000000Z"
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//rapa-schedule//KO", "CALSCALE:GREGORIAN",
         "METHOD:PUBLISH", "X-WR-CALNAME:라파일정표", "X-WR-TIMEZONE:Asia/Seoul",
         "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H"]
    for e in data["events"]:
        d = e["date"].replace("-", "")
        uid = hashlib.sha1(f'{e["date"]}|{e["title"]}'.encode()).hexdigest()[:16]
        title = e["title"] + (f' ({e["note"]})' if e.get("note") else "")
        L += ["BEGIN:VEVENT", f"UID:{uid}@rapa-schedule", f"DTSTAMP:{stamp}"]
        if e.get("time"):
            t1 = e["time"].replace(":", "") + "00"
            t2 = (e.get("endTime") or e["time"]).replace(":", "") + "00"
            L += [f"DTSTART;TZID=Asia/Seoul:{d}T{t1}", f"DTEND;TZID=Asia/Seoul:{d}T{t2}"]
        else:
            last = datetime.date.fromisoformat(e.get("until") or e["date"])
            end = (last + datetime.timedelta(days=1)).strftime("%Y%m%d")
            L += [f"DTSTART;VALUE=DATE:{d}", f"DTEND;VALUE=DATE:{end}", "TRANSP:TRANSPARENT"]
        L += [f"SUMMARY:{esc(title)}", f"CATEGORIES:{esc(CAT.get(e.get('cat'), '개인일정'))}", "END:VEVENT"]
    L.append("END:VCALENDAR")
    (ROOT / "events.ics").write_bytes(("\r\n".join(fold(x) for x in L) + "\r\n").encode("utf-8"))
    print(f'{len(data["events"])} events → events.ics')


if __name__ == "__main__":
    main()
