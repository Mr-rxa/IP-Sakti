function JurisdictionToggle({ value = 'India', onChange }) {
  return (
    <div className="card">
      <label htmlFor="jurisdiction">Jurisdiction</label>
      <select id="jurisdiction" value={value} onChange={onChange} className="select-input">
        <option value="India">India</option>
        <option value="International">International</option>
      </select>
    </div>
  )
}

export default JurisdictionToggle
