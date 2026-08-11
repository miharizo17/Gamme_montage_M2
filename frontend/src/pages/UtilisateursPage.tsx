import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../api/apiClient'
import { creerUtilisateur, listerUtilisateurs } from '../api/authApi'
import type { UtilisateurCourant } from '../api/authApi'
import '../assets/css/UtilisateursPage.css'

function UtilisateursPage() {
  const [utilisateurs, setUtilisateurs] = useState<UtilisateurCourant[]>([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState<string | null>(null)

  const [nomUtilisateur, setNomUtilisateur] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [role, setRole] = useState<'agent_methode' | 'administrateur'>('agent_methode')
  const [enCours, setEnCours] = useState(false)
  const [erreurCreation, setErreurCreation] = useState<string | null>(null)

  function recharger() {
    setChargement(true)
    listerUtilisateurs()
      .then(setUtilisateurs)
      .catch((error) => setErreur(error instanceof ApiError ? error.message : 'Erreur inattendue'))
      .finally(() => setChargement(false))
  }

  useEffect(recharger, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setErreurCreation(null)
    setEnCours(true)
    try {
      await creerUtilisateur({ nom_utilisateur: nomUtilisateur, mot_de_passe: motDePasse, role })
      setNomUtilisateur('')
      setMotDePasse('')
      setRole('agent_methode')
      recharger()
    } catch (error) {
      setErreurCreation(error instanceof ApiError ? error.message : 'Erreur inattendue')
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div>
      <h2>Comptes utilisateurs</h2>

      <form className="utilisateurs-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label className="form-label" htmlFor="nouv-nom">
            Nom d'utilisateur
          </label>
          <input
            id="nouv-nom"
            className="form-input"
            value={nomUtilisateur}
            onChange={(event) => setNomUtilisateur(event.target.value)}
            required
            minLength={3}
          />
        </div>
        <div className="form-field">
          <label className="form-label" htmlFor="nouv-mdp">
            Mot de passe
          </label>
          <input
            id="nouv-mdp"
            className="form-input"
            type="password"
            value={motDePasse}
            onChange={(event) => setMotDePasse(event.target.value)}
            required
            minLength={6}
          />
        </div>
        <div className="form-field">
          <label className="form-label" htmlFor="nouv-role">
            Role
          </label>
          <select
            id="nouv-role"
            className="form-input"
            value={role}
            onChange={(event) => setRole(event.target.value as 'agent_methode' | 'administrateur')}
          >
            <option value="agent_methode">Agent methode</option>
            <option value="administrateur">Administrateur</option>
          </select>
        </div>
        <button type="submit" className="utilisateurs-submit" disabled={enCours}>
          {enCours ? 'Creation...' : 'Creer le compte'}
        </button>
      </form>
      {erreurCreation && <p className="utilisateurs-erreur">{erreurCreation}</p>}

      {chargement && <p>Chargement...</p>}
      {erreur && <p className="utilisateurs-erreur">{erreur}</p>}
      {!chargement && !erreur && (
        <table className="utilisateurs-table">
          <thead>
            <tr>
              <th>Nom d'utilisateur</th>
              <th>Role</th>
              <th>Actif</th>
              <th>Cree le</th>
            </tr>
          </thead>
          <tbody>
            {utilisateurs.map((u) => (
              <tr key={u.id}>
                <td>{u.nom_utilisateur}</td>
                <td>{u.role}</td>
                <td>{u.actif ? 'Oui' : 'Non'}</td>
                <td>{new Date(u.date_creation).toLocaleDateString('fr-FR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default UtilisateursPage
