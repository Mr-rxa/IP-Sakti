import { createContext, useContext, useMemo, useState, useEffect } from 'react'
import { getStoredToken, getStoredUser, getUserActivity, logoutUser } from '../services/authService'
import { createSession, setSessionJurisdiction, getActiveSessionId } from '../services/sessionService'

const AppContext = createContext(null)

const INITIAL_HISTORY = []

export function AppProvider({ children }) {
  const [jurisdiction, setJurisdictionState] = useState('India')
  const [sessionId, setSessionId] = useState(getActiveSessionId())
  
  // Persistent Auth State from localStorage
  const existingToken = getStoredToken()
  const existingUser = getStoredUser()
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(existingToken))
  const [currentUser, setCurrentUser] = useState(existingUser)
  const [userRole, setUserRole] = useState(existingUser?.role || 'AYUSH Practitioner')

  const [historyEntries, setHistoryEntries] = useState(() => {
    try {
      const saved = localStorage.getItem('ip_shakti_history')
      return saved ? JSON.parse(saved) : INITIAL_HISTORY
    } catch (_) {
      return INITIAL_HISTORY
    }
  })

  const [activeModal, setActiveModal] = useState(null) // 'terms' | 'privacy' | 'access' | null

  // Ensure an active backend session exists
  useEffect(() => {
    if (!sessionId) {
      createSession().then((res) => {
        if (res?.session_id) {
          setSessionId(res.session_id)
        }
      })
    }
  }, [sessionId])

  useEffect(() => {
    if (!isAuthenticated) return
    getUserActivity()
      .then((data) => {
        const items = (data?.items || []).map((item) => ({
          id: item.id,
          title: item.title,
          tag: item.kind === 'escalation' ? 'Review request' : item.status,
          summary: item.summary,
          detail: item.detail,
          date: new Date(item.created_at).toLocaleDateString('en-GB'),
          citations: [],
        }))
        setHistoryEntries(items)
      })
      .catch(() => {})
  }, [isAuthenticated])

  // Save history entries to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('ip_shakti_history', JSON.stringify(historyEntries))
    } catch (_) {}
  }, [historyEntries])

  const setJurisdiction = (newJurisdiction) => {
    setJurisdictionState(newJurisdiction)
    if (sessionId) {
      setSessionJurisdiction(sessionId, newJurisdiction).catch(() => {})
    }
  }

  const addHistoryEntry = (entry) => {
    const newEntry = {
      id: Date.now(),
      date: new Date().toLocaleDateString('en-GB'),
      citations: ['Indian Patents Act 1970', 'Drugs & Cosmetics Rules', 'Biological Diversity Act 2002'],
      ...entry,
    }
    setHistoryEntries((prev) => [newEntry, ...prev])
  }

  const logout = () => {
    logoutUser()
    setIsAuthenticated(false)
    setCurrentUser(null)
    setUserRole('AYUSH Practitioner')
    setHistoryEntries([])
    try {
      localStorage.removeItem('ip_shakti_history')
      sessionStorage.removeItem('ip_shakti_session_id')
    } catch (_) {}
  }

  const value = useMemo(
    () => ({
      jurisdiction,
      setJurisdiction,
      sessionId,
      setSessionId,
      isAuthenticated,
      setIsAuthenticated,
      currentUser,
      setCurrentUser,
      userRole,
      setUserRole,
      logout,
      historyEntries,
      addHistoryEntry,
      activeModal,
      setActiveModal,
    }),
    [jurisdiction, sessionId, isAuthenticated, currentUser, userRole, historyEntries, activeModal],
  )

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useAppContext() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider')
  }
  return context
}
