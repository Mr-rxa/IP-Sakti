function QuestionCard({ question, options = [], onSelect }) {
  return (
    <div className="card question-card">
      <h3>{question}</h3>
      <div className="options-list">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            className="secondary-btn option-btn"
            onClick={() => onSelect(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}

export default QuestionCard
