import { useEffect, useState } from 'react';
import type { Employee, Review, ReviewFilters, ReviewPeriod } from '../type';
import { fetchEmployees, fetchReviewPeriods, fetchReviews } from '../api';
import EmployeeSearch from './EmployeeSearch';

interface ReviewListProps {
  selectedReviewId: number | null;
  onSelectReview: (reviewId: number) => void;
  // Bumped by the parent after a new review is submitted, to reload the list
  refreshKey: number;
}

export default function ReviewList({ selectedReviewId, onSelectReview, refreshKey }: ReviewListProps) {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [periods, setPeriods] = useState<ReviewPeriod[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [filters, setFilters] = useState<ReviewFilters>({ employeeId: null, periodId: null });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([fetchEmployees(), fetchReviewPeriods()])
      .then(([emps, allPeriods]) => {
        setEmployees(emps);
        setPeriods(allPeriods);
      })
      .catch((err: Error) => setError(err.message));
  }, [refreshKey]);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    fetchReviews(filters)
      .then(setReviews)
      .catch((err: Error) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [filters, refreshKey]);

  const employeeCodes = new Map(employees.map((e) => [e.id, e.employee_id]));

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
            <th>Employee ID</th>
            <th>Employee</th>
            <th>Period</th>
            <th>Quality</th>
            <th>Delivery</th>
            <th>Teamwork</th>
            <th>Average</th>
            <th>Comments</th>
            <th>Created</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan={10}>Loading...</td>
            </tr>
          ) : reviews.length === 0 ? (
            <tr>
              <td colSpan={10}>No reviews found.</td>
            </tr>
          ) : (
            reviews.map((r) => (
              <tr key={r.id} className={r.id === selectedReviewId ? 'selected' : ''}>
                <td>
                  <button type="button" className="link-button" onClick={() => onSelectReview(r.id)}>
                    {employeeCodes.get(r.employee_id) ?? r.employee_id}
                  </button>
                </td>
                <td>{r.employee_name}</td>
                <td>{r.period_name}</td>
                <td>{r.quality_rating}</td>
                <td>{r.delivery_rating}</td>
                <td>{r.teamwork_rating}</td>
                <td>{Number(r.average_rating).toFixed(2)}</td>
                <td>{r.comments}</td>
                <td>{r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}</td>
                <td>
                  <button type="button" className="link-button" onClick={() => onSelectReview(r.id)}>
                    View
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
      {!isLoading && <p className="muted">{reviews.length} review(s)</p>}
    </section>
  );
}
