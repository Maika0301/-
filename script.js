(() => {
  const header = document.querySelector("[data-header]");
  const year = document.getElementById("year");
  const heeAudio = document.getElementById("hee-hee");
  const soundToggle = document.querySelector("[data-sound-toggle]");
  if (year) year.textContent = String(new Date().getFullYear());

  const onScroll = () => {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 24);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // --- Hee hee: unlock + play with fade-out on each fade-in ---
  let soundEnabled = false;
  let fadeRaf = 0;
  let activeClip = null;

  const setSoundUi = (on) => {
    if (!soundToggle) return;
    soundToggle.setAttribute("aria-pressed", on ? "true" : "false");
    soundToggle.setAttribute(
      "aria-label",
      on ? "Hee hee サウンドをオフ" : "Hee hee サウンドをオン"
    );
    soundToggle.textContent = on ? "Hee hee ON" : "Hee hee";
  };

  const stopFade = () => {
    if (fadeRaf) cancelAnimationFrame(fadeRaf);
    fadeRaf = 0;
  };

  const playHeeHeeFadeOut = () => {
    if (!soundEnabled || !heeAudio) return;

    stopFade();
    if (activeClip) {
      activeClip.pause();
      activeClip.currentTime = 0;
    }

    const clip = heeAudio.cloneNode(true);
    activeClip = clip;
    clip.volume = 1;

    const start = performance.now();
    const durationMs = Math.max(700, (clip.duration || 1.46) * 1000);

    const tick = (now) => {
      const t = Math.min(1, (now - start) / durationMs);
      // ease-out fade
      clip.volume = Math.max(0, 1 - t * t);
      if (t < 1 && activeClip === clip) {
        fadeRaf = requestAnimationFrame(tick);
      }
    };

    const run = clip.play();
    if (run && typeof run.catch === "function") {
      run.catch(() => {
        soundEnabled = false;
        setSoundUi(false);
      });
    }
    fadeRaf = requestAnimationFrame(tick);
  };

  if (soundToggle && heeAudio) {
    soundToggle.addEventListener("click", async () => {
      if (!soundEnabled) {
        try {
          heeAudio.volume = 0;
          await heeAudio.play();
          heeAudio.pause();
          heeAudio.currentTime = 0;
          heeAudio.volume = 1;
          soundEnabled = true;
          setSoundUi(true);
          playHeeHeeFadeOut();
        } catch {
          soundEnabled = false;
          setSoundUi(false);
        }
      } else {
        soundEnabled = false;
        stopFade();
        if (activeClip) {
          activeClip.pause();
          activeClip = null;
        }
        setSoundUi(false);
      }
    });
  }

  // Reveal on scroll
  const revealTargets = document.querySelectorAll(
    ".section-label, .section-title, .section-copy, .legacy-stats, .tribute .brand-mark, .tribute .cta, .portrait"
  );
  revealTargets.forEach((el) => el.classList.add("reveal"));

  const albums = document.querySelectorAll(".album");

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        playHeeHeeFadeOut();
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
