import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import DashboardLayout from '../components/layout/DashboardLayout'

function Profile() {
  const navigate = useNavigate()
  const { currentUser, userRole, jurisdiction } = useAppContext()

  return (
    <DashboardLayout activePath="/profile">
      <div className="content-shell" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <main className="profile-content" style={{ padding: 0 }}>
          <section className="profile-header-panel">
            <div className="profile-avatar-large">{(currentUser?.full_name || currentUser?.email || 'A').slice(0, 1).toUpperCase()}</div>
            <div>
              <span className="query-tag">ACCOUNT PROFILE</span>
              <h1>{currentUser?.full_name || 'Your profile'}</h1>
              <p>{currentUser?.email || 'Signed-in account'} · {userRole}</p>
            </div>
          </section>

          <section className="profile-details-panel">
            <div>
              <span className="profile-detail-label">Full name</span>
              <strong>{currentUser?.full_name || 'Not provided'}</strong>
            </div>
            <div>
              <span className="profile-detail-label">Email</span>
              <strong>{currentUser?.email || 'Not available'}</strong>
            </div>
            <div>
              <span className="profile-detail-label">Workspace role</span>
              <strong>{userRole}</strong>
            </div>
            <div>
              <span className="profile-detail-label">Current legal scope</span>
              <strong>{jurisdiction}</strong>
            </div>
          </section>

          <div className="profile-actions">
            <button type="button" className="secondary-btn" onClick={() => navigate('/result')}>View activity</button>
            <button type="button" className="primary-btn" onClick={() => navigate('/')}>Back to dashboard</button>
          </div>
        </main>
      </div>
    </DashboardLayout>
  )
}

export default Profile
