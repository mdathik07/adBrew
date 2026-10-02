/**
 * Presentational list of TODOs. Holds no state; everything comes from props.
 */
export function TodoList({ todos, isLoading, error, onRetry }) {
  // Only show the loading message when there is nothing to display yet, so a
  // refresh after adding a TODO does not make the existing list flicker.
  if (isLoading && todos.length === 0) {
    return <p>Loading TODOs…</p>;
  }

  return (
    <>
      {error && (
        <div role="alert">
          Could not load TODOs: {error.message}{' '}
          <button type="button" onClick={onRetry} disabled={isLoading}>
            Retry
          </button>
        </div>
      )}
      {todos.length > 0 ? (
        <ul>
          {todos.map((todo) => (
            <li key={todo.id}>{todo.description}</li>
          ))}
        </ul>
      ) : (
        !error && <p>No TODOs yet. Add one below.</p>
      )}
    </>
  );
}
