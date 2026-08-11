import { test, expect } from '@playwright/test'

// Comptes de demonstration crees par backend/scripts/creer_utilisateur_admin.py
// (voir e2e/README.md). Ces tests ne creent ni ne modifient aucune donnee
// en base : uniquement des verifications de lecture/navigation.
const ADMIN = { nom: 'admin', motDePasse: 'Admin2026!' }
const AGENT = { nom: 'agent1', motDePasse: 'Agent2026!' }

async function seConnecter(page: import('@playwright/test').Page, nom: string, motDePasse: string) {
  await page.goto('/')
  await page.fill('#login-nom', nom)
  await page.fill('#login-mdp', motDePasse)
  await page.click('.login-bouton')
  await page.waitForSelector('.app-header-utilisateur-nom', { timeout: 10_000 })
}

test('affiche le login quand aucun token n’est present', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.login-card')).toBeVisible()
})

test('refuse un mauvais mot de passe', async ({ page }) => {
  await page.goto('/')
  await page.fill('#login-nom', AGENT.nom)
  await page.fill('#login-mdp', 'mauvais-mot-de-passe')
  await page.click('.login-bouton')
  await expect(page.locator('.login-erreur')).toBeVisible()
})

test('connexion agent_methode : pas d’onglet Utilisateurs', async ({ page }) => {
  await seConnecter(page, AGENT.nom, AGENT.motDePasse)
  await expect(page.locator('.app-header-utilisateur-nom')).toHaveText(AGENT.nom)
  await expect(page.locator('text=Utilisateurs')).toHaveCount(0)
})

test('connexion administrateur : onglet Utilisateurs visible', async ({ page }) => {
  await seConnecter(page, ADMIN.nom, ADMIN.motDePasse)
  await expect(page.locator('text=Utilisateurs')).toBeVisible()
})

test('la session survit a un rechargement de page', async ({ page }) => {
  await seConnecter(page, AGENT.nom, AGENT.motDePasse)
  await page.reload({ waitUntil: 'networkidle' })
  await expect(page.locator('.app-header-utilisateur-nom')).toHaveText(AGENT.nom)
})

test('la deconnexion ramene au login', async ({ page }) => {
  await seConnecter(page, AGENT.nom, AGENT.motDePasse)
  await page.click('.app-header-deconnexion')
  await expect(page.locator('.login-card')).toBeVisible()
})
