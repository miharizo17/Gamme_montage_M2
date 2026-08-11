import type { TextareaHTMLAttributes } from 'react'
import '../../assets/css/Form.css'

interface TextAreaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
}

function TextAreaField({ label, id, className, ...rest }: TextAreaFieldProps) {
  return (
    <div className="form-field">
      {label && (
        <label htmlFor={id} className="form-label">
          {label}
        </label>
      )}
      <textarea id={id} className={`form-input${className ? ` ${className}` : ''}`} {...rest} />
    </div>
  )
}

export default TextAreaField
