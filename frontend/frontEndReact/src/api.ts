import type { Employee, Review, ReviewFilters } from './type';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchEmployees(): Promise<Employee[]> {
  return getJson<Employee[]>('/employees');
}

export function fetchReviews(filters: ReviewFilters = { employeeId: null, periodId: null }): Promise<Review[]> {
  const params = new URLSearchParams();
  if (filters.employeeId !== null) params.set('employee_id', String(filters.employeeId));
  if (filters.periodId !== null) params.set('period_id', String(filters.periodId));
  const query = params.toString();
  return getJson<Review[]>(query ? `/reviews?${query}` : '/reviews');
}
