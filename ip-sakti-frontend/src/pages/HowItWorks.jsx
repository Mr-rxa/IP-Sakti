import { useNavigate } from 'react-router-dom'
import Reveal from '../components/common/Reveal'
import { useAppContext } from '../context/AppContext'
import DashboardLayout from '../components/layout/DashboardLayout'

const steps = [
  {
    number: '01',
    title: 'Choose the legal scope',
    text: 'Switch between India and International before asking a question. This keeps national statutes and global treaties visibly separate.',
    icon: '◎',
  },
  {
    number: '02',
    title: 'Describe your product',
    text: 'Use Product Type Classification to identify whether your formulation is classical, proprietary, new, phytopharmaceutical, food or cosmetic.',
    icon: '◇',
  },
  {
    number: '03',
    title: 'Ask in plain language',
    text: 'Ask about patents, trademarks, GI, biodiversity, traditional knowledge or regulatory duties. The assistant routes the question to the relevant regimes.',
    icon: '✦',
  },
  {
    number: '04',
    title: 'Review the evidence',
    text: 'Read the answer with its source citations, confidence level and legal-information disclaimer. Low-evidence questions are designed to abstain.',
    icon: '▤',
  },
  {
    number: '05',
    title: 'Keep a verifiable record',
    text: 'Your signed-in workspace stores your questions and review requests in your account activity so decisions do not disappear between sessions.',
    icon: '⌁',
  },
]

const tools = [
  ['Ask IP Question', 'Use this for patentability, trademarks, GI, copyright, designs, plant varieties and traditional-knowledge questions.', '/chat'],
  ['Product Type', 'Use this before making an IP decision when the regulatory category of your formulation is unclear.', '/drug-classification'],
  ['Plant Use Help', 'Use this to understand access, benefit-sharing and biodiversity considerations for biological resources.', '/abs-compliance'],
  ['Documents', 'Use this to inspect the corpus of laws, rules, treaties and references used by the assistant.', '/library'],
  ['My Results', 'Use this to revisit saved assessments and account activity, including queued human review requests.', '/result'],
]

function HowItWorks() {
  const navigate = useNavigate()
  const { jurisdiction } = useAppContext()

  return (
    <DashboardLayout activePath="/how-it-works">
      <div className="content-shell">
        <main className="guide-content" style={{ padding: 0 }}>
          <Reveal className="guide-hero">
            <span className="dashboard-kicker">A practical guide to IP-SHAKTI</span>
            <h1>From a question to a defensible next step.</h1>
            <p>IP-SHAKTI helps AYUSH practitioners, researchers, consultants and founders orient themselves across overlapping IP, biodiversity and product rules.</p>
            <div className="guide-hero-actions">
              <button type="button" className="primary-btn" onClick={() => navigate('/chat')}>Ask a question</button>
              <button type="button" className="secondary-btn" onClick={() => navigate('/drug-classification')}>Classify a product</button>
            </div>
          </Reveal>

          <section className="guide-section">
            <Reveal>
              <div className="section-eyebrow">The workflow</div>
              <h2>Five decisions, one clear trail.</h2>
            </Reveal>
            <div className="workflow-grid">
              {steps.map((step, index) => (
                <Reveal key={step.number} delay={index * 80} className="workflow-card">
                  <div className="workflow-card-top"><span>{step.number}</span><strong>{step.icon}</strong></div>
                  <h3>{step.title}</h3>
                  <p>{step.text}</p>
                </Reveal>
              ))}
            </div>
          </section>

          <section className="guide-section tools-section">
            <Reveal>
              <div className="section-eyebrow">What each option does</div>
              <h2>Every tool has a job.</h2>
              <p className="section-intro">Use the option that matches the decision in front of you. You do not need to understand every legal regime before you begin.</p>
            </Reveal>
            <div className="tool-explanation-grid">
              {tools.map(([title, text, path], index) => (
                <Reveal key={title} delay={index * 70} className="tool-explanation">
                  <div><span className="tool-explanation-index">0{index + 1}</span><h3>{title}</h3></div>
                  <p>{text}</p>
                  <button type="button" className="text-link" onClick={() => navigate(path)}>Open {title} <span aria-hidden="true">→</span></button>
                </Reveal>
              ))}
            </div>
          </section>

          <Reveal className="trust-panel">
            <div>
              <span className="section-eyebrow">The trust boundary</span>
              <h2>Information, not legal advice.</h2>
              <p>Answers are grounded in the available corpus and should be verified against the official source or a qualified professional before filing, commercialising or disclosing sensitive information.</p>
            </div>
            <div className="trust-facts">
              <span><strong>{jurisdiction}</strong> scope selected</span>
              <span><strong>Source</strong> citations shown</span>
              <span><strong>Low confidence</strong> can abstain</span>
            </div>
          </Reveal>
        </main>
      </div>
    </DashboardLayout>
  )
}

export default HowItWorks
