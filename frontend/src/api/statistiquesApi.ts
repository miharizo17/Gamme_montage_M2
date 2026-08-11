import { get } from './apiClient'
import type { Statistiques } from '../types/statistiques'

export function obtenirStatistiques(): Promise<Statistiques> {
  return get<Statistiques>('/statistiques')
}
