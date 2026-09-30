import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../../context/AppContext'

function AccountMenu() {
  const navigate = useNavigate()
  const { currentUser, userRole, logout } = useAppContext()
  const [open, setOpen] = useState(false)
  const displayName = currentUser?.full_name || currentUser?.email?.split('@')[0] || 'Account'
  const email = currentUser?.email || 'Signed-in user'

  const handleLogout = () => {
    logout()
    setOpen(false)
    navigate('/login', { replace: true })
  }

  return (
    <div className="account-menu">
      <button
        type="button"
        className="account-trigger"
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((value) => !value)}
      >
        <span className="account-avatar" aria-hidden="true">{displayName.slice(0, 1).toUpperCase()}</span>
        <span className="account-trigger-copy">
          <strong>{displayName}</strong>
          <small>{userRole}</small>
        </span>
        <span aria-hidden="true">▾</span>
      </button>

      {open && (
        <div className="account-popover" role="menu">
          <div className="account-popover-header">
            <strong>{displayName}</strong>
            <span>{email}</span>
            <small>{userRole}</small>
          </div>
          <button type="button" role="menuitem" onClick={() => { setOpen(false); navigate('/profile') }}>
            My profile
          </button>
          <button type="button" role="menuitem" onClick={() => navigate('/result')}>
            My activity
          </button>
          <button type="button" className="account-logout" role="menuitem" onClick={handleLogout}>
            Log out
          </button>
        </div>
      )}
    </div>
  )
}

export default AccountMenu
