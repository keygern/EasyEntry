import { useQuery } from '@tanstack/react-query'

export default function Account() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('sb-jwt') : ''
  const { data } = useQuery({
    queryKey: ['account'],
    queryFn: async () => {
      const res = await fetch('/user', { headers: { Authorization: `Bearer ${token}` } })
      return res.json()
    },
  })

  return (
    <div className="p-4">
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
