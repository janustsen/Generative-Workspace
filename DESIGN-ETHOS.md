# Trus Design Ethos — Visual & Motion Language

> A portable design system distilled from the Trus marketing site (`/Trus Website (New)`).
> Where `SPEC.md` says *how to build this site*, this document says *what makes it look and
> feel like Trus* — so the same ethos can be applied to any surface of the actual product
> (the canvas, generated modules, settings, onboarding, dashboards, anything new).
>
> Every value below is taken from the **shipped implementation** (`src/styles/tokens.css`,
> `src/styles/globals.css`, and the component/hook source), not from intent docs. File and
> line pointers are given so each rule is traceable.
>
> **How to read this:** §1 is the philosophy (the "why" — internalize this first). §2–§7 are
> the concrete system (color, type, space, surface, motion, components). §8 is interaction
> principles. §9 is the accessibility/performance contract. §10 is the **translation guide**:
> how to take all of it to a brand-new product feature.

---

## 1. The Core Ethos — five principles

Everything else is downstream of these. If a new feature honors only these five, it will
already read as Trus.

### 1.1 "Generated, not drawn." Software assembles itself in front of you.
The product's whole promise is that Trus *builds* a workspace for you. The visual language
makes that literal: nothing fades in — **things construct themselves**. A module seeds, draws
its own border, fills, gets scanned by a light pass, then its label wipes on. Subpage content
wipes in left-to-right as it scrolls into view. The thesis sentence — *"Trus is NOT a
workspace. Trus is a platform that GENERATES workspaces."* — is expressed through motion, not
just copy. **When you add anything, ask: does it look authored, or does it look generated?**

### 1.2 Matte restraint, one magenta spark.
The entire palette is charcoal + matte grey. There is exactly **one** brand accent — a vivid
magenta (`#C42E8C`) — and it is rationed hard. It marks *the one action that matters* on any
given screen and almost nothing else. Restraint is the brand: the calm grey field is what
makes the single magenta moment feel like a decision. Neon belongs only inside the opt-in
"refresh" themes (§2.5), never in default UI.

### 1.3 Low information density. Let it breathe.
Spacing runs deliberately loose — Apple-keynote scale, not dashboard scale. Display headings
occupy ~⅓ of the viewport width. Section gaps are large (`.section` = 168px). Type is big and
bold. The product should feel like a premium, unhurried instrument, never a cramped tool.

### 1.4 Real, working software — never mockups.
The home grid's tile backgrounds are functional simulated module UIs (terminals, charts,
spreadsheets, calendars, forms). The "Try it" widgets are genuinely interactive and **synced**
— toggle a meal and the calorie ring, macro bars, and grocery list all recompute live. The
ethos rejects lorem-ipsum and dead screenshots: surfaces show *plausible live state*. Last-mile
execution (modules that hit real APIs) is signaled with small `live` / `API` badges.

### 1.5 Motion is calm and physical, then it gets out of the way.
Animations overshoot slightly (they have weight and spring), but they're brief and they
**finish** — control is handed back to CSS, props are cleared, the UI settles into a still,
legible resting state. Nothing loops distractingly in the user's working area. And the entire
motion layer is a progressive enhancement: under `prefers-reduced-motion` everything renders
instantly in its final state with zero animation.

---

## 2. Color System

All color lives as CSS custom properties in `src/styles/tokens.css`. **Never hardcode a hex
elsewhere** — reference the token. (Historical note: the accent token is named `--accent-blue`
even though the hue is magenta; the name was kept so existing references resolve. Treat
"`--accent-blue`" as "the brand accent.")

### 2.1 Backgrounds (the charcoal stack)
| Token | Value | Role |
|---|---|---|
| `--bg-base` | `#181818` | App background — the canvas everything sits on |
| `--bg-surface` | `#202020` | Card / module / panel surface |
| `--bg-elevated` | `#282828` | Hover state, tooltips, steppers, inset wells |
| `--bg-overlay` | `#101010` | Dim scrim behind zoom/modal transitions |

