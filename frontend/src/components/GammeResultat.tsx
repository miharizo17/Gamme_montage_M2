import { useEffect, useState } from 'react'
import { ApiError, enregistrerGamme, listerOperateursChaine } from '../api/gammeApi'
import type { GammeGeneree, OperationProposee } from '../types/gamme'
import '../assets/css/Form.css'
import '../assets/css/GammeResultat.css'

interface GammeResultatProps {
  gamme: GammeGeneree
  // SMV saisie des le depart (avant generation), sur la page Ajout. Si
  // fournie, les temps sont repartis dessus des l'affichage - modifiable
  // ensuite via le champ "Repartir sur un total de".
  smvInitiale?: number | null
  onChoisirChaine?: (chaine: string) => void
}

function sommeSecondes(operations: OperationProposee[]): number {
  return operations.reduce((total, op) => total + (op.temps_estime ?? 0), 0)
}

function repartirOperations(operations: OperationProposee[], cibleMinutes: number): OperationProposee[] {
  const somme = sommeSecondes(operations)
  if (!cibleMinutes || cibleMinutes <= 0 || somme <= 0) return operations

  const facteur = (cibleMinutes * 60) / somme
  return operations.map((op) =>
    op.temps_estime != null
      ? { ...op, temps_estime: Math.round(op.temps_estime * facteur * 10) / 10, temps_mesure: false, temps_source: null }
      : op,
  )
}

// Etiquette affichee a cote du temps, selon son origine. Rien pour un
// temps chronometre reel (le cas normal) ; explicite sinon, pour que
// l'agent de methode sache toujours si une valeur est a verifier.
function libelleSourceTemps(operation: OperationProposee): string | null {
  if (operation.temps_estime == null) return null
  if (operation.temps_source === 'ml') return 'prédit par IA'
  if (operation.temps_source === 'historique_operateur') return 'historique opérateur'
  if (!operation.temps_mesure) return 'estimé'
  return null
}

