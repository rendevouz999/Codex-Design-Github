/**
 * Brain Design - Web Deck Medium - deck-runtime.js
 *
 * Inlined verbatim into every generated web deck. Zero dependencies, no build
 * step, no CDN, no framework. Pairs with `stage-base.css`, which owns every
 * class name and custom property this file writes.
 *
 * Responsibilities
 *   - fit the authored 1920 x 1080 stage into the viewport with one transform
 *   - own the active-slide index and apply it through the `is-active` class
 *   - keyboard, coarse-pointer tap and wheel navigation
 *   - deep link, chrome state, accessibility state, lifecycle event
 *
 * Public API, on the single global `BrainDeck`
 *   BrainDeck.index      current 0-based index, -1 when the deck has no slides
 *   BrainDeck.length      slide count
 *   BrainDeck.goTo(i)     jump to a 0-based index, clamped, returns the index
 *   BrainDeck.next()      step forward, returns the index
 *   BrainDeck.prev()      step back, returns the index
 *   BrainDeck.reset()     return to the first slide
 *   BrainDeck.init()      idempotent, called automatically on DOMContentLoaded
 *   BrainDeck.fit()       force a stage refit
 *
 * Lifecycle event
 *   `deckslidechange` on the stage element, `bubbles: true`, `composed: true`,
 *   detail `{ index, previousIndex, total, reason }` where `reason` is
 *   `init` | `key` | `pointer` | `wheel` | `api`.
 *
 * DOM contract, matching the `stage-base.css` header
 *   `.deck-viewport`, `.deck-stage`, `.deck-slide`, `.deck-chrome`,
 *   `.deck-progress`, `.deck-progress-bar`, `.deck-counter-current`,
 *   `.deck-counter-total`, `.deck-control`, `.deck-tap`, `.deck-live`
 *   states `is-active`, `is-rearm`, `is-idle`
 *   attributes `[data-deck-nav]`, `[data-deck-step]`, `[data-deck-index]`,
 *   `[data-deck-headline]`, `[data-deck-interactive]`, `[data-deck-ignore-keys]`,
 *   `[data-deck-reduced-motion]`
 *   custom properties `--deck-scale`, `--deck-progress`
 *
 * Every lookup is optional. A deck with no chrome, no live region or no slides
 * at all still loads without throwing.
 */
