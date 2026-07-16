import type { InputHTMLAttributes } from 'react'
import '../../assets/css/Form.css'

interface CheckboxFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

function CheckboxField({ label, id, className, ...rest }: CheckboxFieldProps) {
  return (
    <label htmlFor={id} className="form-checkbox">
      <input id={id} type="checkbox" className={`form-checkbox-input${className ? ` ${className}` : ''}`} {...rest} />
      {label && <span className="form-checkbox-label">{label}</span>}
    </label>
  )
}

export default CheckboxField
