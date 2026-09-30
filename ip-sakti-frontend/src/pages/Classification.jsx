import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import DashboardLayout from '../components/layout/DashboardLayout'

const defaultSteps = ['Origin', 'Formulation', 'Market Intent']

const classificationConfigs = {
  gi: {
    title: 'Geographical Indication (GI) Classification',
    subtext: 'Is your formulation or biological resource tied to a specific geographical origin in India?',
    options: [
      { title: 'Regional Cultivation / Heritage Crop', description: 'Grown exclusively in a specific agro-climatic zone (e.g., Kashmiri Saffron, Darjeeling Tea).' },
      { title: 'Traditional Knowledge Community Production', description: 'Produced by a specific community using century-old traditional processing methods.' },
      { title: 'Standard Commercial Cultivation', description: 'Grown across multiple regions with standard agricultural methods.' },
    ],
  },
  abs: {
    title: 'Biodesign & ABS (Access and Benefit Sharing) Compliance',
    subtext: 'Identify compliance requirements under the Biological Diversity Act, 2002.',
    options: [
      { title: 'Indian Biological Resource Export / Commercial Utilization', description: 'Requires NBA Form III prior approval and benefit-sharing agreement.' },
      { title: 'Collaborative Research (Indian & Foreign Entity)', description: 'Requires NBA Form IV clearance under Section 5 of BD Act.' },
      { title: 'Domestic Small-Scale AYUSH Practice', description: 'Exempt from commercial ABS under customary traditional use rules.' },
    ],
  },
  drug: {
    title: 'Intended Commercial Application & ASU Classification',
    subtext: 'How is the Ayurvedic, Siddha, or Unani product intended to be sold or marketed?',
    options: [
      {
        title: 'Medicine (Ayurvedic Drug)',
        description: 'Intended for internal or external use in the diagnosis, treatment, mitigation, or prevention of disease.',
      },
      {
        title: 'Nutraceutical / Dietary Supplement',
        description: 'Intended to supplement the diet, containing one or more dietary ingredients under FSSAI regulations.',
      },
      {
        title: 'Cosmetic (Sundarya Prasadhana)',
        description: 'Intended to be applied to the human body for cleansing, beautifying, promoting attractiveness, or altering appearance.',
      },
    ],
  },
}

function Classification() {
  const navigate = useNavigate()
  const location = useLocation()

  const queryParams = new URLSearchParams(location.search)
  const typeParam = queryParams.get('type') || 'drug'

  const config = classificationConfigs[typeParam] || classificationConfigs.drug
  const [currentStep] = useState(2)
  const [selected, setSelected] = useState(config.options[0].title)

  return (
    <DashboardLayout activePath="/drug-classification">
      <div className="content-shell" style={{ maxWidth: '900px', margin: '0 auto' }}>
        <div className="wizard-card">
          <div className="wizard-tracker">
            {defaultSteps.map((step, index) => (
              <div key={step} className={`tracker-step ${index < currentStep ? 'done' : index === currentStep ? 'active' : ''}`}>
                <span>{index < currentStep ? '✓' : index + 1}</span>
                <label>{step}</label>
              </div>
            ))}
          </div>

          <h2>{config.title}</h2>
          <p className="subtext">{config.subtext}</p>

          <div className="option-list">
            {config.options.map((option) => (
              <button
                type="button"
                key={option.title}
                className={`option-row ${selected === option.title ? 'selected' : ''}`}
                onClick={() => setSelected(option.title)}
              >
                <span className="radio-dot" aria-hidden="true" />
                <div className="option-text">
                  <strong>{option.title}</strong>
                  <small>{option.description}</small>
                </div>
              </button>
            ))}
          </div>

          <div className="bottom-actions">
            <button type="button" className="secondary-btn ghost-btn" onClick={() => navigate('/')}>
              Back
            </button>
            <button type="button" className="primary-btn" onClick={() => navigate('/result')}>
              Analyze Classification →
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default Classification
