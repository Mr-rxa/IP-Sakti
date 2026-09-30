import { useState } from 'react'

export function useClassification() {
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const classify = async (payload) => {
    setIsLoading(true)
    try {
      const response = {
        category: payload?.type || 'Trademark',
        confidence: 88,
      }
      setResult(response)
      return response
    } finally {
      setIsLoading(false)
    }
  }

  return { result, isLoading, classify }
}
