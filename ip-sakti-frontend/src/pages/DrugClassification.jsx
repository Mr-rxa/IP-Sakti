import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import { startClassification, answerClassification } from '../services/classificationService'
import DashboardLayout from '../components/layout/DashboardLayout'

const REGULATORY_REQUIREMENTS = {
  'Classical/Generic Medicine': [
    'Listed in First Schedule of Drugs & Cosmetics Act 1940 (Ayurveda authoritative texts)',
    'Manufacturing License under Form 25-D from State Licensing Authority (SLA)',
    'Traditional Knowledge bar under Section 3(p) of Patents Act 1970 — subject to TKDL citations',
    'Mandatory compliance with Pharmacopoeial standards (Ayurvedic Pharmacopoeia of India - API)',
  ],
  'Patent-or-Proprietary Medicine': [
    'Proprietary ASU formulation under Section 3(h) of Drugs and Cosmetics Act',
    'Evidence of safety and effectiveness as per Rule 158-B',
    'Requires Form 25-D manufacturing license and approved pilot stability data',
    'Patentable only if substantial non-obvious synergistic efficacy is clinically demonstrated',
  ],
  'New/Non-classical Drug': [
    'Novel botanical or modified traditional formulation requiring formal clinical trials',
    'Approval from Central Drugs Standard Control Organisation (CDSCO)',
    'Strong patent potential under Indian Patents Act 1970 (Section 3(p) overcomes if synergism proven)',
    'Prior NBA approval required under Section 6 of Biological Diversity Act 2002 before filing',
  ],
  'Phytopharmaceutical': [
    'Purified and standardized fraction with defined phytochemical markers',
    'Classified under Rule 122E of Drugs and Cosmetics Rules (Schedule Y / New Drugs Rules 2019)',
    'Pre-clinical toxicity and Phase I-III clinical trial safety data required',
    'High patentability for novel extraction methods, standardized compositions, and therapeutic uses',
  ],
  'Ayurveda-Aahar/Nutraceutical': [
    'Governed under FSSAI (Ayurveda Aahar) Regulations, 2022',
    'No therapeutic disease-cure claims permitted on packaging or promotional materials',
    'Compliance with Recommended Dietary Allowance (RDA) limits for botanical ingredients',
    'Protected primarily via Trademark and Industrial Design regimes rather than drug patents',
  ],
  'Cosmetic': [
    'Topical herbal preparations for beautifying, cleansing, or skin conditioning',
    'Licensed under Part XIII of Drugs and Cosmetics Rules (Form 32)',
    'BIS Standard compliance (IS:7884) for heavy metals and microbiological safety',
    'Protected via Trademarks, Trade Dress, and Industrial Designs',
  ],
}