Elevation is expressed by **getting lighter** (`base → surface → elevated`), plus border and
shadow — not by colored tints. A surface one level up is one step lighter.

### 2.2 Borders (three weights)
| Token | Value | Role |
|---|---|---|
| `--border-subtle` | `#2C2C2C` | Hairline dividers, default card edges, table cells |
| `--border-default` | `#383838` | Standard interactive element border |
| `--border-strong` | `#484848` | Hover/emphasis border, GridIcon color, scrollbar thumb |

The site-wide **one card-hover convention**: a surface card brightens its border from subtle/
default → `--border-strong` on hover. Nothing scales on hover (scale is reserved for drag).
See `globals.css` `.module:hover`, `.contact-card:hover`, `.team-card/.tier/.milestone-card:hover`.

### 2.3 Text (four levels)
| Token | Value | Role |
|---|---|---|
| `--text-primary` | `#F0EFED` | Headings, primary copy (a warm off-white, never pure `#fff`) |
| `--text-secondary` | `#8F8E8B` | Body, supporting copy |
| `--text-muted` | `#4A4A48` | Captions, metadata, eyebrows, disabled |
| `--text-inverse` | `#181818` | Text on a light/accent fill |

Supplementary greys: `--gray-light #C8C7C4` (labels, sublabels, secondary accents),
`--gray-mid #787673`, `--gray-dark #3A3A38`. Primary white is also exposed as `--white-matte`.
**Pure white (`#fff`) appears in exactly two places:** the tiny specular peak of the wordmark
sheen gradient, and text sitting on the magenta fill. Everywhere else, off-white.

### 2.4 The one accent — magenta
```css
--accent-blue:        #C42E8C;                 /* the brand spark */
--accent-blue-hover:  #A82478;                 /* darker, for hover on filled CTAs */
--accent-blue-soft:   rgba(196, 46, 142, 0.82);/* lower alpha — logo dot, hero "generate" */
--accent-blue-line:   rgba(196, 46, 142, 0.78);/* translucent — accent borders */
--accent-blue-glow:   0 6px 24px rgba(196,46,142,0.38); /* the only colored shadow */
```
**Usage law — magenta marks the single primary action and the brand mark, nothing else:**
- Filled CTAs (`Try now →`, `Generate workspace`) use `color-mix(in srgb, var(--accent-blue) 90%, transparent)` — near-solid but a hair translucent so charcoal reads through. White text on top.
- The logo dot and the hero word *generate* use the **softer** `--accent-blue-soft` (lighter weight; the hero word adds a same-hue text halo for legibility, never a neon glow).
- Live/interactive accents inside real widgets (progress fills, the macro ring, checked states, the active canvas node/link, the GridIcon when it marks an active section) use the accent.
- `--accent-blue-glow` is the **only colored shadow** in the system. All other shadows are black.

If you're reaching for the accent a second time on one screen, stop — one of them isn't the
primary action.

### 2.5 Status colors (desaturated, never neon)
Added for the build-stage nodes and terminal tokens. Deliberately muted to sit *inside* the
matte palette:
```css
--status-err:     #D7674F;  --status-err-dim: rgba(215,103,79,0.16);  /* muted terracotta */
--status-ok:      #5FAE7E;  --status-ok-dim:  rgba(95,174,126,0.16);  /* muted sage */
```
Use these (not red/green) for error/success in product surfaces — they keep the charcoal mood.

### 2.6 Neon is quarantined
The eight refresh themes in `src/lib/themes.ts` (Minimal, Cyberpunk, Retro, Colorful, B&W,
Blueprint, Terminal, Paper) are the **only** place saturated/neon color is allowed, and only
because the user explicitly opts in by hitting a module's refresh button. They re-skin a module
via four scoped vars (`--module-bg/-text/-accent/-border`). Default product UI: never neon.

---

## 3. Typography

