import { useEffect, useState } from 'react'
import Header from './components/header'
import LoginPage from './components/LoginPage'
import ReviewForm from './components/ReviewForm'
import ReviewList from './components/ReviewList'
import ReviewDetails from './components/ReviewDetails'
import { getMe, logout, setUnauthorizedHandler } from './api'
import type { AdminUser } from './auth'
import type { Review } from './type'
import './App.css'

function App() {
  // undefined = still checking the login cookie, null = logged out
  const [user, setUser] = useState<AdminUser | null | undefined>(undefined)
  const [authError, setAuthError] = useState<string | null>(null)
  const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null))
    getMe()
      .then(setUser)
      .catch((err: Error) => {
        setAuthError(err.message)
        setUser(null)
      })
  }, [])

  const handleLogin = (admin: AdminUser) => {
    setAuthError(null)
    setSelectedReviewId(null)
    setUser(admin)
  }

  const handleLogout = async () => {
    try {
      await logout()
    } finally {
      setUser(null)
    }
  }

  const handleSubmitted = (review: Review) => {
    setRefreshKey((k) => k + 1)
    setSelectedReviewId(review.id)
  }

  if (user === undefined) {
    return <p className="loading">Loading…</p>
  }

  if (user === null) {
    return (
      <>
        {authError && <p className="error">Could not reach the server: {authError}</p>}
        <LoginPage onLogin={handleLogin} />
      </>
    )
  }

  return (
    <>
      <Header title="Performance Reviews" username={user.username} onLogout={handleLogout} />
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
