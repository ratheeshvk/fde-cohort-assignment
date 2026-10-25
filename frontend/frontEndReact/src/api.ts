import type { Employee, Review, ReviewCreate, ReviewFilters, ReviewPeriod } from './type';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
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
    throw new Error(message);
  }
  return res.json() as Promise<T>;
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
