# Suite de tests E2E (Playwright)

Tests de bout en bout (frontend <-> backend <-> moteur IA) sur le
parcours reel de l'application : authentification, generation de gamme,
consultation de l'historique. Contrairement aux tests `pytest` du backend
(base SQLite en memoire, isoles), ces tests s'executent contre une **vraie
instance backend/PostgreSQL** : ils sont volontairement non destructifs
(aucun test ne clique sur "Enregistrer") pour pouvoir etre rejoues sans
polluer la base.

## Prerequis

1. Le backend FastAPI doit tourner (par defaut sur `http://127.0.0.1:8000`) :
   ```
   cd backend
   python -m uvicorn main:app --port 8000
   ```
2. Les comptes de demonstration doivent exister (idempotent, sans risque a rejouer) :
   ```
   cd backend
   python scripts/creer_utilisateur_admin.py admin Admin2026! --role administrateur
   python scripts/creer_utilisateur_admin.py agent1 Agent2026! --role agent_methode
   ```
3. Navigateur Playwright installe une seule fois : `npx playwright install chromium`

## Lancer la suite

```
npm run test:e2e
```

Playwright demarre automatiquement un serveur Vite dedie (port 3055,
`vite.config.e2e.ts`) qui proxifie vers le backend. Pour cibler un
backend sur un autre port (ex: instance isolee de verification) :

```
E2E_BACKEND_PORT=8091 npm run test:e2e
```

## Contenu

- `auth.spec.ts` — login/logout, mauvais mot de passe, persistance de
  session, navigation differenciee par role (agent_methode vs administrateur).
- `generation.spec.ts` — generation d'une gamme a partir d'une description,
  repartition SMV, balancement de charge entre operateurs.
- `historique.spec.ts` — liste, recherche, ouverture du detail d'une gamme,
  persistance de l'onglet actif apres rechargement.
