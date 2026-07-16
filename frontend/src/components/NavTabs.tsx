import type { NavItem } from '../types/nav'
import '../assets/css/NavTabs.css'

interface NavTabsProps {
  items: NavItem[]
  activeId: string
  onChange: (id: string) => void
}

function NavTabs({ items, activeId, onChange }: NavTabsProps) {
  return (
    <nav className="nav-tabs">
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          className={`nav-tab${item.id === activeId ? ' nav-tab-active' : ''}`}
          onClick={() => onChange(item.id)}
        >
          <span className="nav-tab-icon">{item.icon}</span>
          {item.label}
        </button>
      ))}
    </nav>
  )
}

export default NavTabs
