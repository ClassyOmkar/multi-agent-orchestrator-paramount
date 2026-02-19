import React, { useState } from 'react';
import styles from './TaskForm.module.css';

interface TaskFormProps {
  onSubmit: (query: string, apiKey: string) => Promise<void>;
  disabled?: boolean;
  onToast?: (msg: string, type: 'success' | 'error' | 'info') => void;
}

export default function TaskForm({ onSubmit, disabled, onToast }: TaskFormProps) {
  const [query, setQuery] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [validating, setValidating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    await onSubmit(query, apiKey);
    setQuery('');
  };

  const validateKey = async () => {
    if (!apiKey) return;
    setValidating(true);
    try {
      const res = await fetch('http://localhost:8000/validate-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
      });
      const data = await res.json();
      if (data.valid) {
        onToast?.("API Key is Valid!", "success");
      } else {
        onToast?.("API Key is Invalid.", "error");
      }
    } catch (e) {
      onToast?.("Validation Network Error", "error");
    } finally {
      setValidating(false);
    }
  };

  return (
    <form className={styles.formContainer} onSubmit={handleSubmit}>
      <div className={styles.inputGroup}>
        <div className={styles.inputWrapper}>
          <input
            type={showKey ? "text" : "password"}
            className={styles.input}
            placeholder="Enter Grok/xAI API Key (Optional)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            disabled={disabled}
          />
        </div>

        <button
          type="button"
          className={styles.toggleButton}
          onClick={() => setShowKey(!showKey)}
        >
          {showKey ? 'Hide' : 'Show'}
        </button>
        <button
          type="button"
          className={styles.validateButton}
          onClick={validateKey}
          disabled={!apiKey || validating}
        >
          {validating ? '...' : 'Check'}
        </button>
      </div>
      <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '-0.5rem', marginBottom: '1rem' }}>
        Leave empty to use Hardcoded Key or Mock Agents.
      </p>

      <input
        type="text"
        className={styles.input}
        placeholder="Enter your research task (e.g., 'Research Quantum Computing')"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={disabled}
      />
      <button type="submit" className={styles.button} disabled={disabled || !query.trim()}>
        {disabled ? 'Processing...' : 'Start Task'}
      </button>
    </form>
  );
}
