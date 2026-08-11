import { useEffect, useState } from 'react'
import { ApiError } from '../api/apiClient'
import { obtenirStatistiques } from '../api/statistiquesApi'
import type { Statistiques } from '../types/statistiques'
import '../assets/css/DashboardPage.css'

function DashboardPage() {
  const [stats, setStats] = useState<Statistiques | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    obtenirStatistiques()
      .then(setStats)
      .catch((error) => setErreur(error instanceof ApiError ? error.message : 'Erreur inattendue'))
  }, [])

  if (erreur) return <p className="dashboard-erreur">{erreur}</p>
  if (!stats) return <p>Chargement...</p>

  const maxGammesMois = Math.max(1, ...stats.gammes_par_mois.map((m) => m.nb_gammes))
  const maxArticlesChaine = Math.max(1, ...stats.articles_par_chaine.map((c) => c.nb_articles))

  return (
    <div>
      <h2>Dashboard</h2>

      <div className="dashboard-cartes">
        <div className="dashboard-carte">
          <span className="dashboard-carte-label">Articles</span>
          <strong className="dashboard-carte-valeur">{stats.nb_articles}</strong>
        </div>
        <div className="dashboard-carte">
          <span className="dashboard-carte-label">Gammes de montage</span>
          <strong className="dashboard-carte-valeur">{stats.nb_gammes}</strong>
        </div>
        <div className="dashboard-carte">
          <span className="dashboard-carte-label">Operateurs actifs</span>
          <strong className="dashboard-carte-valeur">{stats.nb_operateurs_actifs}</strong>
        </div>
        <div className="dashboard-carte">
          <span className="dashboard-carte-label">Chaines de production</span>
          <strong className="dashboard-carte-valeur">{stats.nb_chaines}</strong>
        </div>
        <div className="dashboard-carte">
          <span className="dashboard-carte-label">SMV moyen</span>
          <strong className="dashboard-carte-valeur">
            {stats.smv_moyen_minutes != null ? `${stats.smv_moyen_minutes} min` : '—'}
          </strong>
        </div>
      </div>

      <div className="dashboard-graphiques">
        <div className="dashboard-graphique">
          <h3>Gammes creees par mois</h3>
          {stats.gammes_par_mois.length === 0 && <p className="dashboard-vide">Aucune donnee</p>}
          <ul className="dashboard-barres">
            {stats.gammes_par_mois.map((m) => (
              <li key={m.mois}>
                <span className="dashboard-barre-label">{m.mois}</span>
                <span className="dashboard-barre-piste">
                  <span
                    className="dashboard-barre-remplissage"
                    style={{ width: `${(m.nb_gammes / maxGammesMois) * 100}%` }}
                  />
                </span>
                <span className="dashboard-barre-valeur">{m.nb_gammes}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="dashboard-graphique">
          <h3>Articles par chaine (top 15)</h3>
          {stats.articles_par_chaine.length === 0 && <p className="dashboard-vide">Aucune donnee</p>}
          <ul className="dashboard-barres">
            {stats.articles_par_chaine.map((c) => (
              <li key={c.chaine}>
                <span className="dashboard-barre-label">{c.chaine}</span>
                <span className="dashboard-barre-piste">
                  <span
                    className="dashboard-barre-remplissage"
                    style={{ width: `${(c.nb_articles / maxArticlesChaine) * 100}%` }}
                  />
                </span>
                <span className="dashboard-barre-valeur">{c.nb_articles}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
