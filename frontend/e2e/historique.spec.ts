import { test, expect } from '@playwright/test'

const AGENT = { nom: 'agent1', motDePasse: 'Agent2026!' }

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await page.fill('#login-nom', AGENT.nom)
  await page.fill('#login-mdp', AGENT.motDePasse)
  await page.click('.login-bouton')
  await page.waitForSelector('.app-header-utilisateur-nom', { timeout: 10_000 })
  await page.click('text=Historique')
})

test('liste les gammes historiques avec pagination', async ({ page }) => {
  await expect(page.locator('.historique-table tbody tr').first()).toBeVisible({ timeout: 15_000 })
  await expect(page.locator('.historique-pagination')).toBeVisible()
})

test('filtre par recherche texte', async ({ page }) => {
  await expect(page.locator('.historique-table tbody tr').first()).toBeVisible({ timeout: 15_000 })
  await page.fill('input[type="search"]', 'zzzzzzz-terme-introuvable-zzzzzzz')
  await page.waitForTimeout(500) // debounce de la recherche
  await expect(page.locator('text=Aucun resultat.')).toBeVisible({ timeout: 10_000 })

  await page.fill('input[type="search"]', '')
  await page.waitForTimeout(500)
  await expect(page.locator('.historique-table tbody tr').first()).toBeVisible({ timeout: 10_000 })
})

test('ouvre le detail d’une gamme et affiche ses operations', async ({ page }) => {
  await expect(page.locator('.historique-table tbody tr').first()).toBeVisible({ timeout: 15_000 })
  await page.click('.historique-table tbody tr >> nth=0')

  await expect(page.locator('.article-detail-table, .article-detail-vide')).toBeVisible({ timeout: 10_000 })
  await expect(page.locator('.article-detail-export-btn').first()).toBeVisible()

  await page.click('text=Retour a la liste')
  await expect(page.locator('.historique-table')).toBeVisible()
})

test('reste sur l’onglet Historique apres un rechargement', async ({ page }) => {
  await page.reload({ waitUntil: 'networkidle' })
  await expect(page.locator('h2:has-text("Historique des gammes")')).toBeVisible()
})
