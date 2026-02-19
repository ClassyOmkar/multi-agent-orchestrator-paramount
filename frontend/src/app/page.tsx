'use client';

import { useState, useEffect } from 'react';
import TaskForm from '../components/TaskForm';
import StatusTracker from '../components/StatusTracker';
import ResultDisplay from '../components/ResultDisplay';
import Toast from '../components/Toast';
import styles from './page.module.css';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ToastMsg {
  msg: string;
  type: 'success' | 'error' | 'info';
}

export default function Home() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('IDLE');
  const [logs, setLogs] = useState<any[]>([]);
  const [result, setResult] = useState<string | undefined>(undefined);
  const [toast, setToast] = useState<ToastMsg | null>(null);

  // Load state from localStorage on mount
  useEffect(() => {
    const savedTaskId = localStorage.getItem('mao_taskId');
    if (savedTaskId) {
      setTaskId(savedTaskId);
      fetchStatus(savedTaskId);
    }
  }, []);

  const fetchStatus = async (id: string) => {
    try {
      const res = await fetch(`${API_URL}/tasks/${id}`);
      if (!res.ok) {
        if (res.status === 404) clearSession();
        return;
      }
      const data = await res.json();
      setStatus(data.status);
      setLogs(data.logs || []);
      if (data.status === 'COMPLETED') {
        setResult(data.result);
      }
    } catch (e) {
      console.error("Failed to restore session", e);
    }
  };

  const clearSession = () => {
    localStorage.removeItem('mao_taskId');
    setTaskId(null);
    setStatus('IDLE');
    setLogs([]);
    setResult(undefined);
    setToast({ msg: "Session Cleared", type: "info" });
  }

  const startTask = async (query: string, apiKey: string) => {
    try {
      setStatus('STARTING');
      setLogs([]);
      setResult(undefined);

      const res = await fetch(`${API_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, api_key: apiKey || null }),
      });

      if (!res.ok) throw new Error('Failed to start task');

      const data = await res.json();
      setTaskId(data.task_id);
      localStorage.setItem('mao_taskId', data.task_id); // Save ID
      setStatus(data.status);
      setToast({ msg: "Task Started Successfully", type: "success" });
    } catch (error) {
      console.error(error);
      setStatus('FAILED');
      setToast({ msg: "Failed to start task. Backend may be down.", type: "error" });
    }
  };

  const showToast = (msg: string, type: 'success' | 'error' | 'info') => {
    setToast({ msg, type });
  }

  // Poll for status
  useEffect(() => {
    if (!taskId || status === 'COMPLETED' || status === 'FAILED') return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/tasks/${taskId}`);
        if (!res.ok) return;

        const data = await res.json();
        setStatus(data.status);
        setLogs(data.logs || []);
        if (data.status === 'COMPLETED') {
          setResult(data.result);
          clearInterval(interval);
          setToast({ msg: "Task Completed!", type: "success" });
        } else if (data.status === 'FAILED') {
          clearInterval(interval);
          setToast({ msg: "Task Execution Failed", type: "error" });
        }
      } catch (error) {
        console.error(error);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [taskId, status]);

  return (
    <main className={styles.main}>
      {toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}

      <header className={styles.header}>
        <h1 className={styles.title}>Agent Orchestrator</h1>
        <p className={styles.description}>
          Autonomous multi-agent system powered by Groq & Llama 3.
          Watch the swarm collaborate on your research task.
        </p>
      </header>

      <div className={styles.grid}>
        <section className={styles.card}>
          <div className={styles.formRow}>
            <TaskForm
              onSubmit={startTask}
              disabled={status !== 'IDLE' && status !== 'COMPLETED' && status !== 'FAILED'}
              onToast={showToast}
            />

            {taskId && (
              <button onClick={clearSession} className={styles.clearBtn} title="Clear Session & Start New">
                <span>↺</span>
              </button>
            )}
          </div>
        </section>

        {(status !== 'IDLE' || logs.length > 0) && (
          <section className={styles.trackerSection}>
            <StatusTracker status={status} />
          </section>
        )}

        <ResultDisplay logs={logs} result={result} finalStatus={status} />
      </div>
    </main>
  );
}
