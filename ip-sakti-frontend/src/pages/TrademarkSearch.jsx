import { useState, useEffect } from 'react'
import { useAppContext } from '../context/AppContext'
import { apiRequest } from '../services/api'
import DashboardLayout from '../components/layout/DashboardLayout'

const TRADEMARK_RESULTS = [
  { id: 1, mark: 'AYURVEDA SHAKTI', classNo: 'Class 5 (Pharmaceuticals)', status: 'Registered', owner: 'AyurMed Labs', journalNo: '1982' },
  { id: 2, mark: 'SAKTI BOTANICALS', classNo: 'Class 3 (Cosmetics)', status: 'Opposed', owner: 'Herbal Life Ltd', journalNo: '2014' },
  { id: 3, mark: 'ASHWA-SHAKTI', classNo: 'Class 5 (Ayurvedic Formulation)', status: 'Pending Examination', owner: 'Vedic Care Pvt Ltd', journalNo: 'Pending' },
  { id: 4, mark: 'SHAKTI VEDA', classNo: 'Class 30 (Dietary Supplements)', status: 'Registered', owner: 'Veda Organics', journalNo: '1850' },
  { id: 5, mark: 'TRIKATU SHAKTI', classNo: 'Class 5 (Ayurvedic Medicine)', status: 'Registered', owner: 'AyurPharma Corp', journalNo: '1744' },
]

function TrademarkSearch() {
  const { jurisdiction } = useAppContext()
  const [searchTerm, setSearchTerm] = useState('SHAKTI')
  const [selectedClass, setSelectedClass] = useState('All Classes')
  const [tkdlMatches, setTkdlMatches] = useState([])

  useEffect(() => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setTkdlMatches([])
      return
    }
    const timer = setTimeout(async () => {
      try {
        const data = await apiRequest(`/tkdl/lookup?keyword=${encodeURIComponent(searchTerm.trim())}`)
        if (data?.matches) {
          setTkdlMatches(data.matches)
        } else {
          setTkdlMatches([])
        }
      } catch (_) {
        setTkdlMatches([])
      }
    }, 350)

    return () => clearTimeout(timer)
  }, [searchTerm])

  const filteredMarks = TRADEMARK_RESULTS.filter((item) => {
    const matchesSearch =
      item.mark.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.owner.toLowerCase().includes(searchTerm.toLowerCase())
    const classKey = selectedClass.split(' ')[0] + ' ' + (selectedClass.split(' ')[1] || '')
    const matchesClass =
      selectedClass === 'All Classes' ||
      item.classNo.toLowerCase().includes(classKey.trim().toLowerCase())
    return matchesSearch && matchesClass
  })

  return (
    <DashboardLayout activePath="/trademark">
      <div className="content-shell">
        <section className="query-shell" style={{ width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
          <div className="query-header-row">
            <span className="query-tag">TRADEMARK &amp; TKDL REPOSITORY</span>
            <span className="query-tag tag-right">CGPDTM &amp; TKDL INDIA</span>
          </div>

          <h1>AYUSH Trademark Availability &amp; Prior Art Check</h1>
          <p className="subtext">
            Search trademarks in Class 3 (Cosmetics), Class 5 (Ayurvedic/Pharma), and Class 30 (Dietary), cross-referenced with TKDL prior-art risk alerts.
          </p>

          <div className="ask-form-controls" style={{ marginTop: '1.5rem', marginBottom: '1.5rem', gap: '0.75rem' }}>
            <input
              type="text"
              placeholder="Enter brand mark, herb, or keyword (e.g. Shakti, Turmeric, Neem)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
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
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              style={{
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: '1px solid var(--line)',
                background: 'var(--panel)',
                color: 'var(--heading)',
              }}
            >
              <option>All Classes</option>
              <option>Class 3 (Cosmetics)</option>
              <option>Class 5 (Medicines)</option>
              <option>Class 30 (Supplements)</option>
            </select>
          </div>

          {tkdlMatches.length > 0 && (
            <div style={{ marginBottom: '1.25rem', padding: '1rem', background: 'rgba(215, 111, 26, 0.1)', borderRadius: '8px', border: '1px solid #d76f1a' }}>
              <strong style={{ color: '#d76f1a' }}>⚠️ TKDL Prior-Art Advisory Alert:</strong>
              {tkdlMatches.map((m, idx) => (
                <div key={idx} style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text)' }}>
                  <strong>Keyword: {m.formulation_keyword}</strong> ({m.classification}) — {m.matched_note}
                </div>
              ))}
            </div>
          )}

          <div className="option-list" style={{ display: 'grid', gap: '1rem' }}>
            {filteredMarks.map((item) => (
              <div key={item.id} className="option-row" style={{ justifyContent: 'space-between', cursor: 'default' }}>
                <div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.25rem' }}>
                    <strong style={{ fontSize: '1.1rem', color: 'var(--heading)' }}>{item.mark}</strong>
                    <span className="mini-tag">{item.classNo}</span>
                  </div>
                  <small style={{ color: 'var(--muted)' }}>Owner: {item.owner} | Journal No: {item.journalNo}</small>
                </div>
                <span
                  className="result-badge"
                  style={{
                    background: item.status === 'Registered' ? 'rgba(60, 157, 76, 0.15)' : 'rgba(238, 141, 57, 0.15)',
                    color: item.status === 'Registered' ? '#2e7d32' : '#d76f1a',
                  }}
                >
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}

export default TrademarkSearch
