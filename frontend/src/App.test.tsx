import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { wcagViolations } from './test/axe'

function renderApp() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>,
  )
}

describe('App', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shows the backend status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(Response.json({ status: 'ok', service: 'backend' })),
    )

    renderApp()

    expect(await screen.findByText('Backend: ok')).toBeInTheDocument()
  })

  it('says when the backend is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    renderApp()

    expect(await screen.findByText('Backend unreachable')).toBeInTheDocument()
  })

  it('has no WCAG 2.1 AA violations', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(Response.json({ status: 'ok', service: 'backend' })),
    )

    const { container } = renderApp()
    await screen.findByText('Backend: ok')

    expect(await wcagViolations(container)).toEqual([])
  })
})
