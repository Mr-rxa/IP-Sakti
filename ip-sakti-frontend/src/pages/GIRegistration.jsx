import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import DashboardLayout from '../components/layout/DashboardLayout'

const GI_DATABASE = [
  { herb: 'Kashmiri Saffron (Lachha)', region: 'Jammu & Kashmir', status: 'Registered GI (Tag #635)', class: 'Agricultural / Medicinal', details: 'Protected under GI Act 1999. High crocin content and deep aroma signature.' },
  { herb: 'Darjeeling Black Tea / Ortho', region: 'West Bengal', status: 'Registered GI (Tag #1)', class: 'Agricultural', details: 'First GI registered in India. Strict geographical contour enforcement.' },
  { herb: 'Vazhakulam Pineapple', region: 'Kerala', status: 'Registered GI (Tag #130)', class: 'Agricultural', details: 'High sugar content, medicinal use in traditional Ayurvedic tonic preparations.' },
  { herb: 'Malabar Pepper', region: 'Kerala / Karnataka', status: 'Registered GI (Tag #57)', class: 'Agricultural / Spices', details: 'Key ingredient in Trikatu formulations (Pippali, Maricha, Sunthi).' },
  { herb: 'Nanjanagud Banana', region: 'Karnataka', status: 'Registered GI (Tag #28)', class: 'Agricultural', details: 'Used in traditional Rasayana preparations.' },
]

function GIRegistration() {
  const navigate = useNavigate()
  const { addHistoryEntry } = useAppContext()
  const [herbQuery, setHerbQuery] = useState('')
  const [region, setRegion] = useState('All Regions')
  const [selectedHerb, setSelectedHerb] = useState(GI_DATABASE[0])

  const handleSaveGIResult = () => {
    if (selectedHerb) {
      addHistoryEntry({
        title: `GI Tag Analysis: ${selectedHerb.herb}`,
        tag: selectedHerb.status,
        summary: `Origin Region: ${selectedHerb.region}. Category: ${selectedHerb.class}`,
        detail: `Requirements: Certificate of Origin & Authorized User registration under Form GI-3. ${selectedHerb.details}`,
      })
    }
    navigate('/result')
  }

  const filteredDB = GI_DATABASE.filter((item) => {
    const matchesHerb = item.herb.toLowerCase().includes(herbQuery.toLowerCase()) ||
      item.details.toLowerCase().includes(herbQuery.toLowerCase())
    const matchesRegion = region === 'All Regions' || item.region.includes(region)
    return matchesHerb && matchesRegion
  })

  return (
    <DashboardLayout activePath="/gi-registration">
      <div className="content-shell">
        <section className="query-shell" style={{ width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
          <div className="query-header-row">
            <span className="query-tag" style={{ background: '#3c9d4c', color: '#fff' }}>GEOGRAPHICAL INDICATIONS (GI) REGISTRY</span>
            <span className="query-tag tag-right">GI ACT 1999 COMPLIANCE</span>
          </div>

          <h1>Traditional Herbal &amp; Agricultural GI Portal</h1>
          <p className="subtext">Verify geographical indication tags, heritage origin claims, and authorized user status for traditional Ayurvedic flora.</p>

          <div className="ask-form-controls" style={{ marginTop: '1.5rem', marginBottom: '1.5rem', gap: '0.75rem' }}>
            <input
              type="text"
              placeholder="Search traditional herb, flora, or medicinal plant..."
              value={herbQuery}
              onChange={(e) => setHerbQuery(e.target.value)}
              style={{
                flex: 1,
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--line)',
                background: 'var(--panel)',
                color: 'var(--heading)',
              }}
            />
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--line)',
                background: 'var(--panel)',
                color: 'var(--heading)',
              }}
            >
              <option>All Regions</option>
              <option>Kerala</option>
              <option>Karnataka</option>
              <option>Jammu &amp; Kashmir</option>
              <option>West Bengal</option>
            </select>
          </div>

          <div className="option-list" style={{ display: 'grid', gap: '1rem' }}>
            {filteredDB.map((item) => (
              <div
                key={item.herb}
                className="option-row"
                style={{
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  cursor: 'pointer',
                  borderColor: selectedHerb?.herb === item.herb ? 'var(--accent)' : 'var(--line)',
                  background: selectedHerb?.herb === item.herb ? 'var(--panel-strong)' : 'var(--panel)',
                }}
                onClick={() => setSelectedHerb(item)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '0.25rem' }}>
                  <strong style={{ fontSize: '1.1rem', color: 'var(--heading)' }}>{item.herb}</strong>
                  <span className="mini-tag" style={{ background: '#3c9d4c', color: '#fff' }}>{item.status}</span>
                </div>
                <small style={{ color: 'var(--muted)', marginBottom: '0.5rem' }}>Region: {item.region} | Category: {item.class}</small>
                <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text)' }}>{item.details}</p>
              </div>
            ))}
          </div>

          {selectedHerb && (
            <div className="assessment-box" style={{ marginTop: '1.5rem' }}>
              <div className="assessment-icon">🌿</div>
              <div>
                <h3>GI Clearance &amp; Authorized User Guidance</h3>
                <p>
                  To market <strong>{selectedHerb.herb}</strong> with geographical indication labeling, you must register as an <em>Authorized User</em> under Form GI-3 with the GI Registry in Chennai.
                </p>
                <p>
                  <strong>Proof of Origin Required:</strong> Certificate from state agriculture department or certified producer union in {selectedHerb.region}.
                </p>
              </div>
            </div>
          )}

          <div className="action-row" style={{ marginTop: '2rem' }}>
            <button className="primary-btn" type="button" onClick={handleSaveGIResult}>
              Save to Assessment History →
            </button>
            <button className="secondary-btn light-btn" type="button" onClick={() => navigate('/chat')}>
              Consult AI on GI Claim
            </button>
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}

export default GIRegistration
