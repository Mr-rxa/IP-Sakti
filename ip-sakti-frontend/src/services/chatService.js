import { apiRequest } from './api'

export async function sendChatMessage(queryText, options = {}) {
  const payload = {
    query_text: queryText,
    session_id: options.session_id || sessionStorage.getItem('ip_shakti_session_id') || null,
    jurisdiction: options.jurisdiction || 'India',
    classification_context: options.classification_context || null,
  }

  const response = await apiRequest('/query', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

  // Normalize response for frontend UI consumption
  const isAbstained = Boolean(response.abstained)
  let confidenceScore = 0
  let confidenceLabel = 'Low'

  if (!isAbstained) {
    confidenceScore = response.confidence_score !== undefined
      ? Math.round(response.confidence_score <= 1.0 ? response.confidence_score * 100 : response.confidence_score)
      : 85
    confidenceLabel = response.confidence_label || (confidenceScore >= 75 ? 'High' : confidenceScore >= 40 ? 'Moderate' : 'Low')
  }

  const formattedCitations = (response.citations || []).map((c) => {
    if (!c) return 'Statutory Source'
    if (typeof c === 'string') return c
    const title = c.source_title || 'Statutory Source'
    const section = c.section_or_article ? ` — ${c.section_or_article}` : ''
    return `${title}${section}`
  })

  return {
    queryId: response.query_id || `AYU-${Math.floor(1000 + Math.random() * 9000)}-${(options.jurisdiction || 'IND').toUpperCase().slice(0, 3)}`,
    summary: response.answer_text || response.summary || 'Assessment completed.',
    assessment: response.answer_text || response.assessment || '',
    confidence: confidenceScore,
    confidenceLabel: confidenceLabel,
    citations: formattedCitations,
    rawCitations: response.citations || [],
    abstained: isAbstained,
    escalationSuggested: Boolean(response.escalation_suggested),
    disclaimer: response.disclaimer || 'Information only - not legal advice',
  }
}
