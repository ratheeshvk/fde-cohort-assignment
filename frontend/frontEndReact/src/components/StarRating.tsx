interface StarRatingProps {
  value: number;
  max?: number;
  // When provided, the stars become clickable buttons
  onChange?: (value: number) => void;
}

export default function StarRating({ value, max = 5, onChange }: StarRatingProps) {
  return (
    <span className="stars" aria-label={`${value} out of ${max}`}>
      {Array.from({ length: max }, (_, i) => {
        const className = i < value ? 'star filled' : 'star';
        return onChange ? (
          <button
            key={i}
            type="button"
            className={`${className} star-button`}
            aria-label={`Rate ${i + 1}`}
            onClick={() => onChange(i + 1)}
          >
            ★
          </button>
        ) : (
          <span key={i} className={className}>
            ★
          </span>
        );
      })}
    </span>
  );
}
