# Club 33 Design System Reference

This document records the visual system found in the workspace for the Club 33 / Hearthside canteen application. It distinguishes the active SCSS theme from alternate and legacy stylesheets so that design values are not mistaken for one coherent, globally applied theme.

## 1. Active Theme and Source of Truth

### Active page layouts

The registered customer pages render templates extending `base.html`; the current admin pages extend `admin_base.html`. Both load Bootstrap 5 from a CDN and then link to `static/scss/main.css`.

The active Sass entry point is [`app/static/scss/main.scss`](app/static/scss/main.scss). It imports `abstracts/_variables.scss`, then the base, component, layout, and utility modules. The corresponding currently linked compiled stylesheet is [`app/static/scss/main.css`](app/static/scss/main.css).

### Competing and legacy assets

| Asset | Observed role |
|---|---|
| `app/static/scss/abstracts/_variables.scss` | Variables imported by the active Sass entry point; primary source for the active token palette. |
| `app/static/scss/main.css` | Compiled CSS linked by the active customer and admin base templates. |
| `app/static/scss/main..css` | Alternate stylesheet linked by `base2.html` and `admin_base2.html`; based on a different palette and typography variant. |
| `app/static/css/custom.css` | Separate Bootstrap-variable override; the link is commented out in the base template and it is not the active theme source. |
| `app/static/css/main.css` and `app/static/css/main..css` | Additional generated/alternate CSS artifacts. They contain palette values that differ from the active SCSS output. |
| `app/static/scss/abstracts/_variables1.scss`, `_variables3.scss` | Alternate token sets; not imported by the active `main.scss`. |
| `app/static/scss/components/_badges2.scss` | Alternate status-pill rules; not imported by active `main.scss`. |

`run.py` compiles from `app/static/scss` into `app/static/css` in debug mode, while the active base templates link to `app/static/scss/main.css`. This source/output path mismatch can leave the served stylesheet stale after Sass compilation.

## 2. Color Palette

The active token file expresses most palette colors as HSL. The Hex and RGB columns below are the corresponding opaque sRGB values, rounded to the nearest integer channel. They are derived from the active HSL token values rather than from comments that may describe older hex values.

### Active palette tokens

| Token | HSL source | Hex | RGB | Intended role |
|---|---|---:|---:|---|
| `$terracotta-100` | `hsl(12, 52%, 94%)` | `#F8EBE8` | `248, 235, 232` | Pale warm tint, badges and selected states |
| `$terracotta-200` | `hsl(12, 52%, 84%)` | `#EBC9C1` | `235, 201, 193` | Warm hover tint |
| `$terracotta-500` / `$brand-primary` | `hsl(12, 52%, 55%)` | `#C86851` | `200, 104, 81` | Brand/action primary |
| `$terracotta-600` | `hsl(12, 52%, 45%)` | `#AE4F37` | `174, 79, 55` | Darkened active/action state |
| `$terracotta-700` / `$brand-primary-dark` | `hsl(12, 52%, 35%)` | `#883D2B` | `136, 61, 43` | Deep brick, active text/actions |
| `$sage-100` | `hsl(102, 12%, 94%)` | `#EFF2EE` | `239, 242, 238` | Pale success badge background |
| `$sage-500` / `$brand-secondary` | `hsl(102, 12%, 56%)` | `#899C81` | `137, 156, 129` | Sage accent and completed badge text |
| `$sage-700` | `hsl(102, 12%, 36%)` | `#576751` | `87, 103, 81` | Dark sage action hover |
| `$neutral-50` | `hsl(0, 0%, 100%)` | `#FFFFFF` | `255, 255, 255` | White text and raised surfaces |
| `$neutral-100` | `hsl(35, 30%, 96%)` | `#F8F5F2` | `248, 245, 242` | Sunken/search surface and hover surface |
| `$neutral-200` | `hsl(35, 30%, 88%)` | `#EAE2D7` | `234, 226, 215` | Canvas/page background |
| `$neutral-300` | `hsl(35, 25%, 85%)` | `#E2DACF` | `226, 218, 207` | Subtle borders |
| `$neutral-500` | `hsl(30, 8%, 45%)` | `#7C736A` | `124, 115, 106` | Secondary/muted text |
| `$neutral-800` | `hsl(30, 8%, 20%)` | `#37332F` | `55, 51, 47` | Sass `$body-color` token |
| `$neutral-900` | `hsl(30, 4%, 17%)` | `#2D2B2A` | `45, 43, 42` | Headline/primary text; active CSS body text |
| `$amber-100` | `hsl(32, 95%, 94%)` | `#FEF1E1` | `254, 241, 225` | Pale warning badge background |
| `$amber-500` | `hsl(32, 95%, 44%)` | `#DB7706` | `219, 119, 6` | Warning/accent |
| `$crimson-100` | `hsl(0, 71%, 94%)` | `#FBE5E5` | `251, 229, 229` | Pale destructive/cancelled badge background |
| `$crimson-500` | `hsl(0, 71%, 38%)` | `#A61C1C` | `166, 28, 28` | Destructive/cancelled text |
| `$success-100` | `hsl(140, 38%, 94%)` | `#EAF6EE` | `234, 246, 238` | Success tint token |
| `$success-500` | `hsl(140, 38%, 45%)` | `#479E64` | `71, 158, 100` | Success token |
| `$status-info` | `hsl(207, 28%, 40%)` | `#496983` | `73, 105, 131` | Slate-blue informational token |

