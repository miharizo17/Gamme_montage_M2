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

function UtilisateursIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10" cy="7" r="3.2" />
      <path d="M4 16.5c0-3 2.7-5 6-5s6 2 6 5" />
    </svg>
  )
}

function DashboardIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="6" height="6" rx="1" />
      <rect x="11" y="3" width="6" height="6" rx="1" />
      <rect x="3" y="11" width="6" height="6" rx="1" />
      <rect x="11" y="11" width="6" height="6" rx="1" />
    </svg>
  )
}

function SkillMatrixIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="14" height="14" rx="1.5" />
      <path d="M3 8.3h14M3 13.6h14M8.3 3v14M13.6 3v14" />
    </svg>
  )
}

export const navItems: NavItem[] = [
  { id: 'ajout', label: 'Ajout', icon: <AjoutIcon /> },
  { id: 'historique', label: 'Historique', icon: <HistoriqueIcon /> },
  { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
  { id: 'skillmatrix', label: 'Competences', icon: <SkillMatrixIcon /> },
]

export function navItemsPourRole(role: string | undefined): NavItem[] {
  if (role === 'administrateur') {
    return [...navItems, { id: 'utilisateurs', label: 'Utilisateurs', icon: <UtilisateursIcon /> }]
  }
  return navItems
}
