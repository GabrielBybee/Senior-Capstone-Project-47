import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from './api/health'

function App() {
  const health = useQuery({ queryKey: ['health'], queryFn: fetchHealth })

  let status = 'Checking backend…'
  if (health.isError) status = 'Backend unreachable'
  if (health.data) status = `Backend: ${health.data.status}`

  return (
    <main>
      <h1>SecureCode Tutor</h1>
      <p role="status">{status}</p>
    </main>
  )
}

export default App
