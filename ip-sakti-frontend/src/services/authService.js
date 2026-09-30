import { apiRequest } from './api'

export async function loginUser(email, password, role = 'AYUSH Practitioner') {
  const data = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password, role }),
  })
  if (data?.access_token) {
    localStorage.setItem('ip_shakti_token', data.access_token)
    localStorage.setItem('ip_shakti_user', JSON.stringify(data.user))
  }
  return data
}

export async function registerUser(email, password, role = 'AYUSH Practitioner', fullName = '') {
  const data = await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      role,
      full_name: fullName,
    }),
  })
  if (data?.access_token) {
    localStorage.setItem('ip_shakti_token', data.access_token)
    localStorage.setItem('ip_shakti_user', JSON.stringify(data.user))
  }
  return data
}

export async function getCurrentUser() {
  return apiRequest('/auth/me')
}

export async function getUserActivity() {
  return apiRequest('/auth/activity')
}

export function logoutUser() {
  localStorage.removeItem('ip_shakti_token')
  localStorage.removeItem('ip_shakti_user')
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('ip_shakti_user')
    return raw ? JSON.parse(raw) : null
  } catch (_) {
    return null
  }
}

export function getStoredToken() {
  return localStorage.getItem('ip_shakti_token')
}
