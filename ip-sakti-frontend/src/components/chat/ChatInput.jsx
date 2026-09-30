function ChatInput({ value, onChange, onSubmit }) {
  return (
    <form className="chat-input-form" onSubmit={onSubmit}>
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder="Ask about a trademark, patent, or filing issue..."
        className="chat-input"
      />
      <button type="submit" className="primary-btn">Send</button>
    </form>
  )
}

export default ChatInput
