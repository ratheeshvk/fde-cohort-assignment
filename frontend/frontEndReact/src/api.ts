import type { AdminUser, LoginRequest } from './auth';
import type { Employee, Review, ReviewCreate, ReviewFilters, ReviewPeriod } from './type';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// App registers this so any 401 (expired or missing login) sends the user back to the login screen.
let onUnauthorized: () => void = () => {};

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

interface RequestOptions extends RequestInit {
  // Auth calls handle their own 401s instead of triggering a logout
  skipUnauthorizedHandler?: boolean;
}

async function request<T>(path: string, init: RequestOptions = {}): Promise<T> {
  const { skipUnauthorizedHandler, ...fetchInit } = init;
  // credentials: 'include' sends the httponly login cookie with every request
  const res = await fetch(`${API_BASE}${path}`, { ...fetchInit, credentials: 'include' });
  if (res.status === 401 && !skipUnauthorizedHandler) {
    onUnauthorized();
  }
  if (!res.ok) {
    // FastAPI returns { detail: string } for HTTPException and { detail: [...] } for validation errors
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).join('; ')
          : `${res.status} ${res.statusText}`;
    throw new ApiError(res.status, message);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export function login(credentials: LoginRequest): Promise<AdminUser> {
  return request<AdminUser>('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
    skipUnauthorizedHandler: true,
  });
}

export function logout(): Promise<void> {
  return request<void>('/api/auth/logout', { method: 'POST', skipUnauthorizedHandler: true });
}

// Returns the logged-in admin, or null when no one is logged in.
export async function getMe(): Promise<AdminUser | null> {
  try {
    return await request<AdminUser>('/api/auth/me', { skipUnauthorizedHandler: true });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) return null;
    throw err;
  }
}

function getJson<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function fetchEmployees(): Promise<Employee[]> {
  return getJson<Employee[]>('/employees');
}

// Fallback while the backend has no /review-periods endpoint: derive the periods seen in existing reviews.
function periodsFromReviews(reviews: Review[]): ReviewPeriod[] {
  const byId = new Map<number, ReviewPeriod>();
  for (const r of reviews) {
    if (!byId.has(r.period_id)) {
      byId.set(r.period_id, { id: r.period_id, name: r.period_name ?? `Period ${r.period_id}` });
    }
  }
  return [...byId.values()].sort((a, b) => a.id - b.id);
}

export async function fetchReviewPeriods(): Promise<ReviewPeriod[]> {
  try {
    return await getJson<ReviewPeriod[]>('/review-periods');
  } catch {
    return periodsFromReviews(await fetchReviews());
  }
}

export function fetchReview(reviewId: number): Promise<Review> {
  return getJson<Review>(`/reviews/${reviewId}`);
}

export function fetchReviews(filters: ReviewFilters = { employeeId: null, periodId: null }): Promise<Review[]> {
  const params = new URLSearchParams();
  if (filters.employeeId !== null) params.set('employee_id', String(filters.employeeId));
  if (filters.periodId !== null) params.set('period_id', String(filters.periodId));
  const query = params.toString();
  return getJson<Review[]>(query ? `/reviews?${query}` : '/reviews');
}

export function createReview(review: ReviewCreate): Promise<Review> {
  return request<Review>('/api/reviews', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(review),
  });
}
