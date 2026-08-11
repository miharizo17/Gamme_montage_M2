import { useState } from 'react'
import type { FormEvent } from 'react'
import { useAuth } from '../context/AuthContext'
import '../assets/css/LoginPage.css'

function LoginPage() {
  const { connecter } = useAuth()
  const [nomUtilisateur, setNomUtilisateur] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [erreur, setErreur] = useState<string | null>(null)
  const [enCours, setEnCours] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setErreur(null)
    setEnCours(true)
    try {
      await connecter(nomUtilisateur, motDePasse)
    } catch {
      setErreur("Nom d'utilisateur ou mot de passe incorrect")
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1 className="login-titre">Gamme de montage</h1>
        <p className="login-sous-titre">LOI Confection — Connexion</p>

        <div className="form-field">
          <label className="form-label" htmlFor="login-nom">
            Nom d'utilisateur
          </label>
          <input
            id="login-nom"
            className="form-input"
            value={nomUtilisateur}
            onChange={(event) => setNomUtilisateur(event.target.value)}
            autoFocus
            autoComplete="username"
          />
        </div>

        <div className="form-field">
          <label className="form-label" htmlFor="login-mdp">
            Mot de passe
          </label>
          <input
            id="login-mdp"
            className="form-input"
            type="password"
            value={motDePasse}
            onChange={(event) => setMotDePasse(event.target.value)}
            autoComplete="current-password"
          />
        </div>

        {erreur && <p className="login-erreur">{erreur}</p>}

        <button className="login-bouton" type="submit" disabled={enCours || !nomUtilisateur || !motDePasse}>
          {enCours ? 'Connexion...' : 'Se connecter'}
        </button>
      </form>
    </div>
  )
}

export default LoginPage
