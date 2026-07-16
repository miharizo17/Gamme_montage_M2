import { useState } from 'react'
import type { ComponentType } from 'react'
import Header from './components/Header'
import AjoutPage from './pages/AjoutPage'
import HistoriquePage from './pages/HistoriquePage'
import './assets/css/App.css'

const pages: Record<string, ComponentType> = {
  ajout: AjoutPage,
  historique: HistoriquePage,
}

function App() {
  const [activeTab, setActiveTab] = useState('ajout')
  const ActivePage = pages[activeTab]

  return (
    <div className="app">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="app-content">
        <ActivePage />
      </main>
    </div>
  )
}

export default App
