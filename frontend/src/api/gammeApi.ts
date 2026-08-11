import type { ArticleDetail, ArticleListe, GammeLigne } from '../types/article'
import type { Chaine, OperateurChaine } from '../types/chaine'
import type { EnregistrerGammePayload, GammeGeneree } from '../types/gamme'

const API_BASE = '/api/gamme-montage'

export class ApiError extends Error {}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    const message = typeof payload?.detail === 'string' ? payload.detail : `Erreur ${response.status}`
    throw new ApiError(message)
  }
  return response.json() as Promise<T>
}

async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`)
  return handleResponse<T>(response)
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse<T>(response)
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return handleResponse<T>(response)
}

export function genererGamme(description: string, chaine: string | null): Promise<GammeGeneree> {
  return post<GammeGeneree>('/gammes/generer', { description, chaine })
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
