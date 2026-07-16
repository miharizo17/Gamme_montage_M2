import type { InputHTMLAttributes } from 'react'
import '../../assets/css/Form.css'

interface DateFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

function DateField({ label, id, className, ...rest }: DateFieldProps) {
  return (
    <div className="form-field">
      {label && (
        <label htmlFor={id} className="form-label">
          {label}
        </label>
      )}
      <input id={id} type="date" className={`form-input${className ? ` ${className}` : ''}`} {...rest} />
    </div>
  )
}

export default DateField
