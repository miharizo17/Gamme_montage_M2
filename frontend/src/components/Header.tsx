import BrandBlock from './BrandBlock'
import NavTabs from './NavTabs'
import { navItems } from '../data/navItems'
import useClock from '../hooks/useClock'
import '../assets/css/Header.css'

interface HeaderProps {
  activeTab: string
  onTabChange: (id: string) => void
}

function Header({ activeTab, onTabChange }: HeaderProps) {
  const now = useClock()
  const dateLabel = capitalize(
    now.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }),
  )
  const timeLabel = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <header className="app-header">
      <div className="app-header-top">
        <BrandBlock />
        <div className="app-header-date">
          <span className="app-header-date-full">{dateLabel}</span>
          <span className="app-header-date-time">{timeLabel}</span>
        </div>
      </div>
      <NavTabs items={navItems} activeId={activeTab} onChange={onTabChange} />
    </header>
  )
}

function capitalize(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export default Header
