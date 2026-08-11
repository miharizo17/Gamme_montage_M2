import { useEffect, useState } from 'react'
import {
  ApiError,
  exporterGammeExcel,
  exporterGammePdf,
  listerOperateursChaine,
  modifierLigneGamme,
} from '../api/gammeApi'
import type { ArticleDetail, GammeLigne } from '../types/article'
import '../assets/css/ArticleDetailView.css'

interface ArticleDetailViewProps {
  article: ArticleDetail
  onFermer: () => void
}

function telechargerBlob(blob: Blob, nomFichier: string) {
  const url = URL.createObjectURL(blob)
  const lien = document.createElement('a')
  lien.href = url
  lien.download = nomFichier
  document.body.appendChild(lien)
  lien.click()
  lien.remove()
  URL.revokeObjectURL(url)
}

function formaterDate(dateIso: string | null): string {
  if (!dateIso) return '—'
  return new Date(dateIso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function ArticleDetailView({ article, onFermer }: ArticleDetailViewProps) {
  const [lignes, setLignes] = useState<GammeLigne[]>(article.lignes_gamme)
  const [operateursConnus, setOperateursConnus] = useState<string[]>([])
  const [enregistrement, setEnregistrement] = useState<'idle' | 'chargement' | 'succes' | 'erreur'>('idle')
  const [message, setMessage] = useState<string | null>(null)
  const [exportEnCours, setExportEnCours] = useState<'excel' | 'pdf' | null>(null)

  useEffect(() => {
    setLignes(article.lignes_gamme)
    setEnregistrement('idle')
    setMessage(null)
  }, [article])

  useEffect(() => {
    if (!article.chaine) {
      setOperateursConnus([])
      return
    }
    listerOperateursChaine(article.chaine)
      .then((liste) => setOperateursConnus(liste.map((o) => o.nom)))
      .catch(() => setOperateursConnus([]))
  }, [article.chaine])

  function modifierChamp<K extends keyof GammeLigne>(ligneId: number, champ: K, valeur: GammeLigne[K]) {
    setLignes((precedent) => precedent.map((l) => (l.id === ligneId ? { ...l, [champ]: valeur } : l)))
  }

  async function handleExporter(format: 'excel' | 'pdf') {
    setExportEnCours(format)
    try {
      const blob = format === 'excel' ? await exporterGammeExcel(article.id) : await exporterGammePdf(article.id)
      telechargerBlob(blob, `${article.code}.${format === 'excel' ? 'xlsx' : 'pdf'}`)
    } catch {
      setMessage("Echec de l'export, reessayez.")
      setEnregistrement('erreur')
    } finally {
      setExportEnCours(null)
    }
  }

  async function handleEnregistrer() {
    setEnregistrement('chargement')
    setMessage(null)
    try {
      await Promise.all(
        lignes.map((ligne) =>
          modifierLigneGamme(ligne.id, {
            operation_libelle: ligne.operation_libelle,
            temps_equilibre: ligne.temps_equilibre,
            operateur_nom: ligne.operateur_nom,
          }),
        ),
      )
      setEnregistrement('succes')
      setMessage('Modifications enregistrees.')
    } catch (error) {
      setEnregistrement('erreur')
      setMessage(error instanceof ApiError ? error.message : 'Erreur inattendue, reessayez.')
    }
  }

  return (
    <div className="article-detail">
      <div className="article-detail-header">
        <div>
          <span className="article-detail-label">Gamme historique</span>
          <h3>{article.nom}</h3>
          <span className="article-detail-code">{article.code}</span>
          {article.chaine && <span className="article-detail-chaine">Chaine : {article.chaine}</span>}
          <span className="article-detail-date">Enregistree le {formaterDate(article.date_creation)}</span>
        </div>
        <div className="article-detail-header-actions">
          <button
            type="button"
            className="article-detail-export-btn"
            onClick={() => handleExporter('excel')}
            disabled={exportEnCours !== null}
          >
            {exportEnCours === 'excel' ? 'Export…' : 'Exporter Excel'}
          </button>
          <button
            type="button"
            className="article-detail-export-btn"
            onClick={() => handleExporter('pdf')}
            disabled={exportEnCours !== null}
          >
            {exportEnCours === 'pdf' ? 'Export…' : 'Exporter PDF'}
          </button>
          <button type="button" className="article-detail-fermer" onClick={onFermer}>
            ← Retour a la liste
          </button>
        </div>
      </div>

      {lignes.length === 0 ? (
        <p className="article-detail-vide">Aucune operation enregistree pour cette gamme.</p>
      ) : (
        <>
          <table className="article-detail-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Operation</th>
                <th>Machine</th>
                <th>Temps</th>
                <th>Operateur</th>
              </tr>
            </thead>
            <tbody>
              {lignes.map((ligne) => (
                <tr key={ligne.id}>
                  <td>{ligne.ordre}</td>
                  <td>
                    <input
                      className="article-detail-input"
                      value={ligne.operation_libelle}
                      onChange={(event) => modifierChamp(ligne.id, 'operation_libelle', event.target.value)}
                    />
                  </td>
                  <td>{ligne.machine ?? '—'}</td>
                  <td>
                    <input
                      className="article-detail-input article-detail-input-temps"
                      type="number"
                      min={0}
                      step="0.1"
                      value={ligne.temps_equilibre ?? ''}
                      onChange={(event) => {
                        const valeur = event.target.value
                        const nombre = valeur === '' ? null : Number(valeur)
                        modifierChamp(ligne.id, 'temps_equilibre', Number.isNaN(nombre) ? ligne.temps_equilibre : nombre)
                      }}
                    />
                    s
                  </td>
                  <td>
                    <input
                      className="article-detail-input"
                      value={ligne.operateur_nom ?? ''}
                      onChange={(event) => modifierChamp(ligne.id, 'operateur_nom', event.target.value || null)}
                      list="article-detail-operateurs-connus"
                      placeholder="Non affecte"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <datalist id="article-detail-operateurs-connus">
            {operateursConnus.map((nom) => (
              <option key={nom} value={nom} />
            ))}
          </datalist>

          <div className="article-detail-actions">
            <button type="button" className="article-detail-enregistrer-btn" onClick={handleEnregistrer} disabled={enregistrement === 'chargement'}>
              {enregistrement === 'chargement' ? 'Enregistrement…' : 'Enregistrer les modifications'}
            </button>
            {message && (
              <p className={enregistrement === 'erreur' ? 'article-detail-message-erreur' : 'article-detail-message-succes'}>
                {message}
              </p>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default ArticleDetailView
