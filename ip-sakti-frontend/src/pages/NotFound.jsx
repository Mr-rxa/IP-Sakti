import { Link } from 'react-router-dom'

function NotFound() {
  return (
    <div className="empty-state auth-page">
      <h1>404</h1>
      <p>Page not found.</p>
      <Link to="/login" className="primary-btn inline-link-btn">
        Go to Login
      </Link>
    </div>
  )
}

export default NotFound
