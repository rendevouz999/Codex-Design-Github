#!/usr/bin/env node
/**
 * Smoke tests for the Brain Design Web Deck tool chain.
 *
 * Framework-free: a small case runner, one progress line per check, a pass and
 * fail counter. Every temp artifact is written under the OS temp directory and
 * removed afterwards; nothing is ever written inside the repo.
 *
 * Exit codes: 0 all checks pass, 1 any check fails.
 */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAN_TOOL = path.join(ROOT, "skills", "presentation-deck", "runtime", "web", "design_brain_web_deck_plan.mjs");
const AUDIT_TOOL = path.join(ROOT, "skills", "presentation-deck", "runtime", "web", "design_brain_web_deck_audit.mjs");
const KIT_DIR = path.join(ROOT, "skills", "presentation-deck", "resources", "web-deck");

/** Fonts are the only external host a generated deck may reference. */
const ALLOWED_HOSTS = new Set(["fonts.googleapis.com", "fonts.gstatic.com"]);

const smoke = { passed: 0, failed: 0 };

function check(label, condition, detail) {
  if (condition) {
    smoke.passed += 1;
    process.stdout.write(`PASS  ${label}\n`);
    return true;
  }
  smoke.failed += 1;
  process.stdout.write(`FAIL  ${label}\n`);
  if (detail) process.stdout.write(`      ${String(detail).split("\n").slice(0, 6).join("\n      ")}\n`);
  return false;
}

function run(tool, args) {
  const completed = spawnSync(process.execPath, [tool, ...args], {
    cwd: ROOT,
    encoding: "utf8",
    timeout: 60000,
  });
  const stdout = completed.stdout || "";
  let payload = null;
  try {
    payload = JSON.parse(stdout);
  } catch (error) {
    payload = null;
  }
  return { code: completed.status, stdout, stderr: completed.stderr || "", payload };
}