function DrugClassification() {
  const navigate = useNavigate()
  const { addHistoryEntry, jurisdiction, sessionId } = useAppContext()

  const [currentStep, setCurrentStep] = useState(0)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [selectedOption, setSelectedOption] = useState('')
  const [loading, setLoading] = useState(true)
  const [finalResult, setFinalResult] = useState(null)
  const [serviceError, setServiceError] = useState('')

  useEffect(() => {
    async function initFlow() {
      setLoading(true)
      try {
        const firstQ = await startClassification(sessionId)
        if (firstQ?.question_id) {
          setCurrentQuestion(firstQ)
          setSelectedOption(firstQ.options?.[0] || 'Yes')
        }
      } catch (e) {
        console.error('Classification service unavailable:', e)
        setServiceError('Classification service is unavailable. No legal classification was produced.')
      } finally {
        setLoading(false)
      }
    }
    initFlow()
  }, [sessionId])

  const handleNext = async () => {
    if (!currentQuestion) return

    setLoading(true)
    try {
      const res = await answerClassification(
        sessionId,
        currentQuestion.question_id,
        selectedOption
      )

      if (res?.classification_result) {
        setFinalResult(res)
      } else if (res?.next_question_id) {
        setCurrentQuestion({
          question_id: res.next_question_id,
          question_text: res.question_text,
          options: res.options || ['Yes', 'No', 'Not sure'],
        })
        setSelectedOption(res.options?.[0] || 'Yes')
        setCurrentStep((prev) => prev + 1)
      } else {
        setServiceError('Received unexpected response from classification service.')
      }
    } catch (e) {
      console.error('Classification answer error:', e)
      setServiceError('Classification service is unavailable. No legal classification was produced.')
      setFinalResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveResult = () => {
    if (!finalResult) return
    addHistoryEntry({
      title: `${finalResult.classification_result} Assessment`,
      tag: `Regimes: ${(finalResult.relevant_regimes || ['Patents', 'ABS']).join(', ')}`,
      summary: finalResult.explanation || 'Regulatory classification finalized.',
      detail: `Applicable Regimes: ${(finalResult.relevant_regimes || []).join(', ')}`,
    })
    navigate('/abs-compliance')
  }

  const handleRestart = async () => {
    setFinalResult(null)
    setCurrentStep(0)
    setServiceError('')
    setLoading(true)
    try {
      const firstQ = await startClassification(sessionId)
      if (firstQ) {
        setCurrentQuestion(firstQ)
        setSelectedOption(firstQ?.options?.[0] || 'Yes')
      }
    } catch (e) {
      console.error('Classification restart error:', e)
      setServiceError('Could not restart classification service. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const requirements = finalResult
    ? REGULATORY_REQUIREMENTS[finalResult.classification_result] || REGULATORY_REQUIREMENTS['Classical/Generic Medicine']
    : []

  return (
    <DashboardLayout activePath="/drug-classification">
      <div className="content-shell" style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div className="wizard-card">
          <div className="wizard-tracker">
            {['Authentic Source', 'Product Nature', 'Extract/Botanical', 'Novelty & Process'].map((step, index) => (
              <div key={step} className={`tracker-step ${index <= currentStep ? 'active' : ''}`}>
                <span>{index + 1}</span>
                <label>{step}</label>
              </div>
            ))}
          </div>

          {!finalResult ? (
          <>
            <h2>Product Type Classification</h2>
            <p className="subtext">
              Answer a few simple questions. We will help you understand whether your product is a medicine, food, plant extract or cosmetic.
            </p>

            {loading ? (
              <div style={{ padding: '2rem', textAlign: 'center' }}>Checking trusted documents...</div>
            ) : serviceError ? (
              <div role="alert" style={{ padding: '2rem', textAlign: 'center' }}>{serviceError}</div>
            ) : currentQuestion ? (
              <div style={{ marginTop: '1.25rem' }}>
                <h3 style={{ fontSize: '1.15rem', color: 'var(--heading)', marginBottom: '1rem' }}>
                  {currentQuestion.question_text}
                </h3>

                <div className="option-list">
                  {currentQuestion.options?.map((opt) => (
                    <button
                      type="button"
                      key={opt}
                      className={`option-row ${selectedOption === opt ? 'selected' : ''}`}
                      onClick={() => setSelectedOption(opt)}
                    >
                      <span className="radio-dot" aria-hidden="true" />
                      <div className="option-text">
                        <strong>{opt}</strong>
                      </div>
                    </button>
                  ))}
                </div>

                <div className="bottom-actions" style={{ marginTop: '2rem' }}>
                  <button type="button" className="secondary-btn ghost-btn" onClick={() => navigate('/')}>
                    Cancel
                  </button>
                  <button type="button" className="primary-btn" onClick={handleNext}>
                    Next →
                  </button>
                </div>
              </div>
            ) : null}
          </>
        ) : (
          <div style={{ marginTop: '1rem' }}>
            <div style={{ display: 'inline-block', padding: '4px 12px', background: '#3c9d4c', color: '#fff', borderRadius: '14px', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.75rem' }}>
              PRODUCT TYPE FOUND
            </div>
            <h2>{finalResult.classification_result}</h2>
            <p className="subtext" style={{ fontSize: '1rem', color: 'var(--text)' }}>
              {finalResult.explanation}
            </p>

            <div style={{ marginTop: '1.5rem', background: 'var(--panel-strong)', padding: '1.25rem', borderRadius: '8px', border: '1px solid var(--line)' }}>
              <h4 style={{ margin: '0 0 0.75rem 0', color: 'var(--heading)' }}>
                What you may need to check:
              </h4>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text)', fontSize: '0.92rem' }}>
                {requirements.map((req, i) => (
                  <li key={i} style={{ marginBottom: '0.4rem' }}>{req}</li>
                ))}
              </ul>
            </div>

            <div style={{ marginTop: '1.25rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <strong>Related topics:</strong>
              {finalResult.relevant_regimes?.map((r) => (
                <span key={r} className="mini-tag" style={{ background: 'var(--primary)', color: '#fff' }}>{r}</span>
              ))}
            </div>

            <div className="bottom-actions" style={{ marginTop: '2rem' }}>
              <button type="button" className="secondary-btn" onClick={handleRestart}>
                ↻ Start Over
              </button>
              <button type="button" className="primary-btn" onClick={handleSaveResult}>
                Check plant-use steps &rarr;
              </button>
            </div>
          </div>
        )}
        </div>
      </div>
    </DashboardLayout>
  )
}

export default DrugClassification
