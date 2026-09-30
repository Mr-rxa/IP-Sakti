import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import DashboardLayout from '../components/layout/DashboardLayout'

const steps = ['Origin', 'Formulation', 'Market Intent']

function Result() {
  const navigate = useNavigate()
  const { historyEntries } = useAppContext()
  const [selectedId, setSelectedId] = useState(historyEntries[0]?.id || 1)

  const currentResult = historyEntries.find((e) => e.id === selectedId) || historyEntries[0] || {
    title: 'No Assessments Yet',
    tag: 'Pending',
    summary: 'Submit a query or classification to view assessment results.',
    citations: [],
  }

  return (
    <DashboardLayout activePath="/result">
      <div className="content-shell" style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div className="result-card-panel history-panel" style={{ width: '100%' }}>
          <div className="wizard-tracker">
            {steps.map((step) => (
              <div key={step} className="tracker-step done">
                <span>✓</span>
                <label>{step}</label>
              </div>
            ))}
          </div>

          <div className="history-header-row">
            <span className="history-label">My saved results and answer proof</span>
            <span className="history-count">{historyEntries.length} saved assessments</span>
          </div>

          <div className="history-layout">
            <div className="history-summary-box">
              <span className="result-badge">{currentResult.tag}</span>
              <h2>{currentResult.title}</h2>
              <p>{currentResult.summary}</p>
              {currentResult.detail && <p style={{ fontSize: '0.9rem', opacity: 0.9 }}>{currentResult.detail}</p>}

              {currentResult.citations && currentResult.citations.length > 0 && (
                <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--line)' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--heading)' }}>Answer proof: sources used</h4>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--muted)', fontSize: '0.9rem' }}>
                    {currentResult.citations.map((cite) => (
                      <li key={cite} style={{ marginBottom: '0.25rem' }}>{cite}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <aside className="history-list-panel">
              {historyEntries.map((entry) => (
                <button
                  type="button"
                  key={entry.id}
                  className={`history-item ${currentResult.id === entry.id ? 'selected' : ''}`}
                  onClick={() => setSelectedId(entry.id)}
                >
                  <div className="history-item-top">
                    <span className="mini-tag">{entry.tag}</span>
                    <span className="history-date">{entry.date}</span>
                  </div>
                  <strong>{entry.title}</strong>
                  <small>{entry.detail || entry.summary}</small>
                </button>
              ))}
            </aside>
          </div>

          <div className="bottom-actions result-actions">
            <button type="button" className="secondary-btn ghost-btn" onClick={() => navigate('/drug-classification')}>
              ← Back to Wizard
            </button>
            <button type="button" className="primary-btn" onClick={() => navigate('/chat')}>
              Continue to AI Review →
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default Result
