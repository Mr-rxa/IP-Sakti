import ChatMessage from './ChatMessage'
import TypingIndicator from './TypingIndicator'

function ChatWindow({ messages = [], isTyping = false }) {
  return (
    <div className="chat-window card">
      {messages.length === 0 ? (
        <div className="empty-state">No messages yet.</div>
      ) : (
        messages.map((msg, index) => (
          <ChatMessage key={`${msg.sender}-${index}`} sender={msg.sender} text={msg.text} />
        ))
      )}
      {isTyping && <TypingIndicator />}
    </div>
  )
}

export default ChatWindow
