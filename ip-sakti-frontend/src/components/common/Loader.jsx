function Loader({ label = 'Loading...' }) {
  return (
    <div className="empty-state">
      <p>{label}</p>
    </div>
  )
}

export default Loader
