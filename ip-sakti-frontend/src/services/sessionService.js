import { apiRequest } from './api'

export async function createSession() {
  try {
    const data = await apiRequest('/session', {
      method: 'POST',
    })
    if (data?.session_id) {
      sessionStorage.setItem('ip_shakti_session_id', data.session_id)
    }
    return data
  } catch (e) {
    console.warn('Failed to create session on backend:', e)
    const fallbackId = `sess_${Date.now()}`
    sessionStorage.setItem('ip_shakti_session_id', fallbackId)
    return { session_id: fallbackId }
  }
}

export async function setSessionJurisdiction(sessionId, jurisdiction) {
  try {
    return await apiRequest(`/session/${sessionId}/jurisdiction`, {
      method: 'PATCH',
      body: JSON.stringify({ jurisdiction }),
    })
  } catch (e) {
    console.warn('Failed to update jurisdiction on backend:', e)
    return { session_id: sessionId, jurisdiction }
  }
}

export async function escalateToFacilitator(sessionId, queryId, userContact = null) {
  return apiRequest('/escalate', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      query_id: queryId,
      user_contact_optional: userContact,
    }),
  })
}

export function getActiveSessionId() {
  return sessionStorage.getItem('ip_shakti_session_id')
}
