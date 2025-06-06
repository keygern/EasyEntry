import { useQuery } from '@tanstack/react-query'

export default function Account() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('sb-jwt') : ''
  const { data } = useQuery({
    queryKey: ['account'],
    queryFn: async () => {
      const base = process.env.NEXT_PUBLIC_API_URL || ''
      const res = await fetch(`${base}/user`, { headers: { Authorization: `Bearer ${token}` } })
      return res.json()
    },
  })

  return (
    <div className="p-4">
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
