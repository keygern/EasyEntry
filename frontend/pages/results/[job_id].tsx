import { useRouter } from 'next/router'
import { useQuery } from '@tanstack/react-query'

export default function Results() {
  const router = useRouter()
  const { job_id } = router.query
  const token = typeof window !== 'undefined' ? localStorage.getItem('sb-jwt') : ''
  const { data } = useQuery({
    queryKey: ['parse', job_id],
    queryFn: async () => {
      const res = await fetch(`/documents/parse/invoice/${job_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      return res.json()
    },
    enabled: !!job_id,
    refetchInterval: 3000,
  })

  if (!data) return <p>Loading...</p>
  return (
    <pre>{JSON.stringify(data, null, 2)}</pre>
  )
}
