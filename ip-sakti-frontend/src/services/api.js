const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const DEFAULT_TIMEOUT_MS = 120000

export async function apiRequest(endpoint, options = {}) {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, signal: externalSignal, ...requestOptions } = options
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  if (externalSignal) {
    if (externalSignal.aborted) controller.abort(externalSignal.reason)
    else externalSignal.addEventListener('abort', () => controller.abort(externalSignal.reason), { once: true })
  }

  try {
    const token = localStorage.getItem('ip_shakti_token')
    const authHeaders = token ? { Authorization: `Bearer ${token}` } : {}

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
        ...(requestOptions.headers || {}),
      },
      signal: controller.signal,
      ...requestOptions,
    })

    if (!response.ok) {
      let errorData = null
      try {
        errorData = await response.json()
      } catch (_) {}
      const errorMsg = errorData?.message || errorData?.detail || `Request failed: ${response.status}`
      const error = new Error(errorMsg)
      error.status = response.status
      error.data = errorData
      throw error
    }

    return await response.json()
  } catch (error) {
    if (error.name === 'AbortError') {
      const timeoutError = new Error(
        externalSignal?.aborted
          ? 'The request was cancelled.'
          : 'The answer is taking longer than expected. Please try again.'
      )
      timeoutError.name = 'TimeoutError'
      throw timeoutError
    }
    if (error.status === 401 || error.status === 400 || error.status === 404) {
      throw error
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}
