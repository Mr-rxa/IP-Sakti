function ChatMessage({ sender = 'assistant', text }) {
  return (
    <div className={`chat-message ${sender}`}>
      <div className="message-bubble">
        {text}
      </div>
    </div>
  )
}

export default ChatMessage
