export interface Article {
  id: number
  code: string
  nom: string
  description: string | null
  source: string | null
  chaine: string | null
  date_creation: string | null
}

export interface ArticleListe {
  total: number
  skip: number
  limit: number
  items: Article[]
}

export interface GammeLigne {
  id: number
  ordre: number
  operation_libelle: string
  temps_equilibre: number | null
  target: number | null
  machine: string | null
  operateur_nom: string | null
}

export interface ArticleDetail extends Article {
  gamme_id: number | null
  lignes_gamme: GammeLigne[]
}
