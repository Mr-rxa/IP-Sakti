import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import { getABSChecklist } from '../services/classificationService'
import DashboardLayout from '../components/layout/DashboardLayout'

const FALLBACK_ABS_RULES = {
  'Classical/Generic Medicine': [
    'Verify if raw herbs or biological resources are sourced from local cultivators or forest areas within India.',
    'Indian entities utilizing classical biological resources for commercial utilization must give prior intimation to the State Biodiversity Board (SBB) under Section 7 of Biological Diversity Act (BDA), 2002.',
    'Check exemption eligibility: Local people and communities, including vaidyas and hakims, practicing indigenous medicine are exempted from intimation/fee under BDA 2023 Amendment.',
    'Ensure no exclusive patent claim is filed over the classical formulation to avoid Section 3(p) infringement and NBA non-compliance.',
  ],
  'Patent-or-Proprietary Medicine': [
    'Mandatory determination: If formulation utilizes biological resources occurring in India, prior approval from National Biodiversity Authority (NBA) is required under Section 6 of BDA 2002 before applying for any IPR / patent.',
    'Verify if any foreign collaborator, non-resident Indian, or foreign entity is part of the applicant entity (Section 3 of BDA requirement).',
    'Submit Form III to NBA for obtaining approval before grant of patent in India or overseas.',
    'Execute Benefit Sharing Agreement with NBA/SBB based on percentage of annual gross ex-factory sale per BD Rules 2024.',
  ],
  'New/Non-classical Drug': [
    'Determine source location of all biological material accessed within Indian territory.',
    'File Form I / Form III with the National Biodiversity Authority (NBA) for access and IPR protection respectively.',
    'Check compliance with Prior Informed Consent (PIC) and Mutually Agreed Terms (MAT) if biological resource was accessed from tribal/indigenous areas.',
    'Ensure clinical trials and new drug approval under CDSCO / Drugs & Cosmetics Rules align with biological source disclosures.',
    'Calculate Fair and Equitable Benefit Sharing (FEBS) commitments under Biological Diversity (Amendment) Act 2023.',
  ],
  'Phytopharmaceutical': [
    'Identify exact botanical taxon, geographic origin, and parts of the biological resources used in extraction.',
    'Apply for NBA Section 6 approval prior to filing patents on purified fractions or extraction processes.',
    'Verify compliance with State Biodiversity Board (SBB) intimation rules for commercial raw material procurement.',
    'Ensure full provenance traceability of botanical raw materials in alignment with WHO/AYUSH Good Agricultural and Collection Practices (GACP).',
    'Confirm international ABS compliance under Nagoya Protocol / CBD if commercialized in foreign jurisdictions.',
  ],
  'Ayurveda-Aahar/Nutraceutical': [
    'Confirm whether the product is categorized under FSSAI (Ayurveda Aahar) Regulations, 2022.',
    'Commercial manufacturing using Indian biological resources triggers SBB intimation and benefit-sharing under BDA 2002 / 2023 Rules.',
    'Maintain complete batch traceability of all agro-sourced and wild-collected herbs.',
    'Verify if trademark registration conflicts with registered Geographical Indications (GIs) of specific herbal regions.',
  ],
  'Cosmetic': [
    'Check if herbal extracts are sourced directly from wild or cultivated Indian biological resources.',
    'Commercial entities utilizing bio-resources for cosmetic formulations are subject to SBB access notification and benefit sharing.',
    'Verify adherence to Schedule S / Cosmetics Rules 2020 and biological material origin disclosure.',
    'Verify that cosmetic marketing claims do not violate Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954.',
  ],
}

