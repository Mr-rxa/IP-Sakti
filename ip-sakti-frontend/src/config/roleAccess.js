const COMMON_ITEMS = [
  { label: 'Dashboard', to: '/' },
  { label: 'Documents', to: '/library' },
  { label: 'My Results', to: '/result' },
]

const ROLE_ITEMS = {
  'AYUSH Practitioner': [
    { label: 'Ask IP Question', to: '/chat' },
    { label: 'Product Type', to: '/drug-classification' },
    { label: 'Plant Use Help', to: '/abs-compliance' },
  ],
  'Legal Researcher': [
    { label: 'Ask IP Question', to: '/chat' },
    { label: 'Trademark Search', to: '/trademark' },
    { label: 'GI Registration', to: '/gi-registration' },
  ],
  'IP Consultant': [
    { label: 'Ask IP Question', to: '/chat' },
    { label: 'Trademark Search', to: '/trademark' },
    { label: 'GI Registration', to: '/gi-registration' },
    { label: 'Plant Use Help', to: '/abs-compliance' },
  ],
  'Academic Researcher': [
    { label: 'Ask IP Question', to: '/chat' },
    { label: 'Documents', to: '/library' },
    { label: 'Product Type', to: '/drug-classification' },
  ],
  'MSME / Startup Founder': [
    { label: 'Ask IP Question', to: '/chat' },
    { label: 'Product Type', to: '/drug-classification' },
    { label: 'Plant Use Help', to: '/abs-compliance' },
    { label: 'Trademark Search', to: '/trademark' },
  ],
}

export function getRoleNavigation(role) {
  const roleItems = ROLE_ITEMS[role] || ROLE_ITEMS['AYUSH Practitioner']
  const items = [...COMMON_ITEMS]
  roleItems.forEach((item) => {
    if (!items.some((existing) => existing.to === item.to)) items.push(item)
  })
  return items
}

export function getRoleTools(role) {
  return ROLE_ITEMS[role] || ROLE_ITEMS['AYUSH Practitioner']
}
