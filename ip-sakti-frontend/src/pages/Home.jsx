import { useNavigate } from 'react-router-dom'
import { useAppContext } from '../context/AppContext'
import { getRoleTools } from '../config/roleAccess'
import Reveal from '../components/common/Reveal'
import DashboardLayout from '../components/layout/DashboardLayout'

function Home() {
  const navigate = useNavigate()
  const { userRole, jurisdiction, historyEntries, currentUser } = useAppContext()
  const roleTools = getRoleTools(userRole)

  return (
    <DashboardLayout activePath="/">
      <Reveal className="reference-hero">
        <div>
          <span className="dashboard-kicker">{jurisdiction} knowledge workspace</span>
          <h1>Namaste, {currentUser?.full_name?.split(' ')[0] || 'there'} <span aria-hidden="true">✦</span></h1>
          <p>{jurisdiction === 'India' ? 'How can we protect your Ayurvedic innovation today?' : 'How can we help you take Ayurvedic innovation to the world?'}</p>
        </div>
        <div className="reference-hero-quote">“Knowledge from India.<br />Wellness for the world.”</div>
      </Reveal>

      <section className="reference-actions">
        <Reveal><div className="reference-section-heading"><div><span className="section-eyebrow">Your workspace</span><h2>What would you like to do?</h2></div><span className="role-badge">{userRole}</span></div></Reveal>
        <div className="reference-action-grid">
          {roleTools.map((tool, index) => (
            <Reveal key={tool.to} delay={index * 70}>
              <button type="button" className={`reference-action-card action-tone-${index % 5}`} onClick={() => navigate(tool.to)}>
                <span className="reference-action-icon">{['✦', '◇', '♧', '▤', '◌'][index % 5]}</span>
                <strong>{tool.label}</strong><small>{tool.to === '/chat' ? 'Get accurate, cited answers' : tool.to === '/drug-classification' ? 'Know the regulatory path' : tool.to === '/abs-compliance' ? 'Check access and benefit sharing' : 'Explore trusted resources'}</small><span className="action-arrow">→</span>
              </button>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="dashboard-panels reference-panels">
        <Reveal className="dashboard-panel"><div className="dashboard-panel-heading"><div><span className="section-eyebrow">Your workspace</span><h2>Recent activity</h2></div><button type="button" className="panel-link" onClick={() => navigate('/result')}>View all</button></div>{historyEntries.length > 0 ? historyEntries.slice(0, 3).map((entry) => <div className="activity-row" key={entry.id}><span className="activity-dot" /><div><strong>{entry.title}</strong><small>{entry.date} · {entry.tag}</small></div></div>) : <p className="empty-panel">Your saved questions and review requests will appear here.</p>}</Reveal>
        <Reveal className="dashboard-panel" delay={100}><div className="dashboard-panel-heading"><div><span className="section-eyebrow">Shortcuts</span><h2>Quick links</h2></div><span className="panel-status">{jurisdiction}</span></div><div className="quick-link-list">{roleTools.slice(0, 4).map((tool) => <button type="button" key={tool.to} onClick={() => navigate(tool.to)}>{tool.label}<span aria-hidden="true">→</span></button>)}</div></Reveal>
      </section>
    </DashboardLayout>
  )
}

export default Home