function ABSCompliance() {
  const navigate = useNavigate()
  const { addHistoryEntry } = useAppContext()

  const [classification, setClassification] = useState('Classical/Generic Medicine')
  const [entityType, setEntityType] = useState('Indian Company / Start-up')
  const [purpose, setPurpose] = useState('Commercial Utilization (Manufacturing Formulation)')
  const [resourceSource, setResourceSource] = useState('Directly from Farmers / Local Community')
  const [checklist, setChecklist] = useState([])
  const [analyzed, setAnalyzed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [serviceError, setServiceError] = useState('')

  const handleAnalyze = async (e) => {
    e.preventDefault()
    setLoading(true)
    setServiceError('')
    try {
      const data = await getABSChecklist(classification)
      if (data?.checklist && data.checklist.length > 0) {
        setChecklist(data.checklist)
      } else {
        setChecklist(FALLBACK_ABS_RULES[classification] || FALLBACK_ABS_RULES['Classical/Generic Medicine'])
      }
      setAnalyzed(true)
    } catch (err) {
      console.warn('API lookup fallback triggered:', err)
      setChecklist(FALLBACK_ABS_RULES[classification] || FALLBACK_ABS_RULES['Classical/Generic Medicine'])
      setAnalyzed(true)
    } finally {
      setLoading(false)
    }
  }

  const getRequiredForm = () => {
    if (entityType.includes('Foreign') || entityType.includes('Joint Venture') || entityType.includes('NRI')) {
      return 'Form I (Prior Approval from National Biodiversity Authority under Section 3)'
    }
    if (purpose.includes('Patent') || purpose.includes('Section 6')) {
      return 'Form III (Application for Approval for IPR / Patent Grant under Section 6 of BD Act)'
    }
    if (purpose.includes('Transfer') || purpose.includes('Section 5')) {
      return 'Form IV (Application for Third Party Transfer under Section 5 of BD Act)'
    }
    if (purpose.includes('Export')) {
      return 'Form I / Form II (Approval for Access and Export of Biological Resources)'
    }
    return 'State Biodiversity Board (SBB) Prior Intimation under Section 7 (Form 1 of SBB)'
  }

  const getBenefitSharingScale = () => {
    if (resourceSource.includes('Mandi') || resourceSource.includes('Trader')) {
      return 'Exempt from Benefit Sharing under Section 40 (purchased as Normally Traded Commodity / NTAC notified list).'
    }
    if (entityType.includes('Vaidya') || entityType.includes('Individual')) {
      return 'Exempt from ABS intimation and fee under Section 7 proviso (local vaidyas and practitioners practicing traditional ASU medicine).'
    }
    return '0.1% to 0.5% of annual gross ex-factory sale value (payable to SBB / NBA as per BD Rules 2024).'
  }

  const handleSaveABSResult = () => {
    addHistoryEntry({
      title: `Plant use check: ${classification}`,
      tag: entityType.includes('Foreign') ? 'Form I Required' : purpose.includes('Patent') ? 'Form III Required' : 'SBB Intimation',
      summary: `Entity: ${entityType}. Purpose: ${purpose}`,
      detail: `Requirement: ${getRequiredForm()}. Benefit Sharing: ${getBenefitSharingScale()}`,
    })
    navigate('/result')
  }

  return (
    <DashboardLayout activePath="/abs-compliance">
      <div className="content-shell">
        <section className="query-shell" style={{ width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
          <div className="query-header-row">
            <span className="query-tag" style={{ background: '#d76f1a', color: '#fff' }}>
              PLANT USE AND BENEFIT SHARING
            </span>
            <span className="query-tag tag-right">STEP-BY-STEP CHECK</span>
          </div>

          <h1>Using Plants or Traditional Knowledge</h1>
          <p className="subtext">
            Answer a few questions to understand what permissions and benefit-sharing steps may apply to your product.
          </p>

          <form
            onSubmit={handleAnalyze}
            style={{
              display: 'grid',
              gap: '1.25rem',
              marginTop: '1.5rem',
              background: 'var(--panel)',
              padding: '1.5rem',
              borderRadius: '12px',
              border: '1px solid var(--line)',
            }}
          >
            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--heading)' }}>
                What type of product is it?
              </label>
              <select
                value={classification}
                onChange={(e) => setClassification(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--line)',
                  background: 'var(--surface)',
                  color: 'var(--heading)',
                }}
              >
                <option>Classical/Generic Medicine</option>
                <option>Patent-or-Proprietary Medicine</option>
                <option>New/Non-classical Drug</option>
                <option>Phytopharmaceutical</option>
                <option>Ayurveda-Aahar/Nutraceutical</option>
                <option>Cosmetic</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--heading)' }}>
                Who is making or selling it?
              </label>
              <select
                value={entityType}
                onChange={(e) => setEntityType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--line)',
                  background: 'var(--surface)',
                  color: 'var(--heading)',
                }}
              >
                <option>Indian Company / Start-up</option>
                <option>Foreign Company / Non-Resident Indian (NRI)</option>
                <option>Joint Venture with Foreign Participation</option>
                <option>Individual AYUSH Practitioner / Vaidya</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--heading)' }}>
                What will you use it for?
              </label>
              <select
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--line)',
                  background: 'var(--surface)',
                  color: 'var(--heading)',
                }}
              >
                <option>Commercial Utilization (Manufacturing Formulation)</option>
                <option>Filing Patent Application (Section 6 Compliance)</option>
                <option>Transfer of Research Results (Section 5)</option>
                <option>Export of Bio-resource for Clinical Trials</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--heading)' }}>
                Bio-resource Sourcing Mode
              </label>
              <select
                value={resourceSource}
                onChange={(e) => setResourceSource(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  border: '1px solid var(--line)',
                  background: 'var(--surface)',
                  color: 'var(--heading)',
                }}
              >
                <option>Directly from Farmers / Local Community</option>
                <option>Purchased from Registered Mandi / Trader (Exempt under Sec 40 if codified)</option>
                <option>Cultivated in Own Herbal Garden</option>
              </select>
            </div>

            <button type="submit" className="primary-btn" disabled={loading} style={{ justifySelf: 'flex-start', marginTop: '0.5rem' }}>
              {loading ? 'Checking trusted documents...' : 'Show me the steps →'}
            </button>
          </form>

          {serviceError && (
            <div className="query-error" role="alert" style={{ marginTop: '1.25rem' }}>
              <strong>Plant-use check unavailable</strong>
              <span>{serviceError}</span>
            </div>
          )}

          {analyzed && checklist.length > 0 && (
            <div className="assessment-box" style={{ marginTop: '1.5rem' }}>
              <div className="assessment-icon">📋</div>
              <div>
                <h3>Steps you may need to follow</h3>
                <p>
                  <strong>Form Required:</strong> {getRequiredForm()}
                </p>
                <p>
                  <strong>Benefit Sharing Scale:</strong> {getBenefitSharingScale()}
                </p>

                <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--line)' }}>
                  <strong>Mandatory Compliance Checklist for {classification}:</strong>
                  <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.25rem' }}>
                    {checklist.map((item, idx) => (
                      <li key={idx} style={{ marginBottom: '0.35rem' }}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          <div className="action-row" style={{ marginTop: '2rem' }}>
            <button
              className="primary-btn"
              type="button"
              onClick={handleSaveABSResult}
              disabled={!analyzed || checklist.length === 0}
            >
              Save to Assessment History →
            </button>
            <button className="secondary-btn light-btn" type="button" onClick={() => navigate('/chat')}>
              Ask AI about NBA Approvals
            </button>
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}

export default ABSCompliance
