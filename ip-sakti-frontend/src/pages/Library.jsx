import { useState, useEffect } from 'react'
import { useAppContext } from '../context/AppContext'
import { apiRequest } from '../services/api'
import DashboardLayout from '../components/layout/DashboardLayout'
import Reveal from '../components/common/Reveal'

const LIBRARY_ARTICLES = [
  {
    id: 1,
    category: 'Patents Act Section 3(p)',
    title: 'Traditional Knowledge & Non-Patentability Guidelines',
    summary: 'Comprehensive legal analysis of Section 3(p) restricting patents on traditional knowledge aggregations without proven synergistic efficacy.',
    date: 'Updated Aug 2026',
    tag: 'Patent Law',
    statute: 'Indian Patents Act, 1970 & 2024 Rules',
  },
  {
    id: 2,
    category: 'Biodiversity Act (NBA)',
    title: 'Access & Benefit Sharing (ABS) Protocols for Bio-Resources',
    summary: 'Step-by-step compliance guide for obtaining Form III approval from National Biodiversity Authority before filing IPR.',
    date: 'Updated Jul 2026',
    tag: 'Regulatory',
    statute: 'Biological Diversity (Amendment) Act, 2023 & 2024 Rules',
  },
  {
    id: 3,
    category: 'International Treaties',
    title: 'WIPO Treaty on Genetic Resources & Associated Traditional Knowledge',
    summary: 'Global mandatory disclosure requirements for patent applications based on genetic resources and traditional knowledge (Diplomatic Conference 2024).',
    date: 'Adopted May 2024',
    tag: 'International',
    statute: 'WIPO GRATK Treaty, Nagoya Protocol, CBD',
  },
  {
    id: 4,
    category: 'Geographical Indications',
    title: 'GI Registration of Heritage AYUSH Medicinal Plants',
    summary: 'Framework for agricultural and natural product GI registration including traditional cultivation regions.',
    date: 'Updated Jun 2026',
    tag: 'GI Guidelines',
    statute: 'Geographical Indications of Goods Act, 1999',
  },
  {
    id: 5,
    category: 'Drugs & Cosmetics Act',
    title: 'ASU (Ayurveda, Siddha, Unani) Drug Licensing Standards',
    summary: 'Rule 158-B licensing requirements, proof of safety, and classical text citation standards for patenting novel formulations.',
    date: 'Updated May 2026',
    tag: 'Drug Standards',
    statute: 'Drugs & Cosmetics Act 1940, First Schedule Texts',
  },
  {
    id: 6,
    category: 'Nutraceuticals & Food',
    title: 'FSSAI Ayurveda-Aahar Regulations and Labelling Standards',
    summary: 'Regulatory boundaries separating therapeutic ASU drugs from dietary health supplements and permitted botanicals.',
    date: 'Gazette 2022',
    tag: 'Regulatory',
    statute: 'Food Safety and Standards (Ayurveda Aahar) Regulations, 2022',
  },
]

function Library() {
  const { jurisdiction } = useAppContext()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTag, setSelectedTag] = useState('All')
  const [corpusMeta, setCorpusMeta] = useState(null)

  useEffect(() => {
    async function fetchCorpusInfo() {
      try {
        const data = await apiRequest('/corpus/version')
        if (data?.corpus_version) {
          setCorpusMeta(data)
        }
      } catch (_) {}
    }
    fetchCorpusInfo()
  }, [])

  const filteredArticles = LIBRARY_ARTICLES.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.statute.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTag = selectedTag === 'All' || item.tag === selectedTag
    return matchesSearch && matchesTag
  })

  return (
    <DashboardLayout activePath="/library">
      <div className="content-shell">
        <div className="dashboard-page-header">
          <div className="page-header-tags">
            <span className="page-category-badge">KNOWLEDGE BASE &amp; STATUTORY REPOSITORY</span>
            <span className="page-status-badge">
              {corpusMeta ? `DOCUMENTS V${corpusMeta.corpus_version}` : 'AYUSH LEGAL CORPUS'}
            </span>
          </div>
          <h1>AYUSH Legal &amp; IPR Document Library</h1>
          <p className="page-header-sub">
            Verified statutory documents, acts, rules, gazettes, and international treaties indexed in the IP-SAKTI intelligence corpus.
          </p>
        </div>

        {corpusMeta?.latest_amendments_indexed && (
          <Reveal className="amendments-banner">
            <div className="amendments-header">
              <span className="banner-icon">📜</span>
              <strong>Recent statutory amendments indexed in this corpus:</strong>
            </div>
            <div className="amendments-chips">
              {corpusMeta.latest_amendments_indexed.map((amd, i) => (
                <span key={i} className="amendment-chip">
                  ✓ {amd}
                </span>
              ))}
            </div>
          </Reveal>
        )}

        <div className="search-filter-row">
          <div className="search-input-wrap">
            <span className="search-icon">⌕</span>
            <input
              type="text"
              placeholder="Search legal provisions, herbs, acts, or guidelines (e.g. Section 3(p), WIPO, FSSAI)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="styled-search-input"
            />
          </div>
          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
            className="styled-filter-select"
          >
            <option value="All">All Regimes</option>
            <option value="Patent Law">Patent Law</option>
            <option value="Regulatory">Regulatory &amp; ABS</option>
            <option value="International">International</option>
            <option value="GI Guidelines">GI Guidelines</option>
            <option value="Drug Standards">Drug Standards</option>
          </select>
        </div>

        <div className="articles-grid">
          {filteredArticles.map((item, idx) => (
            <Reveal key={item.id} delay={idx * 50} className="article-card">
              <div className="article-card-top">
                <div className="article-title-wrap">
                  <h3>{item.title}</h3>
                  <span className="article-regime-tag">{item.tag}</span>
                </div>
                <span className="article-date">{item.date}</span>
              </div>
              <p className="article-summary">{item.summary}</p>
              <div className="article-footer">
                <span className="statute-label">Statutory Reference:</span>
                <span className="statute-value">{item.statute}</span>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </DashboardLayout>
  )
}

export default Library