### Active order status pills

The active implementation is in [`app/static/scss/components/_badges.scss`](app/static/scss/components/_badges.scss), imported by `main.scss`. These selectors are emitted in the linked `main.css`.

| Status class | Background | Text | Border | Notes |
|---|---|---|---|---|
| `.status-pill.status-completed` | `#EFF2EE` / `rgb(239, 242, 238)` | `#899C81` / `rgb(137, 156, 129)` | `rgba(137, 156, 129, 0.25)` | Sage success treatment |
| `.status-pill.status-pending` | `#F8EBE8` / `rgb(248, 235, 232)` | `#883D2B` / `rgb(136, 61, 43)` | `rgba(200, 104, 81, 0.25)` | Terracotta pending treatment |
| `.status-pill.status-cancelled` | `#FBE5E5` / `rgb(251, 229, 229)` | `#A61C1C` / `rgb(166, 28, 28)` | `rgba(166, 28, 28, 0.25)` | Crimson cancelled treatment |
| `.status-pill.status-ready` | Not specifically defined | Not specifically defined | Not specifically defined | No `.status-ready` rule exists in the active badge module. It receives the base `.status-pill` styling only. |
| `.status-pill.status-confirmed` | Not specifically defined | Not specifically defined | Not specifically defined | No `.status-confirmed` rule exists in the active badge module. It receives the base `.status-pill` styling only. |

The base `.status-pill` uses the Inter stack, `0.75rem` font size, weight `500`, `0.35rem 0.75rem` padding, and the small project radius. The current history partial emits `status-pill status-<order status>`, so a `ready` order does not acquire a distinct color treatment from the active stylesheet.

### Alternate/legacy colors

These are defined in alternate assets and should not be treated as the active palette:

| Asset/value | Hex and RGB | Notes |
|---|---|---|
| `_variables1.scss` `$brand-primary` | `#C86B53` / `rgb(200, 107, 83)` | Older hand-entered terracotta; differs from active HSL primary `#C86851`. |
| `_variables1.scss` `$brand-secondary` | `#8B9D83` / `rgb(139, 157, 131)` | Older sage; differs from active HSL sage `#899C81`. |
| `_variables1.scss` `$brand-tertiary` | `#EBE4D8` / `rgb(235, 228, 216)` | Older canvas; differs from active HSL canvas `#EAE2D7`. |
| `_variables1.scss` `$brand-neutral` | `#2C2B29` / `rgb(44, 43, 41)` | Older charcoal; differs from active headline color `#2D2B2A`. |
| `_variables1.scss` `$brand-cream` | `#FAF7F2` / `rgb(250, 247, 242)` | Legacy warm cream surface. |
| `_variables1.scss` `$brand-off-white` | `#F9F8F6` / `rgb(249, 248, 246)` | Legacy off-white. |
| `_variables1.scss` `$brand-alabaster` | `#F7F4F0` / `rgb(247, 244, 240)` | Legacy canvas token. |
| `custom.css` `--bs-primary` | `#B55D44` / `rgb(181, 93, 68)` | Separate Bootstrap override, not linked by the active base templates. |
| `custom.css` `--bs-body-bg` | `#F4F1E9` / `rgb(244, 241, 233)` | Separate warm background override. |
| `custom.css` `--bs-body-color` | `#4A4036` / `rgb(74, 64, 54)` | Separate dark-wood text override. |
| `base3.html` inline body style | Background `#FAF7F2` / `rgb(250, 247, 242)`; text `#2D2319` / `rgb(45, 35, 25)` | Direct style on an alternate base template. |
| Menu template inline accents | `#C86B53` / `rgb(200, 107, 83)`; icon tile `#EBF0F5` / `rgb(235, 240, 245)`; icon stroke `#A8B4C0` / `rgb(168, 180, 192)` | Literal colors in `menu/menu.html`; accent differs from active primary. |

Some comments in the active `_variables.scss` still show the older hex approximations, for example `#C86B53`, `#8B9D83`, and `#EBE4D8`. Use the HSL-derived values in the active token table when documenting actual compiled colors.

