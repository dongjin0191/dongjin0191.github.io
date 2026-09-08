# 영광교회 홈페이지

정적(static) 웹사이트입니다. 서버·데이터베이스 없이 파일만 올리면 동작합니다.

## 폴더 구성

```
yeonggwang-homepage/
├─ index.html        홈
├─ about.html        교회 소개 (담임목사 인사말)
├─ worship.html      예배 안내 (시간표)
├─ sermon.html       설교 목록
├─ bulletin.html     주보 목록
├─ location.html     오시는 길 (지도)
├─ css/style.css     전체 디자인
├─ js/main.js        모바일 메뉴 등 공통 동작
├─ images/           로고·사진 (지금은 임시 로고만)
└─ .nojekyll         GitHub Pages 빌드 우회용
```

## 먼저 고쳐야 할 곳 (노란 안내 상자가 붙어 있는 부분)

| 파일 | 고칠 내용 |
|---|---|
| `worship.html`, `index.html` | 예배 시간표 → 실제 예배 시간 |
| `about.html` | 담임목사 인사말 초안 → 목사님 말씀 |
| `location.html` | 지도 iframe → 정확한 위치의 네이버/카카오 지도 주소, 대중교통 안내 |
| `sermon.html` | 설교 제목·날짜·유튜브 링크 |
| `bulletin.html` | 주보 파일 링크 |
| `images/logo.svg` | 임시 로고 → 교회 공식 로고 |

모든 페이지 하단(푸터)의 주소·전화번호도 확인해 주세요.
전화번호는 각 HTML에서 `01025400533` 로 검색하면 바로 찾을 수 있습니다.

## 로컬에서 미리 보기

`index.html` 을 브라우저로 열면 바로 보입니다.
지도·글꼴 등 일부 기능은 아래처럼 간단한 서버로 열어야 정상 동작합니다.

```
python -m http.server 8000
```

→ 브라우저에서 `http://localhost:8000`

## 인터넷에 공개하기 (GitHub Pages · 무료)

1. GitHub 계정 생성 후 새 저장소(repository) 생성 (예: `yeonggwang-church`)
2. 이 폴더의 파일을 모두 업로드 (드래그 앤 드롭 가능)
3. 저장소 **Settings → Pages → Source** 를 `main` 브랜치 / `/ (root)` 로 지정
4. 1~2분 뒤 `https://<계정명>.github.io/yeonggwang-church/` 주소로 공개됨

### 도메인을 연결하려면

- 도메인 구입 후, 저장소에 `CNAME` 파일(내용: `yeonggwang.org` 같은 도메인 한 줄)을 추가
- 도메인 업체 DNS에서 GitHub Pages 주소로 CNAME/A 레코드 설정
- GitHub Pages 설정에서 도메인 입력 + "Enforce HTTPS" 체크

## 다른 무료 호스팅

- **Netlify** / **Cloudflare Pages** : 이 폴더를 그대로 끌어다 놓으면 배포됩니다.

---
문의: 010-2540-0533
