export type TempsSource = 'mesure' | 'historique_operateur' | 'ml' | null

export interface OperationProposee {
  ordre: number
  operation_libelle: string
  temps_estime: number | null
  temps_mesure: boolean
  temps_source: TempsSource
  machine: string | null
  operateur_suggere: string | null
  operateur_nb_occurrences: number | null
  operateur_meme_chaine: boolean | null
}

export interface ChaineSuggeree {
  chaine: string
  nb_operations_couvertes: number
  nb_operations_total: number
  experience_totale: number
}

export interface ChargeOperateur {
  operateur_nom: string
  nb_operations: number
  temps_total_secondes: number
}

export interface GammeGeneree {
  article_reference_id: number
  article_reference_code: string
  article_reference_nom: string
  chaine: string | null
  score_similarite: number
  operations: OperationProposee[]
  chaines_suggerees: ChaineSuggeree[]
  charge_operateurs: ChargeOperateur[]
  equilibrage_applique: boolean
}

export interface OperationAEnregistrer {
  ordre: number
  operation_libelle: string
  temps_estime: number | null
  machine: string | null
  operateur_nom: string | null
}

export interface EnregistrerGammePayload {
  nom: string
  chaine: string | null
  date_creation: string | null
  operations: OperationAEnregistrer[]
}