async function writeJson(filePath, value) {
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function main() {
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "brain-web-deck-smoke-"));
  try {
    /* A. Runtime kit ---------------------------------------------------- */

    const kit = {};
    let kitPresent = true;
    for (const name of ["stage-base.css", "deck-runtime.js", "deck-plan-schema.json"]) {
      try {
        kit[name] = await fs.readFile(path.join(KIT_DIR, name), "utf8");
      } catch (error) {
        kitPresent = false;
      }
    }
    check("A1. Runtime kit files exist in `.design-brain/web-deck`", kitPresent, `missing under ${KIT_DIR}`);
    if (!kitPresent) return 1;

    /* B. Demo deck ------------------------------------------------------ */

    const deck = path.join(tmp, "deck.html");
    const build = run(PLAN_TOOL, ["--demo", "--out", deck, "--json"]);
    check("B1. Demo plan builds a deck", build.code === 0 && build.payload && build.payload.status === "PASS", build.stderr || build.stdout);
    if (build.code !== 0) return 1;

    const planPath = build.payload.planOut;
    check("B2. Demo run writes the sidecar deck plan", Boolean(planPath) && (await exists(planPath)), `planOut: ${planPath}`);

    const html = await fs.readFile(deck, "utf8");
    check(
      "B3. `stage-base.css` is inlined verbatim",
      html.includes(kit["stage-base.css"].trimEnd()),
      "the generated deck does not contain the kit stylesheet byte for byte"
    );
    check(
      "B4. `deck-runtime.js` is inlined verbatim",
      html.includes(kit["deck-runtime.js"].trimEnd()),
      "the generated deck does not contain the kit runtime byte for byte"
    );
    check(
      "B5. No `<link>` or `<script src>` back to the repo kit",
      !/stage-base\.css"/.test(html) && !/deck-runtime\.js"/.test(html),
      "the deck references the kit by path instead of inlining it"
    );

    const hosts = new Set([...html.matchAll(/https?:\/\/([^/"'\s)<>]+)/g)].map((match) => match[1].toLowerCase()));
    const foreign = [...hosts].filter((host) => !ALLOWED_HOSTS.has(host));
    check(
      "B6. The only external hosts are the allowed font hosts",
      foreign.length === 0 && !/<script\b[^>]*\bsrc\s*=/i.test(html),
      `foreign hosts: ${foreign.join(", ") || "none"}`
    );

    /* C. Audit of the demo deck ----------------------------------------- */

    const audit = run(AUDIT_TOOL, [deck, "--json"]);
    check(
      "C1. The demo deck passes the audit with zero P0",
      audit.code === 0 && audit.payload && audit.payload.status === "PASS" && audit.payload.p0Count === 0,
      audit.stdout || audit.stderr
    );
    check(
      "C2. The demo deck passes the audit with zero findings at all",
      Boolean(audit.payload) && audit.payload.findingCount === 0,
      audit.payload ? JSON.stringify(audit.payload.findings, null, 2) : audit.stderr
    );

    const auditWithPlan = run(AUDIT_TOOL, [deck, "--plan", planPath, "--json"]);
    check(
      "C3. The demo deck passes the plan-relative audit with zero findings",
      auditWithPlan.code === 0 && auditWithPlan.payload && auditWithPlan.payload.findingCount === 0,
      auditWithPlan.payload ? JSON.stringify(auditWithPlan.payload.findings, null, 2) : auditWithPlan.stderr
    );

    const human = run(AUDIT_TOOL, [deck]);
    check("C4. Human output is Markdown-ish, not JSON", human.code === 0 && human.stdout.startsWith("# Web Deck Static Audit"), human.stdout.slice(0, 120));

    /* D. Broken decks are blocked --------------------------------------- */

    const toggled = path.join(tmp, "display-toggled.html");
    await fs.writeFile(
      toggled,
      html.replace("</style>", ".deck-slide { display: none; }\n.deck-slide.is-active { display: flex; }\n</style>"),
      "utf8"
    );
    const toggledAudit = run(AUDIT_TOOL, [toggled, "--json"]);
    check(
      "D1. A display-toggled deck is BLOCKED",
      toggledAudit.code === 2 &&
        toggledAudit.payload &&
        toggledAudit.payload.status === "BLOCKED" &&
        toggledAudit.payload.findings.some((finding) => finding.id === "slide-switch-no-display-toggle"),
      toggledAudit.stdout || toggledAudit.stderr
    );

    const noReduced = path.join(tmp, "no-reduced-motion.html");
    await fs.writeFile(
      noReduced,
      html.replace("@media (prefers-reduced-motion: reduce)", "@media (prefers-contrast: more)"),
      "utf8"
    );
    const reducedAudit = run(AUDIT_TOOL, [noReduced, "--json"]);
    check(
      "D2. A deck with no reduced-motion block is BLOCKED",
      reducedAudit.code === 2 &&
        reducedAudit.payload &&
        reducedAudit.payload.findings.some((finding) => finding.id === "reduced-motion-block"),
      reducedAudit.stdout || reducedAudit.stderr
    );

    const remote = path.join(tmp, "remote-script.html");
    await fs.writeFile(
      remote,
      html.replace("</head>", '<script src="https://cdn.example.net/remote-bundle.js"></script>\n</head>'),
      "utf8"
    );
    const remoteAudit = run(AUDIT_TOOL, [remote, "--json"]);
    check(
      "D3. A deck with a remote script is BLOCKED",
      remoteAudit.code === 2 &&
        remoteAudit.payload &&
        remoteAudit.payload.findings.some((finding) => finding.id === "external-requests-fonts-only"),
      remoteAudit.stdout || remoteAudit.stderr
    );

    const breakpoint = path.join(tmp, "breakpoint.html");
    await fs.writeFile(
      breakpoint,
      html.replace(
        "</style>",
        "@media (max-width: 900px) { .deck-slide { padding: 24px; } .deck-headline { font-size: 32px; } }\n</style>"
      ),
      "utf8"
    );
    const breakpointAudit = run(AUDIT_TOOL, [breakpoint, "--json"]);
    check(
      "D4. A deck with a stage breakpoint is BLOCKED",
      breakpointAudit.code === 2 &&
        breakpointAudit.payload &&
        breakpointAudit.payload.findings.some((finding) => finding.id === "no-stage-breakpoints"),
      breakpointAudit.stdout || breakpointAudit.stderr
    );

    /* E. Invalid plans are rejected ------------------------------------- */

    const demoPlan = JSON.parse(await fs.readFile(planPath, "utf8"));

    const missingKey = path.join(tmp, "missing-slides.json");
    const withoutSlides = { ...demoPlan };
    delete withoutSlides.slides;
    await writeJson(missingKey, withoutSlides);
    const missingRun = run(PLAN_TOOL, ["--plan", missingKey, "--out", path.join(tmp, "x.html"), "--json"]);
    check(
      "E1. A plan with no `slides` key is BLOCKED with exit 2",
      missingRun.code === 2 && missingRun.payload && missingRun.payload.status === "BLOCKED",
      missingRun.stdout || missingRun.stderr
    );

    const badEnum = path.join(tmp, "bad-enum.json");
    await writeJson(badEnum, { ...demoPlan, densityMode: "skimmable" });
    const badEnumRun = run(PLAN_TOOL, ["--plan", badEnum, "--out", path.join(tmp, "y.html"), "--json"]);
    check(
      "E2. A bad `densityMode` enum is BLOCKED with exit 2",
      badEnumRun.code === 2 && badEnumRun.payload && badEnumRun.payload.errors.some((error) => error.includes("densityMode")),
      badEnumRun.stdout || badEnumRun.stderr
    );

    const badSlide = path.join(tmp, "bad-slide.json");
    const slides = demoPlan.slides.map((slide) => ({ ...slide }));
    delete slides[2].headline;
    slides[3].archetype = "mega-hero";
    await writeJson(badSlide, { ...demoPlan, slides });
    const badSlideRun = run(PLAN_TOOL, ["--plan", badSlide, "--out", path.join(tmp, "z.html"), "--json"]);
    check(
      "E3. Slide-level shape errors are BLOCKED with exit 2",
      badSlideRun.code === 2 &&
        badSlideRun.payload &&
        badSlideRun.payload.errors.some((error) => error.includes("slides[2]")) &&
        badSlideRun.payload.errors.some((error) => error.includes("slides[3].archetype")),
      badSlideRun.stdout || badSlideRun.stderr
    );

    const orphanStep = path.join(tmp, "orphan-step.json");
    const orphanSlides = demoPlan.slides.map((slide) => ({ ...slide }));
    orphanSlides[1] = { ...orphanSlides[1], revealOrder: [...orphanSlides[1].revealOrder, "item-9"] };
    await writeJson(orphanStep, { ...demoPlan, slides: orphanSlides });
    const orphanRun = run(PLAN_TOOL, ["--plan", orphanStep, "--out", path.join(tmp, "o.html"), "--json"]);
    check(
      "E4. A reveal step with nothing to reveal is BLOCKED with exit 2",
      orphanRun.code === 2 && orphanRun.payload && orphanRun.payload.errors.some((error) => error.includes("item-9")),
      orphanRun.stdout || orphanRun.stderr
    );

    check(
      "E5. A blocked plan writes no deck",
      !(await exists(path.join(tmp, "x.html"))) && !(await exists(path.join(tmp, "z.html"))),
      "the plan tool wrote an output file for a rejected plan"
    );

    /* F. Valid plan round trip ------------------------------------------ */

    const rebuilt = path.join(tmp, "rebuilt.html");
    const rebuild = run(PLAN_TOOL, ["--plan", planPath, "--out", rebuilt, "--json"]);
    check("F1. The sidecar plan rebuilds the same deck", rebuild.code === 0, rebuild.stderr || rebuild.stdout);
    if (rebuild.code === 0) {
      const rebuiltHtml = await fs.readFile(rebuilt, "utf8");
      check("F2. The rebuild is byte-identical to the demo deck", rebuiltHtml === html, `${rebuiltHtml.length} vs ${html.length} bytes`);
    }

    const dry = run(PLAN_TOOL, ["--plan", planPath, "--out", path.join(tmp, "dry.html"), "--dry-run", "--json"]);
    check(
      "F3. `--dry-run` validates and writes nothing",
      dry.code === 0 && dry.payload && dry.payload.dryRun === true && !(await exists(path.join(tmp, "dry.html"))),
      dry.stdout || dry.stderr
    );

    /* G. Usage errors --------------------------------------------------- */

    const noSource = run(PLAN_TOOL, ["--out", path.join(tmp, "none.html")]);
    check("G1. The plan tool exits 1 with no plan and no --demo", noSource.code === 1, noSource.stderr);
    const noDeck = run(AUDIT_TOOL, ["--json"]);
    check("G2. The audit tool exits 1 with no deck path", noDeck.code === 1, noDeck.stderr);
    const missingDeck = run(AUDIT_TOOL, [path.join(tmp, "absent.html"), "--json"]);
    check("G3. The audit tool exits 1 on an unreadable deck", missingDeck.code === 1, missingDeck.stderr);
  } finally {
    await fs.rm(tmp, { recursive: true, force: true });
  }

  const total = smoke.passed + smoke.failed;
  if (smoke.failed) {
    process.stdout.write(`\nFAIL: Brain Design web deck smoke (${smoke.failed} of ${total} checks failed)\n`);
    return 1;
  }
  process.stdout.write(`\nPASS: Brain Design web deck smoke (${total} checks)\n`);
  return 0;
}

async function exists(filePath) {
  if (!filePath) return false;
  try {
    await fs.access(filePath);
    return true;
  } catch (error) {
    return false;
  }
}

main().then(
  (code) => {
    process.exit(code);
  },
  (error) => {
    process.stdout.write(`\nFAIL: Brain Design web deck smoke crashed: ${error && error.stack ? error.stack : error}\n`);
    process.exit(1);
  }
);
