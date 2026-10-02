import { useCallback, useEffect, useRef, useState } from 'react';
import { createTodo, fetchTodos } from '../api/todosApi';

/**
 * Server state for the TODO list.
 *
 * The list always comes from the backend: after a successful create the hook
 * re-fetches instead of appending locally, so the UI shows what MongoDB stored.
 */
export function useTodos() {
  const [todos, setTodos] = useState([]);
  // true initially so the UI never flashes "empty" before the first load.
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Every load takes a ticket; only the latest ticket may update state. This
  // drops out-of-order responses and any response arriving after unmount.
  const latestRequestId = useRef(0);

  // Never throws: load failures are exposed through `error`.
  const refresh = useCallback(async () => {
    const requestId = ++latestRequestId.current;
    const isLatest = () => requestId === latestRequestId.current;

    setIsLoading(true);
    try {
      const data = await fetchTodos();
      if (isLatest()) {
        setTodos(data);
        setError(null);
      }
    } catch (err) {
      if (isLatest()) {
        setError(err);
      }
    } finally {
      if (isLatest()) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    refresh();
    return () => {
      // Invalidate in-flight loads so they cannot set state after unmount.
      latestRequestId.current += 1;
    };
  }, [refresh]);

  // Rejects if the create fails, so the caller can keep the user's input.
  // Resolves once the item is saved, even if the follow-up refresh fails.
  const addTodo = useCallback(
    async (description) => {
      await createTodo(description);
      await refresh();
    },
    [refresh]
  );

  return { todos, isLoading, error, refresh, addTodo };
}