## 3. Typography

The active mappings are defined in [`app/static/scss/abstracts/_variables.scss`](app/static/scss/abstracts/_variables.scss) and applied by [`app/static/scss/base/_typography.scss`](app/static/scss/base/_typography.scss).

| Selector or role | Exact font stack | Additional styling |
|---|---|---|
| `body`, `.body-font` | `'Plus Jakarta Sans', system-ui, -apple-system, sans-serif` | `1.05rem`, line-height `1.6`, primary text color |
| `h1`–`h6`, `.h1`–`.h6`, `.headline-font` | `'Fraunces', serif` | Weight `700`, line-height `1.2`, letter-spacing `-0.015em` |
| `.label-font` | `'Fraunces', serif` | `0.01em` letter spacing |
| `label`, `.form-control`, `.form-select`, `.form-text` | `'Fraunces', serif` | Shared control typography in base typography rules |
| `.btn` | `'Inter', system-ui, -apple-system, sans-serif` | The later `.btn` component rule overrides the general typography rule for buttons; weight `600` |
| `.badge`, `.status-pill` | `'Inter', system-ui, -apple-system, sans-serif` | Badge component rule sets Inter; status pills set their own Inter stack |
| `.text-eyebrow`, `.overline` | `'Fraunces', serif` | `0.6875rem`, weight `700`, uppercase, letter-spacing `0.08em` |
| `.price-tag`, `.order-id`, `.numeric-data` | `'Fraunces', serif` | Tabular numerals, `1.15rem`, weight `600` |
| `p.lead` | `'Plus Jakarta Sans', system-ui, -apple-system, sans-serif` | `1.15rem`, line-height `1.5` |
| `$font-family-serif` token | `'Newsreader', Georgia, serif` | Token exists, but it is not the active body stack in `_variables.scss`. |

### Font loading caveat

The active `base.html` and `admin_base.html` load Google Fonts for Fraunces, Bebas Neue, and Barlow. They do not explicitly load Inter, Newsreader, or Plus Jakarta Sans, despite those families being named in the active SCSS stacks. Those fonts therefore depend on local availability or fallback behavior unless loaded elsewhere.

`custom.css` defines `.font-serif { font-family: var(--bs-font-serif); }` with `--bs-font-serif: 'Georgia', 'Playfair Display', serif`; however, its stylesheet link is commented out in the base template. The `.font-serif` class is used in templates, but no `.font-serif` or `.font-sans` utility is defined in the active SCSS entry point. Inline/template style and alternate CSS may consequently determine their appearance on those views.

The alternate `_variables1.scss` uses `$font-family-base: $font-family-serif` (Newsreader), while the active `_variables.scss` maps `$font-family-base` to Plus Jakarta Sans. These are different typography variants.

## 4. Bootstrap Overrides and CSS Custom Properties

### Root-level custom properties in the active compiled theme

Defined in `base/_reset.scss` and emitted by the active `main.css`:

| Custom property | Value | Resolved color |
|---|---|---|
| `--bs-primary` | `hsl(12, 52%, 55%)` | `#C86851`, RGB `200, 104, 81` |
| `--bs-primary-rgb` | `181, 93, 68` | `#B55D44`; **does not match** the active `--bs-primary` (`#C86851`) |
| `--bs-body-bg` | `hsl(35, 30%, 88%)` | `#EAE2D7`, RGB `234, 226, 215` |
| `--bs-body-color` | `hsl(30, 4%, 17%)` | `#2D2B2A`, RGB `45, 43, 42` |

The `--bs-primary-rgb` mismatch is present in the SCSS reset and compiled CSS. It can affect Bootstrap utilities or components that use the RGB custom property for translucent primary colors.

### Component-scoped and template-scoped properties

- `.btn-primary` declares Bootstrap button variables: `--bs-btn-bg`, `--bs-btn-border-color`, `--bs-btn-color`, `--bs-btn-hover-bg`, `--bs-btn-hover-border-color`, `--bs-btn-hover-color`, `--bs-btn-active-bg`, `--bs-btn-active-border-color`, `--bs-btn-active-color`, and `--bs-btn-focus-shadow-rgb`. They are set from the active terracotta token and its Sass darkened states.
- `partials/_history_content.html` and the alternate `admin/history1.html` set the table custom property `--bs-table-bg: transparent` inline. The current history table also uses `table-layout: fixed` and a `<colgroup>` with explicit widths.
- `custom.css` separately defines `--bs-primary`, `--bs-primary-rgb`, `--bs-body-bg`, `--bs-body-color`, and `--bs-font-serif`; those declarations are not part of the active base stylesheet.
- `--border-divider` is referenced in the order layout styles, but no local definition was found in the SCSS, CSS, templates, or active root variables.

