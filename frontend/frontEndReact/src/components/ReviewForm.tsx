import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import type { Employee, Review, ReviewPeriod } from '../type';
import { createReview, fetchEmployees, fetchReviewPeriods } from '../api';
import StarRating from './StarRating';

interface ReviewFormProps {
  onSubmitted: (review: Review) => void;
}

interface FormState {
  employeeId: string;
  periodId: string;
  quality: number;
  delivery: number;
  teamwork: number;
  comments: string;
}

const EMPTY_FORM: FormState = {
  employeeId: '',
  periodId: '',
  quality: 0,
  delivery: 0,
  teamwork: 0,
  comments: '',
};

const RATINGS = [
  { key: 'quality', label: 'Quality of Work' },
  { key: 'delivery', label: 'Delivery & Ownership' },
  { key: 'teamwork', label: 'Teamwork & Collaboration' },
] as const;

function validate(form: FormState): string[] {
  const errors: string[] = [];
  if (!form.employeeId) errors.push('Employee is required.');
  if (!form.periodId) errors.push('Review Period is required.');
  for (const r of RATINGS) {
    if (form[r.key] < 1 || form[r.key] > 5) errors.push(`${r.label} rating (1-5) is required.`);
  }
  if (!form.comments.trim()) errors.push('Overall Comments are required.');
  return errors;
}

export default function ReviewForm({ onSubmitted }: ReviewFormProps) {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [periods, setPeriods] = useState<ReviewPeriod[]>([]);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    Promise.all([fetchEmployees(), fetchReviewPeriods()])
      .then(([emps, allPeriods]) => {
        setEmployees(emps);
        // Business rule: only open periods accept new reviews (status is absent in the fallback list)
        setPeriods(allPeriods.filter((p) => p.status === undefined || p.status === 'Open'));
      })
      .catch((err: Error) => setErrors([err.message]));
  }, []);

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setSuccess(null);
  };

  const reset = () => {
    setForm(EMPTY_FORM);
    setErrors([]);
    setSuccess(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const validationErrors = validate(form);
    setErrors(validationErrors);
    if (validationErrors.length > 0) return;

    setIsSubmitting(true);
    try {
      const created = await createReview({
        employee_id: Number(form.employeeId),
        period_id: Number(form.periodId),
        quality_rating: form.quality,
        delivery_rating: form.delivery,
        teamwork_rating: form.teamwork,
        comments: form.comments.trim(),
      });
      setForm(EMPTY_FORM);
      setSuccess(`Review submitted. Average rating: ${Number(created.average_rating).toFixed(2)}`);
      onSubmitted(created);
    } catch (err) {
      setErrors([(err as Error).message]);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="review-form">
      <h2>Submit Performance Review</h2>
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-row">
          <label>
            Employee <span className="required">*</span>
            <select value={form.employeeId} onChange={(e) => update('employeeId', e.target.value)}>
              <option value="">Select employee</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.employee_id} - {emp.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Review Period <span className="required">*</span>
            <select value={form.periodId} onChange={(e) => update('periodId', e.target.value)}>
              <option value="">Select period</option>
              {periods.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <h3>Performance Ratings (1 - 5)</h3>
        <div className="rating-rows">
          {RATINGS.map((r) => (
            <div key={r.key} className="rating-row">
              <span>
                {r.label} <span className="required">*</span>
              </span>
              <StarRating value={form[r.key]} onChange={(v) => update(r.key, v)} />
            </div>
          ))}
        </div>

        <label className="comments-field">
          Overall Comments <span className="required">*</span>
          <textarea
            rows={4}
            placeholder="Enter your feedback, strengths, areas of improvement..."
            value={form.comments}
            onChange={(e) => update('comments', e.target.value)}
          />
        </label>

        {errors.length > 0 && (
          <ul className="error">
            {errors.map((msg) => (
              <li key={msg}>{msg}</li>
            ))}
          </ul>
        )}
        {success && <p className="success">{success}</p>}

        <div className="form-actions">
          <button type="button" className="secondary" onClick={reset} disabled={isSubmitting}>
            Reset
          </button>
          <button type="submit" className="primary" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit Review'}
          </button>
        </div>
      </form>
    </section>
  );
}
