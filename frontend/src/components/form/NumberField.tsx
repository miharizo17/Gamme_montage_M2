import type { InputHTMLAttributes } from 'react'
import '../../assets/css/Form.css'

interface NumberFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

function NumberField({ label, id, className, ...rest }: NumberFieldProps) {
  return (
    <div className="form-field">
      {label && (
        <label htmlFor={id} className="form-label">
          {label}
        </label>
      )}
      <input id={id} type="number" className={`form-input${className ? ` ${className}` : ''}`} {...rest} />
    </div>
  )
}

export default NumberField
