import { get, getBlob, post, put } from './apiClient'
import type { ArticleDetail, ArticleListe, GammeLigne } from '../types/article'
import type { Chaine, MatriceCompetences, OperateurChaine } from '../types/chaine'
import type { EnregistrerGammePayload, GammeGeneree } from '../types/gamme'

export { ApiError } from './apiClient'

export function genererGamme(
  description: string,
  chaine: string | null,
  equilibrerCharge = false,
): Promise<GammeGeneree> {
  return post<GammeGeneree>('/gammes/generer', { description, chaine, equilibrer_charge: equilibrerCharge })
}

export function enregistrerGamme(payload: EnregistrerGammePayload): Promise<ArticleDetail> {
  return post<ArticleDetail>('/gammes/enregistrer', payload)
}

export interface ModifierLigneGammePayload {
  operation_libelle?: string
  temps_equilibre?: number | null
  machine?: string | null
  operateur_nom?: string | null
}

export function modifierLigneGamme(ligneId: number, payload: ModifierLigneGammePayload): Promise<GammeLigne> {
  return put<GammeLigne>(`/gamme-lignes/${ligneId}`, payload)
}

export function listerChaines(): Promise<Chaine[]> {
  return get<Chaine[]>('/chaines')
}

export function listerOperateursChaine(chaine: string): Promise<OperateurChaine[]> {
  return get<OperateurChaine[]>(`/chaines/${encodeURIComponent(chaine)}/operateurs`)
}

export function obtenirMatriceCompetences(chaine: string): Promise<MatriceCompetences> {
  return get<MatriceCompetences>(`/chaines/${encodeURIComponent(chaine)}/matrice-competences`)
}

export interface ListerArticlesOptions {
  skip?: number
  limit?: number
  q?: string
  chaine?: string
}

export function listerArticles(options: ListerArticlesOptions = {}): Promise<ArticleListe> {
  const params = new URLSearchParams()
  params.set('skip', String(options.skip ?? 0))
  params.set('limit', String(options.limit ?? 20))
  if (options.q) params.set('q', options.q)
  if (options.chaine) params.set('chaine', options.chaine)
  return get<ArticleListe>(`/articles?${params.toString()}`)
}

export function obtenirArticle(articleId: number): Promise<ArticleDetail> {
  return get<ArticleDetail>(`/articles/${articleId}`)
}

export function exporterGammeExcel(articleId: number): Promise<Blob> {
  return getBlob(`/articles/${articleId}/export/excel`)
}

export function exporterGammePdf(articleId: number): Promise<Blob> {
  return getBlob(`/articles/${articleId}/export/pdf`)
}
