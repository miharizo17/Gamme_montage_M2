import logo from '../assets/img/logo-loi-confection.png'
import '../assets/css/BrandBlock.css'

function BrandBlock() {
  return (
    <div className="brand-block">
      <img src={logo} alt="L.O.I Confection" className="brand-logo" />
      <h1 className="brand-title">Gamme de montage</h1>
    </div>
  )
}

export default BrandBlock
