import { NavLink, useNavigate } from 'react-router-dom'
import { useAppContext } from '../../context/AppContext'
import { getRoleNavigation } from '../../config/roleAccess'

function DashboardSidebar() {
  const navigate = useNavigate()
  const { userRole, jurisdiction } = useAppContext()
  const navigation = getRoleNavigation(userRole)

  return (
    <aside className="dashboard-sidebar">
      <button type="button" className="dashboard-logo" onClick={() => navigate('/')}>
        <span className="logo-leaf">✦</span>
        <span><strong>IP Shakti</strong><small>Intellectual Property for Ayurveda</small></span>
      </button>

      <div className="sidebar-context">
        <span className="sidebar-context-dot" />
        <span>{jurisdiction} workspace</span>
      </div>

      <nav className="dashboard-nav" aria-label="Workspace navigation">
        {navigation.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'}>
            <span className="nav-glyph" aria-hidden="true">{item.to === '/' ? '⌂' : item.to === '/result' ? '◌' : item.to === '/library' ? '▤' : '◇'}</span>
            {item.label}
          </NavLink>
        ))}
        <NavLink to="/how-it-works"><span className="nav-glyph" aria-hidden="true">?</span>How it works</NavLink>
      </nav>

      <div className="dashboard-sidebar-bottom">
        <div className="sidebar-divider" />
        <span className="sidebar-note">Information, not legal advice.</span>
      </div>
    </aside>
  )
}

export default DashboardSidebar
