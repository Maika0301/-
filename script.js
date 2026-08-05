(() => {
  const header = document.querySelector("[data-header]");
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 24);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Reveal on scroll
  const revealTargets = document.querySelectorAll(
    ".section-label, .section-title, .section-copy, .legacy-stats, .tribute .brand-mark, .tribute .cta"
  );
  revealTargets.forEach((el) => el.classList.add("reveal"));

  const albums = document.querySelectorAll(".album");

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    },
    { threshold: 0.18, rootMargin: "0px 0px -8% 0px" }
  );

  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
  albums.forEach((el) => io.observe(el));

  // Count-up stats
  const counters = document.querySelectorAll("[data-count]");
  const countIo = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = Number(el.getAttribute("data-count") || "0");
        const duration = 1200;
        const start = performance.now();

        const tick = (now) => {
          const t = Math.min(1, (now - start) / duration);
          const eased = 1 - Math.pow(1 - t, 3);
          el.textContent = String(Math.round(target * eased));
          if (t < 1) requestAnimationFrame(tick);
        };

        requestAnimationFrame(tick);
        countIo.unobserve(el);
      });
    },
    { threshold: 0.5 }
  );
  counters.forEach((el) => countIo.observe(el));

  // Moments carousel
  const moments = Array.from(document.querySelectorAll(".moment"));
  const dots = Array.from(document.querySelectorAll(".moment-dot"));
  let index = 0;
  let timer;

  const show = (next) => {
    index = (next + moments.length) % moments.length;
    moments.forEach((m, i) => m.classList.toggle("is-active", i === index));
    dots.forEach((d, i) => {
      const active = i === index;
      d.classList.toggle("is-active", active);
      d.setAttribute("aria-selected", active ? "true" : "false");
    });
  };

  const restart = () => {
    clearInterval(timer);
    timer = setInterval(() => show(index + 1), 5200);
  };

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      show(Number(dot.getAttribute("data-go") || "0"));
      restart();
    });
  });

  if (moments.length > 1) restart();
})();
