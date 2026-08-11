export interface Chaine {
  chaine: string
  nb_gammes: number
}

export interface OperateurChaine {
  operateur_id: number
  nom: string
  nb_operations_distinctes: number
  nb_occurrences_total: number
}

export interface CelluleCompetence {
  operateur_nom: string
  operation_libelle: string
  nb_occurrences: number
  temps_moyen: number | null
}

export interface MatriceCompetences {
  chaine: string
  operateurs: string[]
  operations: string[]
  cellules: CelluleCompetence[]
}