### SCSS design tokens and Bootstrap Sass settings

The active variable file also customizes Bootstrap Sass values for:

- Theme colors: primary, secondary, success, info, warning, danger, light, and dark.
- Body and heading typography and colors.
- Link color, hover color, decoration, and focus ring.
- Border color; small, standard, large, extra-large, and pill radii.
- Three shadow levels.
- Button padding, weight, font, radius, and focus shadow.
- Card surface, text, border, radius, spacing, and shadow.
- Input, focus, placeholder, and checkbox colors.
- Modal and offcanvas surfaces and borders.
- Badge typography, padding, radius, and active navigation pills.
- Dropdown, sticky, fixed, modal, and offcanvas z-index values.

**Integration limitation:** Bootstrap CSS is loaded from the Bootstrap CDN; the active SCSS entry point does not import/recompile Bootstrap's Sass. Therefore the `$theme-colors` and other Bootstrap Sass settings document the intended overrides, but do not by themselves rebuild the CDN's `.text-*`, `.bg-*`, or component rules. The local root custom properties and custom component CSS are the overrides actually emitted by the project stylesheet.

## 5. SCSS Architecture and Mixins

`main.scss` imports the active token file, then:

- `base/_reset.scss` and `base/_typography.scss`
- Components for buttons, cards, icons, badges, indicators, forms, switches, toast messages, and pagination
- Layout modules for hero, menu, and navbar
- `utilities/_responsive.scss`

No project-defined SCSS `@mixin` or `@include` directives were found in the SCSS workspace. The Sass code uses built-in functions such as `darken()`, `lighten()`, `rgba()`, `map-get()`, `red()`, `green()`, and `blue()`; these are functions, not custom mixins. Components also use Sass `@extend` (for example, order and dish cards extending `.card`).

## 6. Layout, Bootstrap, and Component Conventions

- Bootstrap 5.3.3 and Bootstrap Icons are included by CDN in the base templates.
- The project stylesheet is loaded after Bootstrap in the base layouts so local selectors can override framework styles.
- Layouts use Bootstrap grid/flex utilities extensively; the main page uses a viewport-height flex shell and the admin base uses a flex-column content area.
- The order-history table uses fixed column widths and a transparent Bootstrap table background to keep the table stable across HTMX swaps.
- Buttons use shared radius/padding tokens, visible focus rings, subtle active scaling, and hover transitions in `components/_buttons.scss`.
- Cards share a surface, border, radius, shadow, and transition treatment in `components/_cards.scss`.
- The theme uses semantic tokens (`$bg-canvas`, `$bg-surface`, `$text-primary`, `$status-danger`, etc.) mapped from primitive color scales.

## 7. Known Design-System Gaps

1. **Several parallel palettes exist.** The active HSL palette, `_variables1.scss`/`_variables3.scss`, `main..css`, `custom.css`, and template-level inline colors differ. Use the active `main.scss` import chain for current token values; label all other values as alternate/legacy.
2. **HSL comments are stale.** Several comments in the active token file quote hex values that do not exactly correspond to their HSL declarations.
3. **Primary RGB is inconsistent.** `--bs-primary` resolves to `#C86851`, while `--bs-primary-rgb` encodes `#B55D44`.
4. **Status coverage is incomplete.** The active order badge styles define completed, pending, and cancelled only. Ready and confirmed lack status-specific colors.
5. **Status-pill variants are not unified.** The older `_badges2.scss` and `main..css` use `.pill-danger`, `.pill-warning`, and `.pill-success`, while the active status classes use `.status-cancelled`, `.status-pending`, and `.status-completed`.
6. **Font declarations and font loading differ.** Fraunces is loaded by the active base templates, but Inter, Newsreader, and Plus Jakarta Sans are named in active CSS without explicit Google Fonts loading there.
7. **Build and served CSS paths differ.** Debug Sass compilation targets `static/css`, while active templates link `static/scss/main.css`.
8. **Some template colors are hardcoded.** Menu and modal templates include inline colors that bypass the semantic SCSS tokens.

## 8. Source Files Reviewed

- `app/static/scss/main.scss`
- `app/static/scss/abstracts/_variables.scss`, `_variables1.scss`, `_variables3.scss`
- `app/static/scss/base/_reset.scss`, `_typography.scss`
- `app/static/scss/components/_badges.scss`, `_badges2.scss`, `_buttons.scss`, `_cards.scss`
- `app/static/scss/layouts/_orders.scss`
- `app/static/scss/main.css`, `main..css`
- `app/static/css/custom.css`, `main.css`, `main..css`
- `app/templates/base.html`, `base2.html`, `base3.html`, `admin_base.html`, `admin_base2.html`
- `app/templates/partials/_history_content.html`, `app/templates/menu/menu.html`
