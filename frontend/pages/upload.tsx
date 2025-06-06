import { useState } from 'react';
import { API_BASE } from '../lib/api';

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const api = API_BASE;

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    form.append('doc_type', 'invoice');
    const res = await fetch(`${api}/documents/upload`, {
      method: 'POST',
      body: form,
    });
    const data = await res.json();
    console.log(data);
  };

  return (
    <form onSubmit={onSubmit}>
      <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
      <button type="submit">Upload</button>
    </form>
  );
}

