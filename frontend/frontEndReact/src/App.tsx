import { useState } from 'react'
import Header from './components/header'
import ReviewForm from './components/ReviewForm'
import ReviewList from './components/ReviewList'
import ReviewDetails from './components/ReviewDetails'
import type { Review } from './type'
import './App.css'

function App() {
  const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleSubmitted = (review: Review) => {
    setRefreshKey((k) => k + 1)
    setSelectedReviewId(review.id)
  }

  return (
    <>
      <Header title="Performance Reviews" />
      <div className="review-layout">
        <div className="panel form-panel">
          <ReviewForm onSubmitted={handleSubmitted} />
        </div>
        <div className="panel">
          <ReviewList
            selectedReviewId={selectedReviewId}
            onSelectReview={setSelectedReviewId}
            refreshKey={refreshKey}
          />
        </div>
        <div className="panel">
          {selectedReviewId !== null ? (
            <ReviewDetails reviewId={selectedReviewId} onClose={() => setSelectedReviewId(null)} />
          ) : (
            <section className="review-details">
              <h2>Review Details</h2>
              <p className="muted">Select an Employee ID or View to see review details.</p>
            </section>
          )}
        </div>
      </div>
    </>
  )
}

export default App
