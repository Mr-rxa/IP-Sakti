function CitationList({ citations = [] }) {
  if (!citations.length) return null

  return (
    <div className="card">
      <h3>Answer proof: where this information came from</h3>
      <ul className="citation-list">
        {citations.map((citation, index) => (
          <li key={`${citation}-${index}`}>{citation}</li>
        ))}
      </ul>
    </div>
  )
}

export default CitationList
