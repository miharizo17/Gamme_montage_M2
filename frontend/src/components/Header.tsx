import BrandBlock from './BrandBlock'
import NavTabs from './NavTabs'
import { navItemsPourRole } from '../data/navItems'
import useClock from '../hooks/useClock'
import { useAuth } from '../context/AuthContext'
import '../assets/css/Header.css'

interface HeaderProps {
  activeTab: string
  onTabChange: (id: string) => void
}

function Header({ activeTab, onTabChange }: HeaderProps) {
  const now = useClock()
  const { utilisateur, deconnecter } = useAuth()
  const dateLabel = capitalize(
    now.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }),
  )
  const timeLabel = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <header className="app-header">
      <div className="app-header-top">
        <BrandBlock />
        <div className="app-header-right">
          <div className="app-header-date">
            <span className="app-header-date-full">{dateLabel}</span>
            <span className="app-header-date-time">{timeLabel}</span>
          </div>
          {utilisateur && (
            <div className="app-header-utilisateur">
              <span className="app-header-utilisateur-nom">{utilisateur.nom_utilisateur}</span>
              <span className="app-header-utilisateur-role">{utilisateur.role}</span>
              <button type="button" className="app-header-deconnexion" onClick={deconnecter}>
                Deconnexion
              </button>
            </div>
          )}
        </div>
      </div>
      <NavTabs items={navItemsPourRole(utilisateur?.role)} activeId={activeTab} onChange={onTabChange} />
    </header>
  )
}

function capitalize(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export default Header
