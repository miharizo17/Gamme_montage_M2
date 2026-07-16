import type { InputHTMLAttributes } from 'react'
import '../../assets/css/Form.css'

interface FileFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

function FileField({ label, id, className, ...rest }: FileFieldProps) {
  return (
    <div className="form-field">
      {label && (
        <label htmlFor={id} className="form-label">
          {label}
        </label>
      )}
      <input id={id} type="file" className={`form-input form-input-file${className ? ` ${className}` : ''}`} {...rest} />
    </div>
  )
}

export default FileField
