import { useState } from 'react'
import type { FormEvent } from 'react'
import { NumberField, TextAreaField } from '../components/form'
import ChaineSelector from '../components/ChaineSelector'
import GammeResultat from '../components/GammeResultat'
import { ApiError, genererGamme } from '../api/gammeApi'
import type { GammeGeneree } from '../types/gamme'
import '../assets/css/AjoutPage.css'

function AjoutPage() {
  const [description, setDescription] = useState('')
  const [chaine, setChaine] = useState('')
  const [smv, setSmv] = useState('')
  const [equilibrerCharge, setEquilibrerCharge] = useState(false)
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)
  const [resultat, setResultat] = useState<GammeGeneree | null>(null)

  async function generer(chaineChoisie: string) {
    setChargement(true)
    setErreur(null)

    try {
      const gamme = await genererGamme(description, chaineChoisie || null, equilibrerCharge)
      setResultat(gamme)
    } catch (error) {
      setErreur(error instanceof ApiError ? error.message : 'Erreur inattendue, reessayez.')
    } finally {
      setChargement(false)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setResultat(null)
    generer(chaine)
  }

  function handleChoisirChaineSuggeree(nouvelleChaine: string) {
    setChaine(nouvelleChaine)
    generer(nouvelleChaine)
  }

  return (
    <div>
      <h2>Nouvelle gamme</h2>
      <form onSubmit={handleSubmit} className="ajout-form">
        <TextAreaField
          label="Description du prototype"
          placeholder="Ex: veste femme doublee, fermeture zip, deux poches passepoilees, col tailleur"
          rows={4}
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          required
          minLength={3}
        />
        <ChaineSelector value={chaine} onChange={setChaine} />
        <NumberField
          label="SMV visee (minutes, optionnel)"
          placeholder="Ex: 22"
          min={0}
          step="0.1"
          value={smv}
          onChange={(event) => setSmv(event.target.value)}
        />
        <label className="form-checkbox">
          <input
            type="checkbox"
            className="form-checkbox-input"
            checked={equilibrerCharge}
            onChange={(event) => setEquilibrerCharge(event.target.checked)}
          />
          Equilibrer la charge entre operateurs (balancement de ligne)
        </label>
        <button type="submit" className="ajout-submit" disabled={chargement || description.trim().length < 3}>
          {chargement ? 'Generation en cours…' : 'Generer la gamme'}
        </button>
      </form>

      {erreur && <p className="ajout-erreur">{erreur}</p>}
      {resultat && (
        <GammeResultat
          gamme={resultat}
          smvInitiale={smv ? Number(smv) : null}
          onChoisirChaine={handleChoisirChaineSuggeree}
        />
      )}
    </div>
  )
}

export default AjoutPage
