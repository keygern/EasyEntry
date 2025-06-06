import { useEffect, useState } from 'react';

interface Account {
  plan: string;
  quota_remaining: number;
}

export default function Account() {
  const [account, setAccount] = useState<Account | null>(null);
  const api = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    fetch(`${api}/account`, { credentials: 'include' })
      .then(res => res.json())
      .then(setAccount);
  }, [api]);

  if (!account) return <div>Loading...</div>;
  return (
    <div>
      <h1>Account</h1>
      <p>Plan: {account.plan}</p>
      <p>Quota Remaining: {account.quota_remaining}</p>
    </div>
  );
}