### 3.1 Fonts (registered in `src/app/layout.tsx`)
- **Geist Sans** (`--font-geist-sans`) — everything: UI, headings, body.
- **Geist Mono** (`--font-geist-mono`) — "machine" texture: metadata, data values, badges,
  terminal/spreadsheet/timeline content, anything that should read as *system output*.
- **Anton** (`--font-anton`) and **DM Serif Display** (`--font-dm-serif`) — loaded **only** for
  the hero wordmark's typeface-swap cycle (§5.1). Subset to latin (the wordmark needs just
  `T R U S`), so the footprint is tiny. Don't reach for these elsewhere.

### 3.2 The weight philosophy: big + bold headers, light body
Hierarchy comes from **weight and size, not color tricks.** Headers/labels are weight **600**;
body is light (**300–400**). The contrast between a heavy heading and airy body copy *is* the
typographic system.

### 3.3 Scale (as shipped, `globals.css`)
| Class / role | Size | Weight | Tracking | Notes |
|---|---|---|---|---|
| `.hero-wordmark` | `clamp(108px, 18vw, 198px)` | 600 | −0.05em | line-height 0.92 |
| `.display` (subpage H1) | `clamp(52px, 6.6vw, 92px)` | 600 | −0.045em | `max-width: 14ch` keeps it ~⅓ screen |
| `.headline` | `clamp(34px, 4.2vw, 50px)` | 600 | −0.03em | section titles |
| `.subhead` | `28px` | 600 | −0.02em | |
| `.body-lg` / `.intro` | `22–23px` | 300–400 | 0 | intro paragraphs, `max-width: 620px` |
| body (base) | `17px` / lh 1.6 | 400 | 0 | `--gray`/secondary for supporting copy |
| `.caption` / eyebrow | `13px` | 400–500 | 0.05em (eyebrows 0.16–0.18em, uppercase) | metadata |
| mono micro | `9–12px` | 400 | 0.04–0.14em | data, badges, module backgrounds |

### 3.4 Casing & tracking laws
- **Always sentence case.** Never title case. The only all-caps strings are the `TRUS`
  wordmark and tracked eyebrow labels (`BUILT AT STANFORD`, `GET EARLY ACCESS`).
- Big type gets **negative tracking** (tighten as it grows: down to −0.05em on the wordmark).
- Small labels/eyebrows/mono get **positive tracking** (`+0.04em` to `+0.18em`) and uppercase.
- Headings carry tight line-height (1.0–1.1); body opens up to 1.55–1.65.
- Eyebrows are a recurring unit: `GridIcon + tracked uppercase 13px label`, often with the
  GridIcon tinted magenta to mark the section.

---

## 4. Spacing, Radii & Layout

### 4.1 Spacing scale (`tokens.css`)
`--gap-xs 4 · --gap-sm 8 · --gap-md 16 · --gap-lg 24 · --gap-xl 48 · --gap-2xl 96` (px).
Macro rhythm is even larger and fluid: sections use `clamp()` in the 96–200px range;
`.section` margin-top is **168px** desktop / 112px mobile. **Default to too much space, then
remove.** Density is a deliberate anti-goal.

### 4.2 Radii (`tokens.css`)
`--radius-sm 4px` (buttons, chips-as-rect, small controls) · `--radius-md 8px` (cards, fields,
nodes) · `--radius-lg 14px` (large panels, the prompt box, tiers). **Grid module tiles are a
flat 18px** (`.module`). Fully-round (`999px`) is reserved for pills/chips and progress tracks.
**No blobby, angled, or hexagonal silhouettes — ever.** Every tile is a clean rounded rectangle,
including mid-drag (a stated invariant in `globals.css`).

### 4.3 Layout primitives
- **Content max-widths:** subpage body `1080px`; grid `1120px`; widgets `1180px`; closing CTA
  `760px`; prose columns `~620px`. Always centered, generous side padding (`48px` desktop,
  `24px` mobile).
- **Fixed header** 56px tall, transparent until scrolled >40px, then
  `rgba(24,24,24,0.85)` + `backdrop-filter: blur(16px)` + subtle bottom border.
