const navToggle = document.querySelector(".nav-toggle");
const siteNav = document.querySelector(".site-nav");
const mobileNavQuery = window.matchMedia("(max-width: 1040px)");

if (navToggle && siteNav) {
  const closeNav = () => {
    siteNav.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
  };

  navToggle.addEventListener("click", () => {
    const isOpen = siteNav.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  siteNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (mobileNavQuery.matches) {
        closeNav();
      }
    });
  });

  mobileNavQuery.addEventListener("change", (event) => {
    if (!event.matches) {
      closeNav();
    }
  });
}

const revealTargets = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    },
    {
      // Large sections such as the publications archive may only have a small
      // visible slice on initial load, so reveal them as soon as they enter view.
      rootMargin: "0px 0px -8% 0px",
      threshold: 0,
    }
  );

  revealTargets.forEach((target) => observer.observe(target));
} else {
  revealTargets.forEach((target) => target.classList.add("is-visible"));
}
