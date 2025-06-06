import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import { API_BASE } from '../../lib/api';

interface Result {
  status: string;
  data?: any;
}

export default function ResultPage() {
  const router = useRouter();
  const { job_id } = router.query as { job_id: string };
  const api = API_BASE;

  const { data, isLoading } = useQuery({
    queryKey: ['result', job_id],
    queryFn: async () => {
      const res = await fetch(`${api}/documents/parse/invoice/${job_id}`);
      return res.json() as Promise<Result>;
    },
    enabled: !!job_id,
    refetchInterval: 3000,
  });

  if (isLoading || !data) return <div>Loading...</div>;
  return (
    <pre>{JSON.stringify(data, null, 2)}</pre>
  );
}
