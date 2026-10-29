import axe from 'axe-core'

// The WCAG levels we must meet: 2.1 AA (ADA Title II), which includes A.
const WCAG_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']

/**
 * Runs axe-core on a rendered element and returns its WCAG 2.1 AA violations,
 * formatted so a failing test says what is wrong and where.
 *
 * jsdom has no layout engine, so axe can't check things like color contrast here.
 * Playwright + axe covers those against a real browser (Phase 3).
 */
export async function wcagViolations(element: Element): Promise<string[]> {
  const results = await axe.run(element, { runOnly: { type: 'tag', values: WCAG_TAGS } })
  return results.violations.map(
    (v) =>
      `${v.id} (${v.impact}): ${v.help} — ${v.nodes.map((n) => n.target.join(' ')).join(', ')}`,
  )
}