- **The grid is the primary nav.** Desktop header is intentionally minimal: logotype left,
  one magenta `Try now →` right, *no other links*. Full route list lives only in the mobile
  drawer. (Lesson for the product: let the work surface be the navigation; keep chrome quiet.)
- **Responsive breakpoints:** mobile `<768px`, tablet `768–1024px`, desktop `>1024px`. A
  notable extra break at `900px` where the draggable widget canvas collapses to a stack.

---

## 5. Motion Language

> This is the soul of the brand. Read §1.1 and §1.5 first. The meta-rule: **construction over
> opacity.** A thing should look like it is being assembled, not like it is being faded in. And
> every animation resolves to a clean, static end state.

### 5.1 Easing & timing tokens (`tokens.css`)
```css
--ease-snap:  cubic-bezier(0.16, 1, 0.3, 1);    /* decisive settle (drawers, progress) */
--ease-out:   cubic-bezier(0.0, 0.0, 0.2, 1);   /* standard reveal */
--ease-build: cubic-bezier(0.34, 1.56, 0.64, 1);/* OVERSHOOT — the signature "spring into place" */
--dur-fast:  0.12s;  --dur-base: 0.28s;  --dur-slow: 0.55s;  --dur-xslow: 0.9s;
```
GSAP equivalents used in JS: `power3.out` (reveals), `power2.inOut` (border draw / zoom),
`back.out(2)` (micro-settle bounce). The overshoot easings are what give Trus motion its
*physical, springy* character — use them for the final "settle" of any constructed element.

### 5.2 The signature animation — module assembly (`src/components/TetrisGrid.tsx`, `Module.tsx`)
The single most important animation. A GSAP timeline runs per tile, staggered ~100ms
(`stagger: 0` on fast return visits). Each tile's six-beat sequence — **memorize this shape; it
is the template for "a thing being generated":**

1. **Seed** (~0.26s, `power3.out`): card drops in from `scale 0.94, y +12, opacity 0` → settled.
2. **Border draws** (~0.26s, `power2.inOut`): an SVG `<rect>` overlay traces itself clockwise
   via `stroke-dashoffset: perimeter → 0`.
3. **Fill** (~0.24s, after border ~60% drawn): the surface and the faded background content fade
   to target opacity (background lands at `0.5`).
4. **Scan sweep** (~0.5s, `power2.inOut`): a narrow translucent light band sweeps L→R
   (`xPercent: -130 → 330`) across the fresh surface — echoes the hero wordmark sheen.
5. **Label wipe** (~0.2s, `power3.out`): the label reveals via `clip-path: inset(0 100% 0 0) →
   inset(0 0% 0 0)`; sublabel, GridIcon, refresh button fade in alongside.
6. **Micro-settle** (~0.14s, `back.out(2)`): `scale 1.015 → 1`, then **`clearProps`** hands
   everything back to CSS (so hover, themes, etc. keep working) and the trace SVG hides.

`fast` variant durations are roughly halved with no stagger (used on return-from-subpage).

### 5.3 Scroll reveal — same philosophy, lighter (`src/hooks/useScrollReveal.ts`)
Subpage content "builds itself" on open and as it scrolls in. Driven by **GSAP
`ScrollTrigger.batch`** (not a hand-rolled IntersectionObserver — that historically left pages
blank). Per block out of `opacity:0, clip-path: inset(0 100% 0 0), y:18, scale:0.985`:
- **Wipe + rise** L→R (`power3.out`) → **micro-settle** `scale 0.994 → 1` (`back.out(2)`).
- **20% rule:** `start: 'top 82%'` — a block builds when its top crosses ~20% up from the
  viewport bottom. `batch` staggers a cluster as a wave (~80ms apart).
- **Velocity-scaled duration:** fast scroll → ~0.2s; slow/on-open → ~0.7s; clamped 0.15–0.8s
  (via `useScrollVelocity`).
