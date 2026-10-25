import { useEffect, useState } from 'react';
import type { Employee, Review, ReviewFilters, ReviewPeriod } from '../type';
import { fetchEmployees, fetchReviews } from '../api';
import EmployeeSearch from './EmployeeSearch';

// No /periods endpoint exists, so derive the period options from the unfiltered review list.
function uniquePeriods(reviews: Review[]): ReviewPeriod[] {
  const byId = new Map<number, ReviewPeriod>();
  for (const r of reviews) {
    if (!byId.has(r.period_id)) {
      byId.set(r.period_id, { id: r.period_id, name: r.period_name ?? `Period ${r.period_id}` });
    }
  }
  return [...byId.values()].sort((a, b) => a.id - b.id);
}

export default function ReviewList() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [periods, setPeriods] = useState<ReviewPeriod[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [filters, setFilters] = useState<ReviewFilters>({ employeeId: null, periodId: null });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchEmployees(), fetchReviews()])
      .then(([emps, allReviews]) => {
        setEmployees(emps);
        setPeriods(uniquePeriods(allReviews));
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    fetchReviews(filters)
      .then(setReviews)
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [filters]);

  return (
    <section className="review-list">
      <div className="filters">
        <label>
          Review Period
          <select
            value={filters.periodId ?? ''}
            onChange={(e) =>
              setFilters({ ...filters, periodId: e.target.value === '' ? null : Number(e.target.value) })
            }
          >
            <option value="">All Periods</option>
            {periods.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Employee
          <EmployeeSearch
            employees={employees}
            selectedId={filters.employeeId}
            onChange={(employeeId) => setFilters({ ...filters, employeeId })}
          />
        </label>
      </div>

      {error && <p className="error">Error: {error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Employee</th>
            <th>Period</th>
            <th>Quality</th>
            <th>Delivery</th>
            <th>Teamwork</th>
            <th>Average</th>
            <th>Comments</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan={9}>Loading...</td>
            </tr>
          ) : reviews.length === 0 ? (
            <tr>
              <td colSpan={9}>No reviews found.</td>
            </tr>
          ) : (
            reviews.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.employee_name}</td>
                <td>{r.period_name}</td>
                <td>{r.quality_rating}</td>
                <td>{r.delivery_rating}</td>
                <td>{r.teamwork_rating}</td>
                <td>{Number(r.average_rating).toFixed(2)}</td>
                <td>{r.comments}</td>
                <td>{r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      {!isLoading && <p className="muted">{reviews.length} review(s)</p>}
    </section>
  );
}
