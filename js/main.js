/* 영광교회 홈페이지 — 공통 스크립트 */
(function () {
  "use strict";

  // 모바일 메뉴 토글
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") nav.classList.remove("open");
    });
  }

  // 현재 페이지 메뉴 강조
  var here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === here || (here === "" && href === "index.html")) {
      a.classList.add("active");
    }
  });

  // 푸터 연도 자동
  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();
})();
