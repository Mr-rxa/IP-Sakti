import { NavLink } from 'react-router-dom'
import { useAppContext } from '../../context/AppContext'
import { getRoleNavigation } from '../../config/roleAccess'

function RoleNavigation({ activePath }) {
  const { userRole } = useAppContext()
  const navigation = getRoleNavigation(userRole)

  return (
    <nav className="side-nav" aria-label="Role-based workspace navigation">
      {navigation.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={item.to === activePath ? 'active' : undefined}
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default RoleNavigation
