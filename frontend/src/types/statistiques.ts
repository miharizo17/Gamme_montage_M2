export interface GammeParMois {
  mois: string
  nb_gammes: number
}

export interface ArticleParChaine {
  chaine: string
  nb_articles: number
}

export interface Statistiques {
  nb_articles: number
  nb_gammes: number
  nb_operateurs_actifs: number
  nb_chaines: number
  smv_moyen_minutes: number | null
  gammes_par_mois: GammeParMois[]
  articles_par_chaine: ArticleParChaine[]
}
