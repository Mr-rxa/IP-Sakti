import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import { sendChatMessage } from '../services/chatService'
import { escalateToFacilitator } from '../services/sessionService'
import DashboardLayout from '../components/layout/DashboardLayout'

function formatInline(str) {
  if (!str) return ''
  return str
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

function FormattedAnswer({ text }) {
  if (!text) return null

  // Line-by-line block parser for headings, lists, and paragraphs
  const lines = text.split('\n')
  const elements = []
  let currentList = null // { type: 'ul' | 'ol', items: [] }

  const flushList = () => {
    if (currentList) {
      const Tag = currentList.type
      elements.push(
        <Tag key={elements.length} style={{ margin: '0.4rem 0 0.8rem 1.35rem', padding: 0 }}>
          {currentList.items.map((item, itemIdx) => (
            <li
              key={itemIdx}
              style={{ marginBottom: '0.35rem' }}
              dangerouslySetInnerHTML={{ __html: formatInline(item) }}
            />
          ))}
        </Tag>
      )
      currentList = null
    }
  }

  lines.forEach((line) => {
    const trimmed = line.trim()
    if (!trimmed) {
      flushList()
      return
    }

    if (trimmed.startsWith('### ')) {
      flushList()
      elements.push(
        <h4
          key={elements.length}
          style={{
            margin: '1.2rem 0 0.4rem 0',
            fontSize: '1.05rem',
            fontWeight: 700,
            color: 'var(--brand, #1a365d)',
          }}
        >
          {trimmed.replace(/^###\s*/, '')}
        </h4>
      )
    } else if (trimmed.startsWith('* ') || trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
      const itemText = trimmed.replace(/^[\*\•\-]\s*/, '')
      if (currentList && currentList.type === 'ul') {
        currentList.items.push(itemText)
      } else {
        flushList()
        currentList = { type: 'ul', items: [itemText] }
      }
    } else if (/^\d+\.\s+/.test(trimmed)) {
      const itemText = trimmed.replace(/^\d+\.\s+/, '')
      if (currentList && currentList.type === 'ol') {
        currentList.items.push(itemText)
      } else {
        flushList()
        currentList = { type: 'ol', items: [itemText] }
      }
    } else {
      flushList()
      elements.push(
        <p
          key={elements.length}
          style={{ marginBottom: '0.75rem' }}
          dangerouslySetInnerHTML={{ __html: formatInline(trimmed) }}
        />
      )
    }
  })

  flushList()

  return (
    <div style={{ lineHeight: '1.6', fontSize: '0.98rem' }}>
      {elements}
    </div>
  )
}

function Chat() {
  const navigate = useNavigate()
  const {
    jurisdiction,
    setJurisdiction,
    sessionId,
    userRole,
    addHistoryEntry,
  } = useAppContext()

  const [query, setQuery] = useState('')
  const [role, setRole] = useState(userRole || 'AYUSH Practitioner')
  const [category, setCategory] = useState('Classical/Generic Medicine')
  const [isLoading, setIsLoading] = useState(false)
  const [assessmentResult, setAssessmentResult] = useState(null)
  const [queryError, setQueryError] = useState('')
  const [escalated, setEscalated] = useState(false)
  const [escalateMsg, setEscalateMsg] = useState('')

  const [isEscalating, setIsEscalating] = useState(false)

  const starterQuestions = jurisdiction === 'India'
    ? [
      'Can I patent a classical Ayurvedic formulation in India?',
      'What should I check before using an Indian plant in my product?',
      'How can I protect the name of my Ayurvedic product?',
    ]
    : [
      'What does TRIPS say about traditional knowledge?',
      'What is the Nagoya Protocol about?',
      'How does the PCT help with an international patent filing?',
    ]

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setQueryError('')
    setEscalated(false)
    setEscalateMsg('')

    try {
      const response = await sendChatMessage(query, {
        session_id: sessionId,
        jurisdiction,
        classification_context: category,
      })
      setAssessmentResult(response)

      addHistoryEntry({
        title: `Patent Assessment: ${query.slice(0, 30)}...`,
        tag: `${jurisdiction} (${response.confidenceLabel})`,
        summary: response.summary,
        detail: response.assessment,
        citations: response.citations,
      })
    } catch (err) {
      console.error('Query error:', err)
      setQueryError(err.message || 'We could not check the trusted documents. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleEscalate = async () => {
    if (!assessmentResult || isEscalating) return
    setIsEscalating(true)
    try {
      const res = await escalateToFacilitator(sessionId, assessmentResult.queryId)
      setEscalated(true)
      setEscalateMsg(
        res?.expert_assigned
          ? `Your request was assigned to an AYUSH IP expert (Reference: ${res?.escalation_id?.slice(0, 8) || 'ESC-2026'}).`
          : `Your request was recorded (Reference: ${res?.escalation_id?.slice(0, 8) || 'ESC-2026'}). No human expert is currently assigned.`
      )
    } catch (err) {
      setEscalated(true)
      setEscalateMsg('Your help request was recorded. No human expert is currently assigned.')
    } finally {
      setIsEscalating(false)
    }
  }

  return (
    <DashboardLayout activePath="/chat">
      <div className="content-shell">
        <section className="query-shell" style={{ width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
          <div className="query-header-row">
            <span className="query-tag">SOURCE-CHECKED ANSWER</span>
            <span className="query-tag tag-right">
              {assessmentResult ? assessmentResult.queryId : `ID: AYU-${jurisdiction.toUpperCase()}`}
            </span>
          </div>

          <h1>Ask About Your Ayurvedic Product</h1>

          <div className="confidence-row">
            <span>{assessmentResult ? 'How sure is the answer?' : 'Ready to check your question'}</span>
            <div className="confidence-bar">
              <span
                className="confidence-fill"
                style={{
                  width: assessmentResult ? `${assessmentResult.confidence}%` : '0%',
                  background: assessmentResult?.confidence >= 75 ? '#38a169' : assessmentResult?.confidence >= 40 ? '#d69e2e' : '#e53e3e',
                }}
              />
            </div>
            <strong>
              {assessmentResult
                ? `${assessmentResult.confidenceLabel || ''} (${assessmentResult.confidence}%)`
                : 'No answer yet'}
            </strong>
          </div>

          {!assessmentResult ? (
            <form className="ask-form" onSubmit={handleSubmit}>
              <textarea
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value)
                  setQueryError('')
                }}
                placeholder="Write your question in your own words..."
                rows={4}
              />
              <div className="question-help">
                <strong>Not sure what to ask?</strong>
                <div className="starter-question-list">
                  {starterQuestions.map((question) => (
                    <button
                      type="button"
                      key={question}
                      className="starter-question"
                      onClick={() => setQuery(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
              {queryError && (
                <div className="query-error" role="alert">
                  <strong>We could not check this question.</strong>
                  <span>{queryError}</span>
                </div>
              )}
              <div className="ask-form-controls">
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option>AYUSH Practitioner</option>
                  <option>Researcher</option>
                  <option>Legal Counsel</option>
                  <option>Startup Founder</option>
                </select>
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option>Classical/Generic Medicine</option>
                  <option>Patent-or-Proprietary Medicine</option>
                  <option>New/Non-classical Drug</option>
                  <option>Phytopharmaceutical</option>
                  <option>Ayurveda-Aahar/Nutraceutical</option>
                  <option>Cosmetic</option>
                </select>
                <button type="submit" className="primary-btn ask-btn" disabled={isLoading}>
                  {isLoading ? 'Checking trusted documents...' : 'Get Answer'}
                </button>
              </div>
            </form>
          ) : (
            <div className="assessment-box">
              <div className="assessment-icon">✎</div>
              <div>
                <h3>{assessmentResult.abstained ? 'We could not find a safe answer' : `Answer for ${jurisdiction}`}</h3>
                {assessmentResult.abstained && (
                  <p className="abstention-help">
                    I can help only with Ayurveda, traditional knowledge, IPR and product-rule questions covered by our trusted documents. Try one of the example questions below or ask an IP expert for help.
                  </p>
                )}
                <FormattedAnswer text={assessmentResult.assessment} />

                {assessmentResult.citations && assessmentResult.citations.length > 0 && (
                  <div style={{ marginTop: '1.25rem', paddingTop: '0.85rem', borderTop: '1px solid var(--line)' }}>
                    <strong>Sources used</strong>
                    <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.25rem' }}>
                      {assessmentResult.citations.map((c, idx) => (
                        <li key={idx} style={{ marginBottom: '0.35rem' }}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {assessmentResult.disclaimer && (
                  <div style={{ marginTop: '1rem', padding: '0.6rem 0.85rem', background: 'rgba(215, 111, 26, 0.08)', borderRadius: '6px', fontSize: '0.82rem', color: 'var(--muted)' }}>
                    ⚖️ <strong>Legal Notice:</strong> {assessmentResult.disclaimer}
                  </div>
                )}

                {escalated && (
                  <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: '#ebf8ff', borderRadius: '8px', border: '1px solid #bee3f8', color: '#2b6cb0', fontSize: '0.9rem' }}>
                    ✅ {escalateMsg}
                  </div>
                )}

                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.25rem' }}>
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={() => {
                      setAssessmentResult(null)
                      setQuery('')
                      setQueryError('')
                      setEscalated(false)
                      setEscalateMsg('')
                    }}
                  >
                    ← Ask Another Question
                  </button>
                  {!escalated && (
                    <button
                      type="button"
                      className="secondary-btn"
                      style={{ borderColor: '#d76f1a', color: '#d76f1a' }}
                      onClick={handleEscalate}
                      disabled={isEscalating}
                    >
                      {isEscalating ? 'Contacting expert...' : 'Ask an IP expert for help'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="action-row">
            <button className="primary-btn" type="button" onClick={() => navigate('/drug-classification')}>
              Classify this product →
            </button>
            <button className="secondary-btn light-btn" type="button" onClick={() => navigate('/result')}>
              View My Saved Results
            </button>
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}

export default Chat
