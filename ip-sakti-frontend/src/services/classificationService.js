import { apiRequest } from './api'

export async function startClassification(sessionId) {
  return apiRequest('/classification/start', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}

export async function answerClassification(sessionId, questionId, answer) {
  return apiRequest('/classification/answer', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      question_id: questionId,
      answer,
    }),
  })
}

export async function getABSChecklist(classification) {
  return apiRequest(`/abs/checklist?classification=${encodeURIComponent(classification)}`)
}

export async function classifyMatter(payload = {}) {
  return apiRequest('/classification/start', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
