import type { NavItem } from '../types/nav'

function AjoutIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10" cy="10" r="7.3" />
      <path d="M10 6.5v7M6.5 10h7" />
    </svg>
  )
}

function HistoriqueIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="3.4" cy="5" r="0.9" fill="currentColor" stroke="none" />
      <circle cx="3.4" cy="10" r="0.9" fill="currentColor" stroke="none" />
      <circle cx="3.4" cy="15" r="0.9" fill="currentColor" stroke="none" />
      <path d="M7 5h9.6M7 10h9.6M7 15h9.6" />
    </svg>
  )
}

export const navItems: NavItem[] = [
  { id: 'ajout', label: 'Ajout', icon: <AjoutIcon /> },
  { id: 'historique', label: 'Historique', icon: <HistoriqueIcon /> },
]
