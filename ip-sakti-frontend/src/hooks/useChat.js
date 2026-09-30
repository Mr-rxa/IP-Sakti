import { useState } from 'react'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return

    setMessages((prev) => [...prev, { sender: 'user', text: messageText }])
    setIsLoading(true)

    try {
      const response = { sender: 'assistant', text: 'Connected hook ready for backend integration.' }
      setMessages((prev) => [...prev, response])
    } finally {
      setIsLoading(false)
    }
  }

  return { messages, isLoading, sendMessage }
}
