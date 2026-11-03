# Accessibility

**Target: WCAG 2.1 Level AA** for everything students and instructors use.

## Why

The 2024 update to ADA Title II requires state and local government web content
and apps, including public universities' internal and password-protected tools,
to meet WCAG 2.1 AA. The Department of Justice moved the compliance date for
large public entities to **April 26, 2027** in an interim rule on April 20, 2026.
The standard itself didn't change.

Confirm the details that apply to the University of Idaho with its accessibility
office. Either way, building it in from the start is far cheaper than fixing it later.

## What's checked automatically

| Check | Where | Catches |
|---|---|---|
| oxlint `jsx-a11y` rules (all 36, as errors) | `npm run lint`, `check.py` | Missing alt text, unlabeled controls, click handlers that can't be used from the keyboard, invalid ARIA, links with no destination |
| axe-core (WCAG 2.0/2.1 A + AA rules) | Vitest component tests, `check.py` | Missing names and labels, wrong roles, structure problems in rendered components |
| Playwright + axe on real pages | *planned, Phase 3* | Color contrast, focus order, whole-page structure. jsdom can't check these. |

To test a new component, render it and assert it has no violations:

```tsx
import { wcagViolations } from './test/axe'

const { container } = render(<HintPanel … />)
expect(await wcagViolations(container)).toEqual([])
```

## What automation can't check

Automated tools find roughly a third to a half of WCAG problems. Before
releasing any new page, someone checks it by hand:

- [ ] **Keyboard only:** everything works with Tab, Shift+Tab, Enter, Space,
      Escape and the arrow keys. Focus is always visible and never gets stuck.
      The code editor has a documented way to Tab out of it.
- [ ] **Screen reader** (NVDA on Windows, VoiceOver on macOS, Orca on Linux):
      headings, buttons, form fields and errors are announced sensibly. Results
      and hints that appear on their own are announced (live regions).
- [ ] **200% zoom, and 320 px wide:** nothing is cut off or overlaps, and there's
      no sideways scrolling except in the code editor.
- [ ] **Color:** information is never shown by color alone, for example
      pass/fail also has an icon or text. Text contrast is at least 4.5:1.
- [ ] **Motion and time:** nothing flashes, and no time limits without a way to extend them.
- [ ] **Errors:** form errors say what's wrong and how to fix it, next to the field.

## Project-specific notes

- **Monaco editor:** turn on its accessibility support mode and test it with a
  screen reader early. Code editors are where tools like this usually fail.
- **Sanitizer output** (ASan, Valgrind) is long and dense. Show a plain-language
  summary first, with the raw output in an expandable section.
- **Hints and results** appear without a page load. Use `<output>` or
  `aria-live="polite"` so screen reader users hear them.
