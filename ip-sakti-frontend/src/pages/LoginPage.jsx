import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import { loginUser, registerUser } from '../services/authService'

function LoginPage() {
  const navigate = useNavigate()
  const { setIsAuthenticated, setUserRole, setCurrentUser } = useAppContext()
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({
    email: '',
    password: '',
    fullName: '',
    role: 'AYUSH Practitioner',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!form.email || !form.password) {
      setError('Please enter both email and password.')
      return
    }

    if (form.password.length < 6) {
      setError('Password must be at least 6 characters long.')
      return
    }

    setLoading(true)
    try {
      let res
      if (isRegister) {
        res = await registerUser(form.email, form.password, form.role, form.fullName)
      } else {
        res = await loginUser(form.email, form.password, form.role)
      }

      if (res?.user) {
        setUserRole(res.user.role || form.role)
        setCurrentUser(res.user)
      } else {
        setUserRole(form.role)
      }
      setIsAuthenticated(true)
      navigate('/')
    } catch (err) {
      console.error('Auth error:', err)
      setError(err.message || 'Authentication failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="brand-mark">IP</span>
          <span className="brand-name">Shakti</span>
        </div>

        <h1>{isRegister ? 'Create Account' : 'Welcome Back'}</h1>
        <p className="auth-subtitle">
          {isRegister
            ? 'Register for IP-SHAKTI Sahayak AYUSH Portal'
            : 'Access your IP-SHAKTI dashboard & IPR tools'}
        </p>

        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', borderBottom: '1px solid var(--line)', paddingBottom: '0.5rem' }}>
          <button
            type="button"
            className={`tab-btn ${!isRegister ? 'active-tab' : ''}`}
            onClick={() => { setIsRegister(false); setError('') }}
            style={{
              flex: 1,
              background: !isRegister ? 'var(--accent)' : 'transparent',
              color: !isRegister ? '#fff' : 'var(--text)',
              border: 'none',
              borderRadius: '6px',
              padding: '0.5rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`tab-btn ${isRegister ? 'active-tab' : ''}`}
            onClick={() => { setIsRegister(true); setError('') }}
            style={{
              flex: 1,
              background: isRegister ? 'var(--accent)' : 'transparent',
              color: isRegister ? '#fff' : 'var(--text)',
              border: 'none',
              borderRadius: '6px',
              padding: '0.5rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {isRegister && (
            <label>
              Full Name
              <input
                type="text"
                name="fullName"
                value={form.fullName}
                onChange={handleChange}
                placeholder="Dr. Vaidya Sharma"
              />
            </label>
          )}

          <label>
            Email Address
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="user@ayush-innovations.in"
              required
            />
          </label>

          <label>
            User Persona / Role
            <select name="role" value={form.role} onChange={handleChange}>
              <option>AYUSH Practitioner</option>
              <option>Legal Researcher</option>
              <option>IP Consultant</option>
              <option>Academic Researcher</option>
              <option>MSME / Startup Founder</option>
            </select>
          </label>

          <label>
            Password
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="At least 6 characters"
              required
            />
          </label>

          {error && <p className="auth-error" style={{ color: '#e53e3e', fontSize: '0.9rem', marginTop: '0.25rem' }}>{error}</p>}

          <button type="submit" className="primary-btn auth-btn" disabled={loading} style={{ marginTop: '0.75rem' }}>
            {loading ? 'Authenticating...' : (isRegister ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <div style={{ marginTop: '1.25rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--muted)' }}>
          <span>Powered by Supabase Auth &amp; PostgreSQL</span>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
