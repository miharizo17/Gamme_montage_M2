import { useState } from 'react'
import type { ComponentType } from 'react'
import Header from './components/Header'
import AjoutPage from './pages/AjoutPage'
import HistoriquePage from './pages/HistoriquePage'
import DashboardPage from './pages/DashboardPage'
import SkillMatrixPage from './pages/SkillMatrixPage'
import UtilisateursPage from './pages/UtilisateursPage'
import LoginPage from './pages/LoginPage'
import { AuthProvider, useAuth } from './context/AuthContext'
import './assets/css/App.css'

const pages: Record<string, ComponentType> = {
  ajout: AjoutPage,
  historique: HistoriquePage,
  dashboard: DashboardPage,
  skillmatrix: SkillMatrixPage,
  utilisateurs: UtilisateursPage,
}

const CLE_ONGLET_ACTIF = 'gamme-montage:onglet-actif'

function lireOngletInitial(): string {
  try {
    const stocke = localStorage.getItem(CLE_ONGLET_ACTIF)
    return stocke && stocke in pages ? stocke : 'ajout'
  } catch {
    return 'ajout'
  }
}

function AppConnecte() {
  const [activeTab, setActiveTab] = useState(lireOngletInitial)
  const ActivePage = pages[activeTab] ?? AjoutPage

  function handleTabChange(id: string) {
    setActiveTab(id)
    try {
      localStorage.setItem(CLE_ONGLET_ACTIF, id)
    } catch {
      // Stockage indisponible (navigation privee, etc.) : on continue sans persister.
    }
  }

  return (
    <div className="app">
      <Header activeTab={activeTab} onTabChange={handleTabChange} />
      <main className="app-content">
        <ActivePage />
      </main>
    </div>
  )
}

function AppInterne() {
  const { utilisateur, chargement } = useAuth()

  if (chargement) {
    return <div className="app-chargement">Chargement...</div>
  }
  if (!utilisateur) {
    return <LoginPage />
  }
  return <AppConnecte />
}

function App() {
  return (
    <AuthProvider>
      <AppInterne />
    </AuthProvider>
  )
}

export default App
