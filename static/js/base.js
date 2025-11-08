// home.js
document.addEventListener("DOMContentLoaded", function() {
  const navbar = document.querySelector(".navbar-scroll");
  const logo = document.getElementById("logo-img"); // معرف الصورة في HTML

  function checkScroll() {
    if(window.scrollY > 50) {
      navbar.classList.add("scrolled");
      logo.src = "/static/images/logo.png"; // الصورة الجديدة عند السكروول
    } else {
      navbar.classList.remove("scrolled");
      logo.src = "/static/images/logo.png"; // الصورة الأصلية
    }
  }

  window.addEventListener("scroll", checkScroll);
  checkScroll(); // initial check
});