(function (global) {
  "use strict";

  const doc = global.document;
  if (!doc) return;

  const docEl = doc.documentElement;

  /** Authored stage size. Never derived from the viewport. */
  const STAGE_WIDTH = 1920;
  const STAGE_HEIGHT = 1080;

  /** Wheel step needs a floor and a cooldown, or one trackpad flick skips six slides. */
  const WHEEL_THRESHOLD = 28;
  const WHEEL_COOLDOWN_MS = 480;

  /** Digit keys buffer, so a deck with more than nine slides is still reachable. */
  const DIGIT_COMMIT_MS = 700;
  const DIGIT_MAX_LENGTH = 3;

  /** Controls fade out after a quiet stretch and return on the next input. */
  const IDLE_HIDE_MS = 2600;
  const POINTER_ACTIVITY_MS = 250;

  const SELECTOR = {
    viewport: ".deck-viewport",
    stage: ".deck-stage",
    slide: ".deck-slide",
    chrome: ".deck-chrome",
    progress: ".deck-progress",
    counterCurrent: ".deck-counter-current",
    counterTotal: ".deck-counter-total",
    live: ".deck-live, [data-deck-live]",
    headline: "[data-deck-headline], h1, h2",
    navPrev: '[data-deck-nav="prev"]',
    navNext: '[data-deck-nav="next"]',
  };

  /**
   * A coarse-pointer tap inside one of these never steps the deck. `.deck-slide`
   * carries `tabindex="-1"`, so the tabindex clause does not match a slide.
   */
  const INTERACTIVE = [
    "a[href]",
    "button",
    "input",
    "select",
    "textarea",
    "label",
    "summary",
    "video",
    "audio",
    '[contenteditable=""]',
    '[contenteditable="true"]',
    '[tabindex]:not([tabindex="-1"])',
    "[data-deck-interactive]",
  ].join(",");

  let viewportEl = null;
  let stageEl = null;
  let chromeEl = null;
  let progressEl = null;
  let counterCurrentEl = null;
  let counterTotalEl = null;
  let liveEl = null;
  let navPrevEls = [];
  let navNextEls = [];

  let slides = [];
  let index = -1;
  let started = false;
  let reduceMotion = false;
  let coarseQuery = null;

  let fitFrame = 0;
  let lastWheelAt = 0;
  let lastPointerAt = 0;
  let idleTimer = 0;
  let digitBuffer = "";
  let digitTimer = 0;

  /* =========================================================================
     Stage fit
     ========================================================================= */

  /**
   * Apply the uniform fit transform. `transform-origin: 0 0` keeps the
   * translate in unscaled pixels, so the centring offset stays exact.
   */
  function applyFit() {
    fitFrame = 0;
    if (!stageEl) return;
    const width = global.innerWidth || STAGE_WIDTH;
    const height = global.innerHeight || STAGE_HEIGHT;
    const scale = Math.min(width / STAGE_WIDTH, height / STAGE_HEIGHT);
    const offsetX = Math.round((width - STAGE_WIDTH * scale) / 2);
    const offsetY = Math.round((height - STAGE_HEIGHT * scale) / 2);
    stageEl.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
    docEl.style.setProperty("--deck-scale", String(scale));
  }

  /** Coalesce resize bursts into one write per frame. */
  function scheduleFit() {
    if (fitFrame) return;
    fitFrame = global.requestAnimationFrame(applyFit);
  }

  /* =========================================================================
     Slide collection and index maths
     ========================================================================= */

  function collect() {
    if (!stageEl) {
      slides = [];
      return;
    }
    let found = Array.prototype.slice.call(stageEl.querySelectorAll(`:scope > ${SELECTOR.slide}`));
    if (!found.length) {
      found = Array.prototype.slice.call(stageEl.querySelectorAll(SELECTOR.slide));
    }
    slides = found;
  }

  function clamp(value) {
    if (!slides.length) return -1;
    if (!Number.isFinite(value)) return index < 0 ? 0 : index;
    return Math.min(slides.length - 1, Math.max(0, Math.trunc(value)));
  }

  /* =========================================================================
     State application
     ========================================================================= */

  /**
   * Replay the entrance of a slide that is already active. The reset class
   * must be committed to the style system before it is removed, hence the
   * forced layout read.
   */
  function rearm(slide) {
    slide.classList.add("is-rearm");
    void slide.offsetWidth;
    slide.classList.remove("is-rearm");
  }

  function applyState(nextIndex, reason) {
    const previousIndex = index;
    index = nextIndex;

    for (let i = 0; i < slides.length; i += 1) {
      const slide = slides[i];
      const active = i === index;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-hidden", active ? "false" : "true");
      // `inert` keeps the tab order out of a hidden slide. Applied after the
      // active class, so focus is never trapped in an inert subtree.
      if ("inert" in slide) slide.inert = !active;
    }

    const slide = slides[index] || null;
    if (slide && reason !== "init" && !reduceMotion) rearm(slide);

    updateChrome();
    announce(slide);
    syncHash();
    moveFocus(slide);
    emitChange(previousIndex, reason);
  }

  function goTo(target, reason) {
    if (!slides.length) return index;
    const clamped = clamp(target);
    if (clamped === index) {
      // Same slide: replay the entrance, but do not emit a change or rewrite
      // history for a position that did not move.
      const slide = slides[index];
      if (slide && !reduceMotion) rearm(slide);
      return index;
    }
    applyState(clamped, reason || "api");
    return index;
  }

  function step(delta, reason) {
    if (!slides.length) return index;
    return goTo(index + delta, reason);
  }

  /* =========================================================================
     Chrome, announcement, deep link, lifecycle event
     ========================================================================= */

  function setNavDisabled(elements, disabled) {
    for (let i = 0; i < elements.length; i += 1) {
      const el = elements[i];
      if ("disabled" in el) el.disabled = disabled;
      else el.setAttribute("aria-disabled", disabled ? "true" : "false");
    }
  }

  function updateChrome() {
    const total = slides.length;
    const ratio = total ? (index + 1) / total : 0;
    docEl.style.setProperty("--deck-progress", String(ratio));

    if (counterCurrentEl) counterCurrentEl.textContent = String(total ? index + 1 : 0);
    if (counterTotalEl) counterTotalEl.textContent = String(total);

    if (progressEl && progressEl.getAttribute("role") === "progressbar") {
      progressEl.setAttribute("aria-valuemin", "1");
      progressEl.setAttribute("aria-valuemax", String(total || 1));
      progressEl.setAttribute("aria-valuenow", String(total ? index + 1 : 0));
    }

    setNavDisabled(navPrevEls, index <= 0);
    setNavDisabled(navNextEls, total === 0 || index >= total - 1);
  }

  function announce(slide) {
    if (!liveEl) return;
    const headline = slide ? slide.querySelector(SELECTOR.headline) : null;
    const label = headline && headline.textContent ? headline.textContent.trim() : "";
    const position = `Slide ${index + 1} of ${slides.length}`;
    liveEl.textContent = label ? `${position}: ${label}` : position;
  }

  function readHash() {
    const match = /^#(\d+)$/.exec(global.location.hash || "");
    if (!match) return null;
    const value = parseInt(match[1], 10);
    return Number.isFinite(value) && value > 0 ? value - 1 : null;
  }

  function syncHash() {
    if (!global.history || typeof global.history.replaceState !== "function") return;
    const hash = `#${index + 1}`;
    if (global.location.hash === hash) return;
    try {
      global.history.replaceState(null, "", hash);
    } catch (error) {
      // An opaque-origin document rejects replaceState. Navigation still works.
    }
  }

  function emitChange(previousIndex, reason) {
    const target = stageEl || doc.body;
    if (!target) return;
    target.dispatchEvent(
      new CustomEvent("deckslidechange", {
        bubbles: true,
        composed: true,
        detail: { index, previousIndex, total: slides.length, reason },
      })
    );
  }

  /* =========================================================================
     Focus
     ========================================================================= */

  /**
   * Move focus to the active slide container, unless something outside the
   * slides already holds it. Focus sitting in the slide that just went inert
   * must be rescued, focus on a chrome control must be left alone.
   */
  function moveFocus(slide) {
    if (!slide) return;
    const active = doc.activeElement;
    if (active && active !== doc.body && active !== docEl) {
      if (slide.contains(active)) return;
      if (!active.closest(SELECTOR.slide)) return;
    }
    try {
      slide.focus({ preventScroll: true });
    } catch (error) {
      slide.focus();
    }
  }

  /* =========================================================================
     Input
     ========================================================================= */

  function isTypingTarget(node) {
    const el = node instanceof Element ? node : null;
    if (!el) return false;
    if (el.isContentEditable) return true;
    if (el.closest("[data-deck-ignore-keys]")) return true;
    const tag = el.tagName;
    return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || tag === "OPTION";
  }

  function clearDigits() {
    global.clearTimeout(digitTimer);
    digitTimer = 0;
    digitBuffer = "";
  }

  function commitDigits() {
    const value = parseInt(digitBuffer, 10);
    clearDigits();
    if (Number.isFinite(value) && value > 0) goTo(value - 1, "key");
  }

  function pushDigit(digit) {
    digitBuffer = (digitBuffer + digit).slice(-DIGIT_MAX_LENGTH);
    global.clearTimeout(digitTimer);
    digitTimer = global.setTimeout(commitDigits, DIGIT_COMMIT_MS);
  }

  function onKeyDown(event) {
    if (event.defaultPrevented) return;
    // Any meta, control or alt chord belongs to the browser or the platform.
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    if (isTypingTarget(event.target)) return;

    const key = event.key;
    let handled = true;

    if (key === "ArrowRight" || key === "PageDown") step(1, "key");
    else if (key === "ArrowLeft" || key === "PageUp") step(-1, "key");
    else if (key === " " || key === "Spacebar") step(event.shiftKey ? -1 : 1, "key");
    else if (key === "Home") goTo(0, "key");
    else if (key === "End") goTo(slides.length - 1, "key");
    else if (key.length === 1 && key >= "0" && key <= "9") pushDigit(key);
    else if (key === "Enter" && digitBuffer) commitDigits();
    else if (key === "Escape" && digitBuffer) clearDigits();
    else handled = false;

    // preventDefault is reserved for keys this runtime actually consumed.
    if (!handled) return;
    event.preventDefault();
    markActivity();
  }

  /**
   * Coarse-pointer tap zones: left third steps back, right third steps
   * forward. The `.deck-tap` elements are decorative and do not take pointer
   * events, so the hit test runs here and yields to interactive slide content.
   */
  function onViewportClick(event) {
    if (!coarseQuery || !coarseQuery.matches) return;
    if (event.button !== 0) return;
    const el = event.target instanceof Element ? event.target : null;
    if (el && el.closest(INTERACTIVE)) return;
    const width = global.innerWidth || STAGE_WIDTH;
    const ratio = event.clientX / width;
    if (ratio <= 1 / 3) step(-1, "pointer");
    else if (ratio >= 2 / 3) step(1, "pointer");
    markActivity();
  }

  function onChromeClick(event) {
    const el = event.target instanceof Element ? event.target : null;
    const trigger = el ? el.closest("[data-deck-nav]") : null;
    if (!trigger) return;
    const direction = trigger.getAttribute("data-deck-nav");
    if (direction === "next") step(1, "pointer");
    else if (direction === "prev") step(-1, "pointer");
    markActivity();
  }

  function onWheel(event) {
    const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
    if (Math.abs(delta) < WHEEL_THRESHOLD) return;
    const now = Date.now();
    if (now - lastWheelAt < WHEEL_COOLDOWN_MS) return;
    lastWheelAt = now;
    step(delta > 0 ? 1 : -1, "wheel");
    markActivity();
  }

  function onPointerMove() {
    const now = Date.now();
    if (now - lastPointerAt < POINTER_ACTIVITY_MS) return;
    lastPointerAt = now;
    markActivity();
  }

  function markActivity() {
    if (!chromeEl) return;
    chromeEl.classList.remove("is-idle");
    global.clearTimeout(idleTimer);
    idleTimer = global.setTimeout(function hideChrome() {
      if (chromeEl.contains(doc.activeElement)) return;
      chromeEl.classList.add("is-idle");
    }, IDLE_HIDE_MS);
  }

  /* =========================================================================
     Preparation and binding
     ========================================================================= */

  function prepare() {
    if (stageEl) {
      if (!stageEl.hasAttribute("role")) stageEl.setAttribute("role", "region");
      if (!stageEl.hasAttribute("aria-label") && !stageEl.hasAttribute("aria-labelledby")) {
        stageEl.setAttribute("aria-label", doc.title ? `${doc.title} slides` : "Deck slides");
      }
    }

    const total = slides.length;
    for (let i = 0; i < total; i += 1) {
      const slide = slides[i];
      slide.setAttribute("tabindex", "-1");
      slide.setAttribute("data-deck-index", String(i));
      if (!slide.hasAttribute("role")) slide.setAttribute("role", "group");
      if (!slide.hasAttribute("aria-roledescription")) {
        slide.setAttribute("aria-roledescription", "slide");
      }
      if (!slide.hasAttribute("aria-label") && !slide.hasAttribute("aria-labelledby")) {
        slide.setAttribute("aria-label", `Slide ${i + 1} of ${total}`);
      }
    }

    if (liveEl) {
      if (!liveEl.hasAttribute("aria-live")) liveEl.setAttribute("aria-live", "polite");
      if (!liveEl.hasAttribute("role")) liveEl.setAttribute("role", "status");
    }
  }

  /** Reduced motion is read from the platform and re-read when it changes. */
  function bindReducedMotion() {
    if (typeof global.matchMedia !== "function") return;
    const query = global.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = function syncReducedMotion() {
      reduceMotion = query.matches;
      docEl.toggleAttribute("data-deck-reduced-motion", reduceMotion);
    };
    sync();
    query.addEventListener("change", sync);
  }

  function bindEvents() {
    global.addEventListener("resize", scheduleFit);
    global.addEventListener("orientationchange", scheduleFit);
    doc.addEventListener("keydown", onKeyDown);
    global.addEventListener("wheel", onWheel, { passive: true });
    global.addEventListener("pointermove", onPointerMove, { passive: true });
    if (viewportEl) viewportEl.addEventListener("click", onViewportClick);
    if (chromeEl) chromeEl.addEventListener("click", onChromeClick);
  }

  /**
   * Wire the deck. Calling this again is a no-op, so an inline call and the
   * automatic DOMContentLoaded call cannot double-bind the listeners.
   */
  function init(options) {
    if (started) return api;
    const scope = (options && options.root) || doc;

    stageEl = scope.querySelector(SELECTOR.stage);
    viewportEl = scope.querySelector(SELECTOR.viewport) || stageEl;
    chromeEl = scope.querySelector(SELECTOR.chrome);
    progressEl = scope.querySelector(SELECTOR.progress);
    counterCurrentEl = scope.querySelector(SELECTOR.counterCurrent);
    counterTotalEl = scope.querySelector(SELECTOR.counterTotal);
    liveEl = scope.querySelector(SELECTOR.live);
    navPrevEls = Array.prototype.slice.call(scope.querySelectorAll(SELECTOR.navPrev));
    navNextEls = Array.prototype.slice.call(scope.querySelectorAll(SELECTOR.navNext));
    coarseQuery = typeof global.matchMedia === "function" ? global.matchMedia("(pointer: coarse)") : null;

    collect();
    prepare();
    bindReducedMotion();
    bindEvents();
    applyFit();
    started = true;

    const deepLink = readHash();
    if (slides.length) applyState(clamp(deepLink === null ? 0 : deepLink), "init");
    else updateChrome();

    markActivity();
    return api;
  }

  /* =========================================================================
     Public API
     ========================================================================= */

  const api = {
    get index() {
      return index;
    },
    get length() {
      return slides.length;
    },
    goTo: function goToIndex(target) {
      return goTo(Number(target), "api");
    },
    next: function nextSlide() {
      return step(1, "api");
    },
    prev: function prevSlide() {
      return step(-1, "api");
    },
    reset: function resetDeck() {
      return goTo(0, "api");
    },
    init: init,
    fit: scheduleFit,
  };

  global.BrainDeck = api;

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", function onReady() {
      init();
    }, { once: true });
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : globalThis);
