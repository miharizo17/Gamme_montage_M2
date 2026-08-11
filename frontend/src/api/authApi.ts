import { get, post } from './apiClient'

export interface TokenReponse {
  access_token: string
  token_type: string
  role: string
  nom_utilisateur: string
}

export interface UtilisateurCourant {
  id: number
  nom_utilisateur: string
  role: string
  actif: boolean
  date_creation: string
}

export function seConnecter(nomUtilisateur: string, motDePasse: string): Promise<TokenReponse> {
  return post<TokenReponse>('/auth/login', { nom_utilisateur: nomUtilisateur, mot_de_passe: motDePasse }, true)
}

export function obtenirUtilisateurCourant(): Promise<UtilisateurCourant> {
  return get<UtilisateurCourant>('/auth/moi')
}

export function listerUtilisateurs(): Promise<UtilisateurCourant[]> {
  return get<UtilisateurCourant[]>('/auth/utilisateurs')
}

export interface CreerUtilisateurPayload {
  nom_utilisateur: string
  mot_de_passe: string
  role: 'agent_methode' | 'administrateur'
}

export function creerUtilisateur(payload: CreerUtilisateurPayload): Promise<UtilisateurCourant> {
  return post<UtilisateurCourant>('/auth/utilisateurs', payload)
}
