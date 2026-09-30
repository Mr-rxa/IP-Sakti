function ProgressBar({ value = 0, max = 100 }) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  return (
    <div className="progress-bar">
      <div className="progress-fill" style={{ width: `${percentage}%` }} />
    </div>
  )
}

export default ProgressBar