function GammeResultat({ gamme, smvInitiale, onChoisirChaine }: GammeResultatProps) {
  // Etat local editable : l'agent de methode peut corriger les
  // suggestions de l'IA (operation, operateur, temps) directement dans
  // le tableau, sans que ca touche a la generation elle-meme.
  const [operations, setOperations] = useState<OperationProposee[]>(gamme.operations)
  const [operateursConnus, setOperateursConnus] = useState<string[]>([])

  const [nomGamme, setNomGamme] = useState(gamme.article_reference_nom)
  const [dateEnregistrement, setDateEnregistrement] = useState(() => new Date().toISOString().slice(0, 10))
  const [enregistrement, setEnregistrement] = useState<'idle' | 'chargement' | 'succes' | 'erreur'>('idle')
  const [messageEnregistrement, setMessageEnregistrement] = useState<string | null>(null)
  const [smvCible, setSmvCible] = useState('0')

  // SMV = Standard Minute Value = temps total pour produire une piece =
  // somme des temps de toutes les operations. Recalculee a chaque
  // changement (edition manuelle ou repartition).
  const sommeSecondesActuelle = sommeSecondes(operations)
  const smvActuelleMinutes = sommeSecondesActuelle / 60

  useEffect(() => {
    if (smvInitiale && smvInitiale > 0) {
      setOperations(repartirOperations(gamme.operations, smvInitiale))
      setSmvCible(smvInitiale.toFixed(1))
    } else {
      setOperations(gamme.operations)
      setSmvCible((sommeSecondes(gamme.operations) / 60).toFixed(1))
    }
    setNomGamme(gamme.article_reference_nom)
    setEnregistrement('idle')
    setMessageEnregistrement(null)
  }, [gamme, smvInitiale])

  function repartirSmv() {
    setOperations((precedent) => repartirOperations(precedent, Number(smvCible)))
  }

  useEffect(() => {
    if (!gamme.chaine) {
      setOperateursConnus([])
      return
    }
    listerOperateursChaine(gamme.chaine)
      .then((liste) => setOperateursConnus(liste.map((o) => o.nom)))
      .catch(() => setOperateursConnus([]))
  }, [gamme.chaine])

  function modifierLibelle(ordre: number, valeur: string) {
    setOperations((precedent) =>
      precedent.map((op) => (op.ordre === ordre ? { ...op, operation_libelle: valeur } : op)),
    )
  }

  function modifierTemps(ordre: number, valeur: string) {
    const nombre = valeur === '' ? null : Number(valeur)
    setOperations((precedent) =>
      precedent.map((op) =>
        op.ordre === ordre
          ? { ...op, temps_estime: Number.isNaN(nombre) ? op.temps_estime : nombre, temps_mesure: true, temps_source: null }
          : op,
      ),
    )
  }

  function modifierOperateur(ordre: number, valeur: string) {
    setOperations((precedent) =>
      precedent.map((op) =>
        op.ordre === ordre
          ? { ...op, operateur_suggere: valeur || null, operateur_meme_chaine: null, operateur_nb_occurrences: null }
          : op,
      ),
    )
  }

  async function handleEnregistrer() {
    setEnregistrement('chargement')
    setMessageEnregistrement(null)
    try {
      const resultat = await enregistrerGamme({
        nom: nomGamme.trim(),
        chaine: gamme.chaine,
        date_creation: dateEnregistrement ? new Date(dateEnregistrement).toISOString() : null,
        operations: operations.map((op) => ({
          ordre: op.ordre,
          operation_libelle: op.operation_libelle,
          temps_estime: op.temps_estime,
          machine: op.machine,
          operateur_nom: op.operateur_suggere,
        })),
      })
      setEnregistrement('succes')
      setMessageEnregistrement(`Enregistree (reference "${resultat.code}") — visible dans l'historique.`)
    } catch (error) {
      setEnregistrement('erreur')
      setMessageEnregistrement(error instanceof ApiError ? error.message : 'Erreur inattendue, reessayez.')
    }
  }

  return (
    <div className="gamme-resultat">
      <div className="gamme-resultat-header">
        <div>
          <span className="gamme-resultat-label">Gamme de reference retrouvee</span>
          <h3>{gamme.article_reference_nom}</h3>
          <span className="gamme-resultat-code">{gamme.article_reference_code}</span>
          {gamme.chaine && <span className="gamme-resultat-chaine">Chaine : {gamme.chaine}</span>}
        </div>
        <div className="gamme-resultat-score">
          <span className="gamme-resultat-label">Similarite</span>
          <strong>{Math.round(gamme.score_similarite * 100)}%</strong>
        </div>
      </div>

      <div className="gamme-resultat-smv">
        <div>
          <span className="gamme-resultat-label">SMV totale (temps standard de production)</span>
          <strong className="gamme-resultat-smv-valeur">
            {smvActuelleMinutes.toFixed(1)} min
            <span className="gamme-resultat-smv-secondes"> ({Math.round(sommeSecondesActuelle)} s)</span>
          </strong>
        </div>
        <div className="gamme-resultat-smv-cible">
          <label htmlFor="smv-cible" className="form-label">
            Repartir sur un total de (minutes)
          </label>
          <div className="gamme-resultat-smv-cible-champ">
            <input
              id="smv-cible"
              type="number"
              min={0}
              step="0.1"
              className="form-input"
              value={smvCible}
              onChange={(event) => setSmvCible(event.target.value)}
            />
            <button type="button" className="gamme-resultat-repartir-btn" onClick={repartirSmv}>
              Repartir
            </button>
          </div>
        </div>
      </div>

      {gamme.chaines_suggerees.length > 0 && (
        <div className="gamme-resultat-suggestions">
          <span className="gamme-resultat-label">Chaines les mieux equipees pour cette production</span>
          <ul>
            {gamme.chaines_suggerees.map((suggestion) => (
              <li key={suggestion.chaine}>
                <span>
                  <strong>{suggestion.chaine}</strong>
                  {suggestion.chaine === gamme.chaine && ' (chaine actuelle)'} — {suggestion.nb_operations_couvertes}/
                  {suggestion.nb_operations_total} operations couvertes
                </span>
                {onChoisirChaine && suggestion.chaine !== gamme.chaine && (
                  <button type="button" className="gamme-resultat-suggestion-btn" onClick={() => onChoisirChaine(suggestion.chaine)}>
                    Choisir cette chaine
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="gamme-resultat-hint">Vous pouvez corriger l'operation, le temps ou l'operateur directement dans le tableau.</p>

      <table className="gamme-resultat-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Operation</th>
            <th>Machine</th>
            <th>Temps estime</th>
            <th>Operateur suggere</th>
          </tr>
        </thead>
        <tbody>
          {operations.map((operation) => (
            <tr key={operation.ordre}>
              <td>{operation.ordre}</td>
              <td>
                <input
                  className="gamme-resultat-input"
                  value={operation.operation_libelle}
                  onChange={(event) => modifierLibelle(operation.ordre, event.target.value)}
                />
              </td>
              <td>{operation.machine ?? '—'}</td>
              <td>
                <span className="gamme-resultat-temps">
                  <input
                    className="gamme-resultat-input gamme-resultat-input-temps"
                    type="number"
                    min={0}
                    step="0.1"
                    value={operation.temps_estime ?? ''}
                    onChange={(event) => modifierTemps(operation.ordre, event.target.value)}
                    title={operation.temps_mesure ? 'Temps chronometre / confirme' : 'Temps non chronometre : voir etiquette'}
                  />
                  <span>
                    s
                    {libelleSourceTemps(operation) && (
                      <span className={`gamme-resultat-badge-temps gamme-resultat-badge-temps-${operation.temps_source ?? 'estime'}`}>
                        {' '}
                        {libelleSourceTemps(operation)}
                      </span>
                    )}
                  </span>
                </span>
              </td>
              <td>
                <input
                  className={`gamme-resultat-input${operation.operateur_meme_chaine === false ? ' gamme-resultat-operateur-autre-chaine' : ''}`}
                  value={operation.operateur_suggere ?? ''}
                  onChange={(event) => modifierOperateur(operation.ordre, event.target.value)}
                  list="gamme-resultat-operateurs-connus"
                  placeholder="Non affecte"
                  title={
                    operation.operateur_meme_chaine === false
                      ? "Aucun operateur experimente sur la chaine cible : suggestion d'une autre chaine"
                      : undefined
                  }
                />
                {operation.operateur_suggere && operation.operateur_nb_occurrences != null && (
                  <span className="gamme-resultat-occurrences"> ({operation.operateur_nb_occurrences}×)</span>
                )}
                {operation.operateur_meme_chaine === false && ' ⚠'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <datalist id="gamme-resultat-operateurs-connus">
        {operateursConnus.map((nom) => (
          <option key={nom} value={nom} />
        ))}
      </datalist>

      <div className="gamme-resultat-enregistrement">
        <div className="form-field">
          <label htmlFor="nom-gamme" className="form-label">
            Nom de cette gamme
          </label>
          <input id="nom-gamme" className="form-input" value={nomGamme} onChange={(event) => setNomGamme(event.target.value)} />
        </div>
        <div className="form-field">
          <label htmlFor="date-gamme" className="form-label">
            Date d'enregistrement
          </label>
          <input
            id="date-gamme"
            type="date"
            className="form-input"
            value={dateEnregistrement}
            onChange={(event) => setDateEnregistrement(event.target.value)}
          />
        </div>
        <button
          type="button"
          className="gamme-resultat-enregistrer-btn"
          onClick={handleEnregistrer}
          disabled={enregistrement === 'chargement' || !nomGamme.trim()}
        >
          {enregistrement === 'chargement' ? 'Enregistrement…' : 'Enregistrer cette gamme'}
        </button>
        {messageEnregistrement && (
          <p className={enregistrement === 'erreur' ? 'gamme-resultat-message-erreur' : 'gamme-resultat-message-succes'}>
            {messageEnregistrement}
          </p>
        )}
      </div>
    </div>
  )
}

export default GammeResultat