- **Reliability contract — content must NEVER stay invisible:** a `ScrollTrigger.refresh()` on
  the next frame and at 300ms, plus a **2.6s failsafe** that force-builds any still-hidden block
  at/above the fold. Apply `data-reveal` to anything that should construct in.

### 5.4 The hero wordmark — "Spider-Verse reform" (`src/components/HeroWordmark.tsx` + `globals.css`)
`TRUS` continuously **reforms**: it swaps typefaces (Geist Sans → Anton → DM Serif → Geist Mono
→ a sans state with a trailing magenta brand dot) and glitches on each switch. Cadence: hold
**540ms**, glitch **150ms**, loop. The glitch stacks four effects in one grid cell:
- **Chromatic channel-split:** cyan (`#36e0e0`) + magenta ghost duplicates offset ±0.055em with
  `mix-blend-mode: screen` (`aria-hidden`).
- **Motion-blur smear** (`hw-smear`, `blur(0→3px→0)`), **datamosh slice** (`hw-slice`, stepped
  `clip-path` insets + x-jitter), **halftone flicker** (a magenta radial-dot pattern clipped to
  the letterforms).
- The readable base layer keeps a **matte sheen gradient** via `background-clip: text` (a soft
  off-white→white→off-white sweep — the same sheen the module scan-sweep echoes).
- **Accessibility:** the visible text is always literally `TRUS`; the `<h1>` semantics are
  intact; under reduced motion it's a single static matte wordmark.

This is the brand's "wow" moment for VC first impressions — a literal demonstration of *form
generation*. The takeaway for the product isn't "glitch everything," it's that **the brand mark
itself is unstable/generative**, and the matte sheen + magenta accents are its DNA.

### 5.5 The Flurry background (`src/hooks/useFlurry.ts`, `FlurryCanvas.tsx`)
A fixed full-viewport `<canvas>` behind all content (`z-index:0, pointer-events:none`) on
**every page**. Calm, low-saturation light-ribbon arcs (à la macOS "Flurry") that spawn at an
edge, drift along a `quadraticCurveTo` Bezier path, and dissolve via a `sin(life·π)` opacity
envelope before crossing. Tunables:
- 18–24 active arcs desktop, **10 on mobile**; speed mult `1` desktop / `0.3` mobile.
- Stroke width 1.2–3px; peak opacity **0.10–0.22** (calm but visible); per-arc shade jittered
  ±8/channel from a 4-color palette: matte white (weighted dominant), cool blue-white
  `[190,206,236]`, warm sand-white `[236,224,203]`, cool slate `[150,159,174]`.
- Gradient stroke fades transparent→tint→transparent along each arc.
- 60fps delta-capped rAF; an `accelerate()` burst (4× speed + brightness for 0.2s) fires on the
  generate-click flourish.
- **Reduced motion: render nothing, stop the loop entirely.**

It's the atmospheric signature — a living-but-calm field. A product surface can carry it (or a
quieter variant) to stay unmistakably Trus without adding noise to the work area.

### 5.6 The cursor ripple (`src/components/CursorFlux.tsx`)
A single calm magenta ring on **left-click only** — radius ≤20px, expands `easeOutCubic`, fades
once (440ms), thin 1.4px stroke with a soft same-color shadow. **No cursor-follow trail** (a
deliberate restraint — one too many effects was removed). Disabled on coarse pointers / touch /
reduced motion. The interaction-feedback ethos: *one quiet acknowledgement, tied to the brand
color, never a particle storm.*

### 5.7 Smaller motion vocabulary (catalog)
| Effect | Where | Recipe |
|---|---|---|
| iOS "wiggle" | sibling tiles during drag | `rotate(-0.6deg ↔ 0.6deg)` 0.4s infinite |
| Attention pulse | the Generate button | expanding magenta ring `box-shadow 0→12px` 2s |
| Progress sweep loader | post-generate | `scaleX(0→1)` 1.15s, magenta gradient bar |
| Skeleton shimmer | result-card placeholders | 200% gradient slide 1.4s linear |
| Core pulse | the orchestration "engine" node | `box-shadow 0→8px` ring, 1.8s |
| Caret blink | typewriter / form fields | stepped opacity, ~1.05s |
| Bar grow / line draw | stats backgrounds | `scaleY(0→1)` / `stroke-dashoffset` draw |
| Card drift | product-canvas cards | ±2px `translateY` over 6s, unique phase |

