import type { InputHTMLAttributes } from 'react'
import '../../assets/css/Form.css'

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

function TextField({ label, id, className, ...rest }: TextFieldProps) {
  return (
    <div className="form-field">
      {label && (
        <label htmlFor={id} className="form-label">
          {label}
        </label>
      )}
      <input id={id} type="text" className={`form-input${className ? ` ${className}` : ''}`} {...rest} />
    </div>
  )
}

export default TextField
