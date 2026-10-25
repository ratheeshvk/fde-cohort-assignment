-- Sample data for performance_reviews table
-- 25 reviews across employees and review periods

INSERT INTO performance_reviews (
    employee_id,
    period_id,
    quality_rating,
    delivery_rating,
    teamwork_rating,
    comments
) VALUES
(1,  9, 5, 4, 5, 'Excellent quality and strong collaboration.'),
(2,  9, 4, 5, 4, 'Consistently delivered work on time.'),
(3,  9, 4, 4, 4, 'Good performance with reliable delivery.'),
(4,  9, 5, 5, 5, 'Outstanding performance across all areas.'),
(5,  9, 3, 4, 4, 'Good progress with some areas for improvement.'),

(6,  10, 4, 4, 5, 'Strong teamwork and consistent delivery.'),
(7,  10, 5, 5, 4, 'Excellent technical contribution.'),
(8,  10, 4, 3, 4, 'Good overall performance; delivery can improve.'),
(9,  10, 3, 3, 4, 'Needs improvement in delivery consistency.'),
(10, 10, 5, 4, 5, 'Strong contribution and good team collaboration.'),

(11, 9, 4, 4, 5, 'Good collaboration and dependable delivery.'),
(12, 9, 5, 4, 4, 'High-quality work with strong ownership.'),
(13, 9, 3, 4, 3, 'Meets expectations with some improvement needed.'),
(14, 9, 4, 5, 5, 'Very strong delivery and teamwork.'),
(15, 9, 5, 5, 5, 'Exceptional performance throughout the period.'),

(16, 10, 4, 4, 4, 'Consistent performance across all areas.'),
(17, 10, 5, 4, 5, 'Excellent quality and collaboration.'),
(18, 10, 4, 5, 4, 'Strong delivery and good overall performance.'),
(19, 10, 3, 3, 3, 'Performance meets minimum expectations.'),
(20, 10, 5, 5, 4, 'Excellent delivery with strong teamwork.'),

(21, 9, 4, 4, 5, 'Strong team player with consistent results.'),
(22, 9, 5, 4, 4, 'High-quality work and good delivery.'),
(23, 9, 4, 3, 4, 'Good quality; delivery needs some improvement.'),
(24, 10, 5, 5, 5, 'Outstanding performance and leadership.'),
(25, 10, 4, 4, 5, 'Very good performance and collaboration.')
ON CONFLICT (employee_id, period_id) DO NOTHING;