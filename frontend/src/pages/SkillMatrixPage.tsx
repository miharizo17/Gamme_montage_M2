import { useEffect, useState } from 'react'
import { ApiError, listerChaines, obtenirMatriceCompetences } from '../api/gammeApi'
import type { Chaine, MatriceCompetences } from '../types/chaine'
import '../assets/css/Form.css'
import '../assets/css/SkillMatrixPage.css'

function intensite(nbOccurrences: number, max: number): number {
  if (max <= 0) return 0
  return Math.min(1, nbOccurrences / max)
}

function SkillMatrixPage() {
  const [chaines, setChaines] = useState<Chaine[]>([])
  const [chaine, setChaine] = useState('')
  const [matrice, setMatrice] = useState<MatriceCompetences | null>(null)
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    listerChaines()
      .then((liste) => {
        setChaines(liste)
        if (liste.length > 0) setChaine(liste[0].chaine)
      })
      .catch(() => setChaines([]))
  }, [])

  useEffect(() => {
    if (!chaine) {
      setMatrice(null)
      return
    }
    setChargement(true)
    setErreur(null)
    obtenirMatriceCompetences(chaine)
      .then(setMatrice)
      .catch((error) => setErreur(error instanceof ApiError ? error.message : 'Erreur inattendue'))
      .finally(() => setChargement(false))
  }, [chaine])

  const maxOccurrences = matrice
    ? Math.max(1, ...matrice.cellules.map((c) => c.nb_occurrences))
    : 1
  const cellule = (operateur: string, operation: string) =>
    matrice?.cellules.find((c) => c.operateur_nom === operateur && c.operation_libelle === operation)

  return (
    <div>
      <h2>Matrice de competences</h2>
      <div className="form-field skillmatrix-selecteur">
        <label htmlFor="skillmatrix-chaine" className="form-label">
          Chaine de production
        </label>
        <select
          id="skillmatrix-chaine"
          className="form-input"
          value={chaine}
          onChange={(event) => setChaine(event.target.value)}
        >
          {chaines.map((c) => (
            <option key={c.chaine} value={c.chaine}>
              {c.chaine}
            </option>
          ))}
        </select>
      </div>

      {erreur && <p className="skillmatrix-erreur">{erreur}</p>}
      {chargement && <p>Chargement...</p>}

      {!chargement && matrice && matrice.operateurs.length === 0 && (
        <p className="skillmatrix-vide">Aucune competence connue sur cette chaine.</p>
      )}

      {!chargement && matrice && matrice.operateurs.length > 0 && (
        <div className="skillmatrix-scroll">
          <table className="skillmatrix-table">
            <thead>
              <tr>
                <th>Operateur</th>
                {matrice.operations.map((operation) => (
                  <th key={operation} title={operation}>
                    {operation}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrice.operateurs.map((operateur) => (
                <tr key={operateur}>
                  <td className="skillmatrix-operateur">{operateur}</td>
                  {matrice.operations.map((operation) => {
                    const c = cellule(operateur, operation)
                    return (
                      <td
                        key={operation}
                        className="skillmatrix-cellule"
                        style={
                          c
                            ? { backgroundColor: `rgba(156, 107, 82, ${0.15 + intensite(c.nb_occurrences, maxOccurrences) * 0.75})` }
                            : undefined
                        }
                        title={c ? `${c.nb_occurrences} occurrences, ${c.temps_moyen?.toFixed(1) ?? '?'}s en moyenne` : 'Aucune experience'}
                      >
                        {c ? c.nb_occurrences : ''}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="skillmatrix-hint">
        Limitee aux operateurs et operations les plus significatifs de la chaine (volume d'occurrences) pour rester lisible.
      </p>
    </div>
  )
}

export default SkillMatrixPage
