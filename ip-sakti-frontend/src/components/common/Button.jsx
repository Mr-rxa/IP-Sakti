function Button({ children, variant = 'primary', type = 'button', onClick, className = '', ...props }) {
  const variantClass = variant === 'secondary' ? 'secondary-btn' : 'primary-btn'

  return (
    <button
      type={type}
      className={`${variantClass} ${className}`.trim()}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
