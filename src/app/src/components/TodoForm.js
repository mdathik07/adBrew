import { useState } from 'react';

// Mirrors the backend limit; the server remains the source of truth.
const MAX_DESCRIPTION_LENGTH = 500;
const INPUT_ID = 'todo-description';
const ERROR_ID = 'todo-description-error';

/**
 * Form for creating a TODO. Owns its own input and submission state;
 * persisting (and refreshing the list) is delegated to the onAdd prop.
 */
export function TodoForm({ onAdd }) {
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(event) {
    setDescription(event.target.value);
    if (error) {
      setError(null);
    }
  }

  async function handleSubmit(event) {
    // Prevent the browser's full-page form submission.
    event.preventDefault();
    if (isSubmitting) {
      return;
    }

    const trimmed = description.trim();
    if (!trimmed) {
      setError('Please enter a TODO description.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onAdd(trimmed);
      setDescription('');
    } catch (err) {
      // Keep the user's text so they can correct it or retry.
      setError(errorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div>
        <label htmlFor={INPUT_ID}>ToDo: </label>
        <input
          id={INPUT_ID}
          type="text"
          value={description}
          onChange={handleChange}
          maxLength={MAX_DESCRIPTION_LENGTH}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? ERROR_ID : undefined}
        />
      </div>
      {error && (
        <p id={ERROR_ID} role="alert">
          {error}
        </p>
      )}
      <div style={{ marginTop: '5px' }}>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Adding…' : 'Add ToDo!'}
        </button>
      </div>
    </form>
  );
}

function errorMessage(err) {
  // Prefer the field-level validation message from the API when present.
  return (err.details && err.details.description) || err.message || 'Could not add the TODO.';
}
