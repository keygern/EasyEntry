import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)

  const m = useMutation({
    mutationFn: async () => {
      if (!file) return
      const token = localStorage.getItem('sb-jwt')
      const form = new FormData()
      form.append('file', file)
      form.append('doc_type', 'invoice')
      const base = process.env.NEXT_PUBLIC_API_URL || ''
      const res = await fetch(`${base}/documents/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      })
      return res.json()
    },
  })

  return (
    <div className="p-4">
      <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
      <button onClick={() => m.mutate()} className="ml-2 px-4 py-2 bg-blue-500 text-white">Upload</button>
    </div>
  )
}