Common thread: **brief, looping only where decorative/ambient, easing with weight, and silenced
under reduced motion.**

---

## 6. Surface, Elevation & Texture

- **Cards/panels** = `--bg-surface` + 1px `--border-subtle`/`-default` + a radius from §4.2.
  Padding is generous (subpage cards ~40px). Hover brightens the border to `--border-strong`.
- **Glass** is used sparingly for floating chrome: the scrolled header and the prompt box use
  `rgba(...,0.55–0.85)` + `backdrop-filter: blur(6–16px)`.
- **Shadows are black and soft**, scaled to elevation: cards `0 18px 60px rgba(0,0,0,0.28)`;
  lifted drag clone `0 26px 80px rgba(0,0,0,0.6)`; CTAs `0 10–14px 30–40px rgba(0,0,0,0.3–0.4)`.
  The **only colored shadow** is `--accent-blue-glow` on the primary CTA hover and live accents.
- **`--glow-white`** (`0 0 24px / 60px` faint white) is the matte hover glow — used on matte
  CTAs (hero, subpage `.cta-btn`) so they lift without color.
- **Dotted-grid texture** signals "the Trus canvas": `radial-gradient(... 1px, transparent 1px)`
  at 24–26px on the try-it canvas (`.try-canvas`) and the product canvas (`.pcanvas-stage`).
  Reuse this dot field whenever you depict the infinite canvas.
- **The GridIcon motif** (`src/components/GridIcon.tsx`): a 2×2 of tiny rounded squares. It is
  the unifying brand glyph — top-left of every module, in every eyebrow, on the back button, in
  the footer. Default color `--border-strong`; tinted magenta when it marks an active/primary
  context. Put it wherever you need a quiet "this is Trus" stamp.

---

## 7. Component Patterns

### 7.1 Buttons — a strict two-tier system
- **Primary (filled magenta):** `Try now →`, `Generate workspace`. Fill =
  `color-mix(in srgb, var(--accent-blue) 90%, transparent)`, white text, weight 500–600,
  translucent accent border, hover → `--accent-blue-hover` + `--accent-blue-glow`, active →
  `translateY(1px)`. **Exactly one per screen.**
- **Matte secondary:** transparent, 1px `--white-matte` or `--border-strong` border, hover adds
  `--glow-white` or a 4% white wash. Used for *everything that isn't the single primary action*
  (hero `See it generate ↓`, `See the full product →`, subpage CTAs).
- Radii: `sm`/`md`. Letter-spacing `0.01–0.06em`. The hierarchy is **filled-magenta vs
  outline-matte** — there is no third button style.

### 7.2 Inputs & chips
- **Prompt field** (`.clay-prompt-box`): the hero input pattern — large (`clamp(16px,2.2vw,21px)`),
  glass surface, radius-lg, `0 18px 60px` shadow, focus brightens border, a magenta-tinted
  border when it's the gated active element. A blinking `--white-matte` caret.
- **Chips** (`.clay-chip`): fully-round pills, `--bg-surface` + `--border-default`, secondary
  text; selected state = brighter text + white border + elevated bg. Use for example presets/
  quick options.

### 7.3 Data display (the "machine" register)
Anything that represents data/state uses **Geist Mono**, small sizes, tracked: metadata rows,
key-values, badges (`live`/`API`/`ok`), table cells, terminal lines, timeline dates, calorie/
macro readouts. Badges are tiny uppercase mono in a tinted pill (`--status-ok-dim` etc.).
Progress is a 4px rounded track (`--bg-elevated`) with a magenta fill + glow, eased `--ease-snap`.

