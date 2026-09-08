/* ============================================================
   영광교회 — 외부 서비스 설정
   설치 마법사가 자동 생성 (2026-09-08)
   ============================================================ */

/* --- 푸시 알림(OneSignal) — 비어 있으면 푸시만 꺼집니다 --- */
window.ONESIGNAL_APP_ID = "";

/* --- 회원/로그인/게시판(Supabase) ---
   아래 두 값은 공개돼도 안전한 공개키입니다. 실제 보안은 DB의 RLS 정책으로 지킵니다. */
(function () {
  var host = (location.hostname || "").toLowerCase();
  var isLocal = host === "localhost" || host === "127.0.0.1";
  window.APP_ENV = window.APP_ENV || (isLocal ? "development" : "production");
  window.SUPABASE_URL = "";
  window.SUPABASE_ANON_KEY = "";
})();

/* --- 파일 업로드(Cloudflare R2 Worker) — 비어 있으면 업로드 기능이 숨겨집니다 --- */
window.R2_UPLOAD_URL = "";

/* --- 교적·재정 (구글 Apps Script 웹앱) --- */
window.FINANCE_API_URL = "";
window.LIBRARY_API_URL = "";
window.LIBRARY_FOLDER_ID = "";

/* --- 연말정산 알림 이메일(FormSubmit) --- */
window.FORMSUBMIT_EMAIL = "";

/* --- AI 설정 --- */
window.AI_MODE = "none";    // AI 기능 사용 안 함
