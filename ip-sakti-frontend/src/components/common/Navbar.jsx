import { NavLink, useNavigate } from 'react-router-dom'
import { useAppContext } from '../../context/AppContext'
import { getRoleNavigation } from '../../config/roleAccess'

function Navbar() {
  const navigate = useNavigate()
  const { jurisdiction, setJurisdiction, userRole } = useAppContext()
  const navigation = getRoleNavigation(userRole)

  return (
    <header className="topbar">
      <div className="brand-wrap" style={{ cursor: 'pointer' }} onClick={() => navigate('/')}>
        <span className="brand-mark">IP</span>
        <span className="brand-name">Shakti</span>
      </div>

      <nav className="main-nav" aria-label="Main navigation">
        {navigation.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'}>
            {item.label}
          </NavLink>
        ))}
        <NavLink to="/how-it-works">How it works</NavLink>
      </nav>

      <div className="jurisdiction-toggle" aria-label="Choose the law to use">
        <button
          type="button"
          className={`jurisdiction-option ${jurisdiction === 'India' ? 'active' : ''}`}
          onClick={() => setJurisdiction('India')}
        >
          <span className="jurisdiction-indicator" />
          India
        </button>
        <button
          type="button"
          className={`jurisdiction-option ${jurisdiction === 'International' ? 'active' : ''}`}
          onClick={() => setJurisdiction('International')}
        >
          <span className="jurisdiction-indicator" />
          International
        </button>
      </div>
    </header>
  )
}

export default Navbar