### 7.4 The "real module" pattern (for generated UIs)
When you render a generated module, follow the home-grid/widget anatomy:
- Surface card, GridIcon top-corner, a 600-weight label, a mono meta line, and **functional
  interactive content** that reflects live state.
- If a module executes a real task via an API, badge it (`· live` / `· API`).
- Keep one magenta interactive accent (the checkbox, ring, progress) and let the rest stay grey.
- **Sync is a feature:** when modules share data, changing one should visibly update the others
  in real time (see `WidgetsSection.tsx` — meal plan → nutrition ring + macro bars + grocery
  list, all derived, all `--ease-snap` transitioned).

### 7.5 Eyebrow + heading + intro (the section header unit)
Reusable block: `[GridIcon + tracked uppercase eyebrow]` → `[600-weight heading]` →
`[light 22–23px intro, max-width ~620px, secondary color]`. This is how every section and
subpage opens.

---

## 8. Interaction Principles

### 8.1 Direct manipulation everywhere
Tiles drag to rearrange (`@dnd-kit/sortable`), widgets drag freely on a canvas, order persists
to `localStorage`. The mechanics encode taste worth carrying into the product:
- **Translate-only transforms, never scale** — scaling differently-sized tiles distorts their
  text. The lifted item is a fixed-size `DragOverlay` clone; the original is hidden; a dashed
  placeholder shows the molded landing slot.
- **Live reorder** — the grid reflows *as you drag over*, so the final layout is visible before
  you drop (no jarring post-drop snap). Cancel reverts to the pre-drag snapshot.
- Lift is conveyed by **shadow alone** (`0 26px 80px rgba(0,0,0,0.6)`), plus sibling wiggle.
- 5px pointer activation distance so a click still reads as a click, not a drag.

### 8.2 Spatial transitions (zoom, not cut)
Module → subpage is a clone-expand over a dim `--bg-overlay` scrim (`ZoomTransition.tsx`): the
clicked card's rect is cloned, the rest of the page fades down, the clone expands to fullscreen
(`power2.inOut`, 0.45s) while the route pushes, then cross-fades to reveal the page **at its
top**. Back restores the **exact saved scroll position**. Principle: **navigation is a physical
zoom through space, never a hard cut or white flash.**

### 8.3 Earn the payoff — gating
The "how it works" demo is **soft-locked**: while it fills the screen, downward scroll is held
and fills a circular skip ring ("release to skip demo" at full); Generate or up-scroll releases
it, and it never re-locks for the visit. Off on mobile + reduced motion; keyboard is never
blocked. The lesson is not "trap the user" — it's that **the key generative action gets weight
and ceremony** (a prominent pulsing button, a brief loader, then the construction). Make the
moment Trus *generates* something feel deliberate and rewarding.

### 8.4 WYSIWYG honesty
The prompt box is **prefilled with exactly what Generate will build** — no cycling ghost that
implies one thing while building another (that pattern was explicitly removed). What the user
sees is what they get. Carry that honesty into product affordances.

---

## 9. Accessibility & Performance Contract

Non-negotiable, and part of the aesthetic (calm = respectful):
- **`prefers-reduced-motion: reduce`** → Flurry renders nothing; all GSAP no-ops; the wordmark
  is static; `[data-reveal]` content is fully visible; a global rule crushes all
  animation/transition durations to `0.01ms`. Every feature must have a correct, complete
  static end-state.
- **Focus:** `:focus-visible` = `2px solid var(--white-matte)` + 2px offset, everywhere.
- **Semantics preserved through effects:** decorative layers are `aria-hidden`; the wordmark
  stays a real `<h1>` reading `TRUS`; typewriter exposes a stable resting phrase to SRs; live
  regions announce "Generating…"/completion; drag has keyboard sensors; canvas effects are
  `pointer-events: none` so they never block interaction.
