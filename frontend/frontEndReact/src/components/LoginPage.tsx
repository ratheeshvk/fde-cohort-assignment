import { useState } from 'react';
import type { FormEvent } from 'react';
import type { AdminUser } from '../auth';
import { ApiError, login } from '../api';

interface LoginPageProps {
  onLogin: (admin: AdminUser) => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Enter your username and password.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      onLogin(await login({ username: username.trim(), password }));
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? 'Invalid username or password.'
          : `Could not sign in: ${(err as Error).message}`,
      );
      setPassword('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit} noValidate>
        <h1>Performance Reviews</h1>
        <p className="muted">Sign in to continue</p>

        <label>
          Username
          <input
            type="text"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </label>

        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" className="primary" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}
