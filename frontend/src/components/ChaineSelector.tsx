import { useEffect, useState } from 'react'
import { listerChaines, listerOperateursChaine } from '../api/gammeApi'
import type { Chaine, OperateurChaine } from '../types/chaine'
import '../assets/css/Form.css'
import '../assets/css/ChaineSelector.css'

interface ChaineSelectorProps {
  value: string
  onChange: (chaine: string) => void
}

function ChaineSelector({ value, onChange }: ChaineSelectorProps) {
  const [chaines, setChaines] = useState<Chaine[]>([])
  const [operateurs, setOperateurs] = useState<OperateurChaine[]>([])
  const [chargementOperateurs, setChargementOperateurs] = useState(false)

  useEffect(() => {
    listerChaines()
      .then(setChaines)
      .catch(() => setChaines([]))
  }, [])

  useEffect(() => {
    if (!value) {
      setOperateurs([])
      return
    }
    setChargementOperateurs(true)
    listerOperateursChaine(value)
      .then(setOperateurs)
      .catch(() => setOperateurs([]))
      .finally(() => setChargementOperateurs(false))
  }, [value])

  return (
    <div className="chaine-selector">
      <div className="form-field">
        <label htmlFor="chaine-select" className="form-label">
          Chaine de production
        </label>
        <select id="chaine-select" className="form-input" value={value} onChange={(event) => onChange(event.target.value)}>
          <option value="">Deduire automatiquement de la gamme retrouvee</option>
          {chaines.map((c) => (
            <option key={c.chaine} value={c.chaine}>
              {c.chaine} ({c.nb_gammes} gammes historiques)
            </option>
          ))}
        </select>
      </div>

      {value && (
        <div className="chaine-operateurs">
          <span className="chaine-operateurs-label">Operateurs de cette chaine</span>
          {chargementOperateurs && <p className="chaine-operateurs-vide">Chargement…</p>}
          {!chargementOperateurs && operateurs.length === 0 && (
            <p className="chaine-operateurs-vide">Aucun operateur connu sur cette chaine.</p>
          )}
          {!chargementOperateurs && operateurs.length > 0 && (
            <ul className="chaine-operateurs-liste">
              {operateurs.map((operateur) => (
                <li key={operateur.operateur_id}>
                  <span>{operateur.nom}</span>
                  <span className="chaine-operateurs-detail">
                    {operateur.nb_operations_distinctes} operations maitrisees ({operateur.nb_occurrences_total}×)
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default ChaineSelector
