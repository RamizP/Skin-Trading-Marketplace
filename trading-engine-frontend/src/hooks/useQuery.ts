import { useCallback, useEffect, useState } from "react";
import { getErrorMessage } from "../utils/format";

export default function useQuery<T>(
  fetcher: (() => Promise<T>) | null,
  initial: T,
) {
  const [data, setData] = useState(initial);
  const [loading, setLoading] = useState(Boolean(fetcher));
  const [error, setError] = useState("");
  const [version, setVersion] = useState(0);
  const reload = useCallback(() => setVersion((value) => value + 1), []);
  useEffect(() => {
    if (!fetcher) {
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    setError("");
    fetcher()
      .then((result) => {
        if (active) setData(result);
      })
      .catch((reason: unknown) => {
        if (active) setError(getErrorMessage(reason));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetcher, version]);
  return { data, loading, error, reload };
}
