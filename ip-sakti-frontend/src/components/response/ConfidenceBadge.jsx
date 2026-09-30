function ConfidenceBadge({ score = 0 }) {
  return (
    <span className="confidence-badge">How sure is this answer: {score}%</span>
  )
}

export default ConfidenceBadge
