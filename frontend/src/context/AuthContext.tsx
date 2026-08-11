import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import type { ReactNode } from 'react'
import { lireToken, stockerToken, supprimerToken } from '../api/apiClient'
import { seConnecter, obtenirUtilisateurCourant } from '../api/authApi'
import type { UtilisateurCourant } from '../api/authApi'

interface AuthContextValue {
  utilisateur: UtilisateurCourant | null
  chargement: boolean
  connecter: (nomUtilisateur: string, motDePasse: string) => Promise<void>
  deconnecter: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [utilisateur, setUtilisateur] = useState<UtilisateurCourant | null>(null)
  const [chargement, setChargement] = useState(true)

  const deconnecter = useCallback(() => {
    supprimerToken()
    setUtilisateur(null)
  }, [])

  useEffect(() => {
    const token = lireToken()
    if (!token) {
      setChargement(false)
      return
    }
    obtenirUtilisateurCourant()
      .then(setUtilisateur)
      .catch(() => supprimerToken())
      .finally(() => setChargement(false))
  }, [])

  useEffect(() => {
    function surNonAuthentifie() {
      setUtilisateur(null)
    }
    window.addEventListener('gamme-montage:non-authentifie', surNonAuthentifie)
    return () => window.removeEventListener('gamme-montage:non-authentifie', surNonAuthentifie)
  }, [])

  const connecter = useCallback(async (nomUtilisateur: string, motDePasse: string) => {
    const reponse = await seConnecter(nomUtilisateur, motDePasse)
    stockerToken(reponse.access_token)
    const utilisateurComplet = await obtenirUtilisateurCourant()
    setUtilisateur(utilisateurComplet)
  }, [])

  return (
    <AuthContext.Provider value={{ utilisateur, chargement, connecter, deconnecter }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth doit etre utilise a l\'interieur de AuthProvider')
  }
  return ctx
}