- **Performance:** rAF loops are 60fps delta-capped; DPR clamped to 2; mobile reduces Flurry
  arc count/speed and disables ambient background animations; `will-change` only on actively
  animating props, cleared on completion; below-the-fold content lazy-reveals.
- **No file > 50MB** (split or reference by URL); video assets are git-ignored.
- SSR-safe: server and first client paint must match (typewriter starts empty, grid default
  state is deterministic) — no hydration mismatches.

---

## 10. Applying This to the Product — translation guide

When you build any new Trus surface (a generated module, a settings pane, an onboarding step, a
dashboard, a canvas tool), run it through this checklist. If you can answer all of these "yes,"
it will look and feel like Trus.

**Color & surface**
- [ ] Background uses the charcoal stack (`base → surface → elevated`); elevation via lightness +
      border + black shadow, not tints.
- [ ] Exactly **one** magenta primary action on the screen; everything else matte grey.
- [ ] Borders from the three-weight scale; hover brightens to `--border-strong`; nothing scales
      on hover.
- [ ] Off-white text (`--text-primary`), never pure white except on magenta fills.
- [ ] Errors/success use the muted terracotta/sage status tokens, not neon red/green.

**Type & space**
- [ ] Geist Sans for UI, Geist Mono for any data/metadata/state.
- [ ] Headings weight 600 with negative tracking; body light (300–400) with positive tracking on
      small labels; **sentence case** throughout.
- [ ] Generous spacing — err toward too much; large section gaps; content in a centered
      max-width column.

**Motion**
- [ ] New elements **construct themselves** (seed → border/fill → settle), they don't just fade.
- [ ] Reveals use `power3.out`; final settles overshoot (`back.out(2)` / `--ease-build`); then
      props are cleared to a clean static state.
- [ ] Durations from the token scale; ambient loops only where decorative.
- [ ] A complete, correct **reduced-motion** static rendering exists.

**Interaction**
- [ ] Direct manipulation where it makes sense (drag = translate-only + overlay clone +
      persisted state).
- [ ] Spatial zoom transitions, no hard cuts/white flashes; back restores prior position.
- [ ] The primary *generative* action gets weight/ceremony and a short, honest loader.
- [ ] Real, live, synced state — never static mockups; badge real API execution.

**Identity**
- [ ] The GridIcon motif appears as the quiet brand stamp.
- [ ] Canvas surfaces carry the dotted-grid texture.
- [ ] Optionally, the calm Flurry field (or a quieter variant) sits behind the work.
- [ ] The brand mark/feel is *generative* — Trus assembles; it doesn't just display.

---

### Source map (where each rule lives)
| Concern | Files |
|---|---|
| Tokens (color, space, radii, easing) | `src/styles/tokens.css` |
| All component CSS, keyframes, responsive, a11y | `src/styles/globals.css` |
| Fonts, providers, global chrome | `src/app/layout.tsx` |
| Module assembly timeline + drag | `src/components/TetrisGrid.tsx`, `Module.tsx` |
| Scroll reveal / velocity | `src/hooks/useScrollReveal.ts`, `useScrollVelocity.ts` |
| Hero wordmark glitch | `src/components/HeroWordmark.tsx` |
| Typewriter | `src/hooks/useTypewriter.ts`, `HeroSection.tsx` |
| Flurry background | `src/hooks/useFlurry.ts`, `FlurryCanvas.tsx`, `FlurryBackground.tsx` |
| Cursor ripple | `src/components/CursorFlux.tsx` |
| Zoom transition | `src/components/ZoomTransition.tsx`, `context/TransitionContext.tsx` |
| Gated generate demo | `src/components/DigitalClaySection.tsx` |
| Synced real widgets | `src/components/WidgetsSection.tsx` |
| Refresh themes (quarantined neon) | `src/lib/themes.ts` |
| GridIcon motif | `src/components/GridIcon.tsx` |

> Full per-component build behavior and the canonical subpage copy live in `SPEC.md`. This
> document is the *design language* abstracted out of it — the part meant to travel to the
> product.
