import { useEffect, useState } from 'react'
import { ApiError, listerArticles, listerChaines, obtenirArticle } from '../api/gammeApi'
import ArticleDetailView from '../components/ArticleDetailView'
import type { Article, ArticleDetail, ArticleListe } from '../types/article'
import type { Chaine } from '../types/chaine'
import '../assets/css/Form.css'
import '../assets/css/HistoriquePage.css'

const LIMITE = 20

function formaterDate(dateIso: string | null): string {
  if (!dateIso) return '—'
  return new Date(dateIso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function HistoriquePage() {
  const [recherche, setRecherche] = useState('')
  const [chaineFiltre, setChaineFiltre] = useState('')
  const [skip, setSkip] = useState(0)
  const [chaines, setChaines] = useState<Chaine[]>([])
  const [resultat, setResultat] = useState<ArticleListe | null>(null)
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)
  const [articleSelectionne, setArticleSelectionne] = useState<ArticleDetail | null>(null)

  useEffect(() => {
    listerChaines()
      .then(setChaines)
      .catch(() => setChaines([]))
  }, [])

  // Revenir a la premiere page quand la recherche ou le filtre change.
  useEffect(() => {
    setSkip(0)
  }, [recherche, chaineFiltre])

  useEffect(() => {
    const id = setTimeout(() => {
      setChargement(true)
      setErreur(null)
      listerArticles({ skip, limit: LIMITE, q: recherche || undefined, chaine: chaineFiltre || undefined })
        .then(setResultat)
        .catch((error) => setErreur(error instanceof ApiError ? error.message : 'Erreur inattendue, reessayez.'))
        .finally(() => setChargement(false))
    }, 300)
    return () => clearTimeout(id)
  }, [recherche, chaineFiltre, skip])

  async function ouvrirDetail(article: Article) {
    setErreur(null)
    try {
      setArticleSelectionne(await obtenirArticle(article.id))
    } catch (error) {
      setErreur(error instanceof ApiError ? error.message : 'Erreur inattendue, reessayez.')
    }
  }

  const total = resultat?.total ?? 0
  const debut = total === 0 ? 0 : skip + 1
  const fin = Math.min(skip + LIMITE, total)

  return (
    <div>
      <h2>Historique des gammes</h2>

      {articleSelectionne ? (
        <ArticleDetailView article={articleSelectionne} onFermer={() => setArticleSelectionne(null)} />
      ) : (
        <>
          <div className="historique-filtres">
            <input
              type="search"
              className="form-input"
              placeholder="Rechercher par nom ou reference…"
              value={recherche}
              onChange={(event) => setRecherche(event.target.value)}
            />
            <select
              className="form-input historique-select-chaine"
              value={chaineFiltre}
              onChange={(event) => setChaineFiltre(event.target.value)}
            >
              <option value="">Toutes les chaines</option>
              {chaines.map((c) => (
                <option key={c.chaine} value={c.chaine}>
                  {c.chaine} ({c.nb_gammes})
                </option>
              ))}
            </select>
          </div>

          {erreur && <p className="historique-erreur">{erreur}</p>}

          <table className="historique-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Nom</th>
                <th>Chaine</th>
                <th>Date d'enregistrement</th>
              </tr>
            </thead>
            <tbody>
              {resultat?.items.map((article) => (
                <tr key={article.id} onClick={() => ouvrirDetail(article)}>
                  <td>{article.code}</td>
                  <td>{article.nom}</td>
                  <td>{article.chaine ?? '—'}</td>
                  <td>{formaterDate(article.date_creation)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {chargement && <p className="historique-info">Chargement…</p>}
          {!chargement && resultat && resultat.items.length === 0 && <p className="historique-info">Aucun resultat.</p>}

          {total > 0 && (
            <div className="historique-pagination">
              <span>
                {debut}-{fin} sur {total}
              </span>
              <div className="historique-pagination-boutons">
                <button type="button" disabled={skip === 0} onClick={() => setSkip((s) => Math.max(0, s - LIMITE))}>
                  Precedent
                </button>
                <button type="button" disabled={fin >= total} onClick={() => setSkip((s) => s + LIMITE)}>
                  Suivant
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default HistoriquePage
