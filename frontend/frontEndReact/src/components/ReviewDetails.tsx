import { useEffect, useState } from 'react';
import type { Employee, Review } from '../type';
import { fetchEmployees, fetchReview } from '../api';
import StarRating from './StarRating';

interface ReviewDetailsProps {
  reviewId: number;
  onClose: () => void;
}

export default function ReviewDetails({ reviewId, onClose }: ReviewDetailsProps) {
  const [review, setReview] = useState<Review | null>(null);
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setReview(null);
    setError(null);
    // /reviews/{id} returns the numeric employee id; look up the employee for the EMP code.
    Promise.all([fetchReview(reviewId), fetchEmployees()])
      .then(([rev, emps]) => {
        setReview(rev);
        setEmployee(emps.find((e) => e.id === rev.employee_id) ?? null);
      })
      .catch((err: Error) => setError(err.message));
  }, [reviewId]);

  const criteria = review
    ? [
        { label: 'Quality of Work', value: review.quality_rating },
        { label: 'Delivery & Ownership', value: review.delivery_rating },
        { label: 'Teamwork & Collaboration', value: review.teamwork_rating },
      ]
    : [];

  return (
    <section className="review-details">
      <div className="details-header">
        <h2>Review Details</h2>
        <button type="button" onClick={onClose}>
          Close
        </button>
      </div>

      {error && <p className="error">Error: {error}</p>}
      {!error && !review && <p>Loading...</p>}

      {review && (
        <>
          <div className="summary-cards">
            <div className="card">
              <span className="card-label">Employee</span>
              <span>
                {employee ? `${employee.employee_id} - ` : ''}
                {review.employee_name}
              </span>
            </div>
            <div className="card">
              <span className="card-label">Review Period</span>
              <span>{review.period_name}</span>
            </div>
            <div className="card overall">
              <span className="card-label">Overall Rating</span>
              <span>
                <strong>{Number(review.average_rating).toFixed(1)}</strong> / 5
              </span>
            </div>
          </div>

          <h3>Performance Criteria</h3>
          <table>
            <thead>
              <tr>
                <th>Criteria</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
              {criteria.map((c) => (
                <tr key={c.label}>
                  <td>{c.label}</td>
                  <td>
                    <StarRating value={c.value} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3>Manager Comments</h3>
          <p className="comments">{review.comments || 'No comments provided.'}</p>
        </>
      )}
    </section>
  );
}
