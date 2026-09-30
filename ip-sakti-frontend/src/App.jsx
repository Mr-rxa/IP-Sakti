import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppContext } from './context/AppContext'
import LoginPage from './pages/LoginPage'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Library from './pages/Library'
import Result from './pages/Result'
import TrademarkSearch from './pages/TrademarkSearch'
import GIRegistration from './pages/GIRegistration'
import ABSCompliance from './pages/ABSCompliance'
import DrugClassification from './pages/DrugClassification'
import NotFound from './pages/NotFound'
import Profile from './pages/Profile'
import HowItWorks from './pages/HowItWorks'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAppContext()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  const { userRole, jurisdiction, isAuthenticated } = useAppContext()

  return (
    <div
      className="app-shell"
      style={{ '--jurisdiction-image': `url(/${jurisdiction === 'International' ? 'international' : 'indian'}.jpeg)` }}
    >
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/how-it-works"
          element={
            <ProtectedRoute>
              <HowItWorks />
            </ProtectedRoute>
          }
        />

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home userRole={userRole} />
            </ProtectedRoute>
          }
        />

        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />

        <Route
          path="/trademark"
          element={
            <ProtectedRoute>
              <TrademarkSearch />
            </ProtectedRoute>
          }
        />

        <Route
          path="/gi-registration"
          element={
            <ProtectedRoute>
              <GIRegistration />
            </ProtectedRoute>
          }
        />

        <Route
          path="/abs-compliance"
          element={
            <ProtectedRoute>
              <ABSCompliance />
            </ProtectedRoute>
          }
        />

        <Route
          path="/drug-classification"
          element={
            <ProtectedRoute>
              <DrugClassification />
            </ProtectedRoute>
          }
        />

        <Route
          path="/classification"
          element={
            <ProtectedRoute>
              <DrugClassification />
            </ProtectedRoute>
          }
        />

        <Route
          path="/library"
          element={
            <ProtectedRoute>
              <Library />
            </ProtectedRoute>
          }
        />

        <Route
          path="/result"
          element={
            <ProtectedRoute>
              <Result />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

export default App
