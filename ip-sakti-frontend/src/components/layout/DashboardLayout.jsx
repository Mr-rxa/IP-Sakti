import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DashboardSidebar from '../common/DashboardSidebar'
import AccountMenu from '../common/AccountMenu'
import Modal from '../common/Modal'
import { useAppContext } from '../../context/AppContext'

export default function DashboardLayout({ children, activePath }) {
  const navigate = useNavigate()
  const { jurisdiction, setJurisdiction, activeModal, setActiveModal } = useAppContext()

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        navigate('/chat')
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate])

  return (
    <div className="reference-dashboard">
      <DashboardSidebar activePath={activePath} />
      <div className="dashboard-main">
        <header className="reference-topbar">
          <div
            className="global-search"
            onClick={() => navigate('/chat')}
            role="button"
            tabIndex={0}
            aria-label="Search laws, products, plants, or ask an IP question"
          >
            <span>⌕</span>
            <span>Search laws, Ayurvedic formulations, plants, or ask a question...</span>
            <kbd>Ctrl K</kbd>
          </div>

          <div className="topbar-right-group">
            {/* Interactive Jurisdiction Switcher */}
            <div className="topbar-jurisdiction-switch">
              <button
                type="button"
                className={`jurisdiction-chip ${jurisdiction === 'India' ? 'active-india' : ''}`}
                onClick={() => setJurisdiction('India')}
                title="Switch to Indian Legal Framework"
              >
                <span className="chip-dot dot-india" />
                <span>India</span>
              </button>
              <button
                type="button"
                className={`jurisdiction-chip ${jurisdiction === 'International' ? 'active-intl' : ''}`}
                onClick={() => setJurisdiction('International')}
                title="Switch to International Legal Treaties (PCT, TRIPS, WIPO)"
              >
                <span className="chip-dot dot-intl" />
                <span>International</span>
              </button>
            </div>

            {/* Account Profile Menu */}
            <div className="topbar-account-wrap">
              <AccountMenu />
            </div>
          </div>
        </header>

        <main className="reference-content inner-page-content">
          {children}
        </main>

        <footer className="site-footer">
          <div className="footer-warning">
            <span className="warning-caret">⚠</span>
            <div>
              <strong>LEGAL DISCLAIMER</strong>
              <p>
                © 2026 IP Shakti. Legal Disclaimer: This AI provides informational guidance based on existing AYUSH frameworks and statutory sources. It does not constitute formal legal counsel.
              </p>
            </div>
          </div>
          <div className="footer-links">
            <button type="button" className="footer-link-btn" onClick={() => setActiveModal('terms')}>
              Terms of Service
            </button>
            <button type="button" className="footer-link-btn" onClick={() => setActiveModal('privacy')}>
              Privacy Policy
            </button>
            <button type="button" className="footer-link-btn" onClick={() => setActiveModal('access')}>
              Institutional Access
            </button>
          </div>
        </footer>
      </div>

      <Modal
        isOpen={activeModal === 'terms'}
        title="Terms of Service"
        onClose={() => setActiveModal(null)}
      >
        <p>
          IP-SHAKTI provides AI-assisted analytical tools for traditional knowledge and intellectual property compliance. All analysis generated is for preliminary research and guidance only.
        </p>
        <p>
          Statutory filings under the Patents Act 1970, GI Act 1999, and Biological Diversity Act 2002 require verification by registered patent attorneys or legal practitioners.
        </p>
      </Modal>

      <Modal
        isOpen={activeModal === 'privacy'}
        title="Privacy Policy &amp; Data Security"
        onClose={() => setActiveModal(null)}
      >
        <p>
          Your formulation queries, bio-resource disclosures, and proprietary research inputs are strictly confidential and encrypted in transit.
        </p>
        <p>
          IP-SHAKTI does not index or store unpublished formulation data in public AI training sets.
        </p>
      </Modal>

      <Modal
        isOpen={activeModal === 'access'}
        title="Institutional &amp; Enterprise Access"
        onClose={() => setActiveModal(null)}
      >
        <p>
          AYUSH Research Institutes, University Innovation Hubs, and Pharmaceutical R&amp;D labs can request institutional API access and dedicated TKDL integration.
        </p>
        <p>
          Contact <strong>institutional@ipshakti.gov.in</strong> for multi-user enterprise access.
        </p>
      </Modal>
    </div>
  )
}
