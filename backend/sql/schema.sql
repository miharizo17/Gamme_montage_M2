-- =============================================================
-- Schema PostgreSQL du projet Gamme_montage_M2
-- Genere a partir des modeles SQLAlchemy (backend/models/models.py)
-- Base attendue : gamme_montage (voir backend/database.py)
--
-- Usage :
--   psql -h 127.0.0.1 -p 5432 -U postgres -d gamme_montage -f schema.sql
-- =============================================================


-- -------------------------------------------------------------
-- TABLES
-- -------------------------------------------------------------

CREATE TABLE IF NOT EXISTS article (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(150) NOT NULL UNIQUE,   -- reference du prototype (ex: DEMO-001, ou chemin relatif nettoye pour les imports reels)
    nom         VARCHAR(200) NOT NULL,
    description TEXT,                            -- description du prototype (entree du moteur NLP)
    source      VARCHAR(300),                     -- dossier/fichier d'origine, ou "donnees de test"
    chaine      VARCHAR(100)                      -- chaine/ligne de production extraite du chemin source
);

CREATE TABLE IF NOT EXISTS operateur (
    id        SERIAL PRIMARY KEY,
    nom       VARCHAR(120) NOT NULL,
    matricule VARCHAR(30),
    actif     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS gamme (
    id             SERIAL PRIMARY KEY,
    article_id     INTEGER NOT NULL REFERENCES article (id) ON DELETE CASCADE,
    date_creation  TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS gamme_ligne (
    id                 SERIAL PRIMARY KEY,
    gamme_id           INTEGER NOT NULL REFERENCES gamme (id) ON DELETE CASCADE,
    ordre              INTEGER NOT NULL,          -- position reelle dans le tableau source (PAS "POSTE N", peu fiable)
    operation_libelle  VARCHAR(200) NOT NULL,
    temps_equilibre    FLOAT,                      -- TEMPS EQUILIBREE (secondes)
    target             FLOAT,                      -- QTE/H/OPERATION ou TRGT CHRONO
    machine            VARCHAR(100),                -- MATERIEL / TYPE MACHINE
    operateur_id       INTEGER REFERENCES operateur (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS competence (
    id                 SERIAL PRIMARY KEY,
    operateur_id       INTEGER NOT NULL REFERENCES operateur (id) ON DELETE CASCADE,
    operation_libelle  VARCHAR(200) NOT NULL,
    chaine             VARCHAR(100),               -- une chaine a ses propres operateurs
    nb_occurrences     INTEGER NOT NULL DEFAULT 0,
    temps_moyen        FLOAT,
    CONSTRAINT uq_competence_operateur_operation_chaine UNIQUE (operateur_id, operation_libelle, chaine)
);


-- -------------------------------------------------------------
-- INDEX (colonnes de jointure frequentes, non indexees automatiquement)
-- -------------------------------------------------------------

CREATE INDEX IF NOT EXISTS ix_gamme_article_id        ON gamme (article_id);
CREATE INDEX IF NOT EXISTS ix_gamme_ligne_gamme_id     ON gamme_ligne (gamme_id);
CREATE INDEX IF NOT EXISTS ix_gamme_ligne_operateur_id ON gamme_ligne (operateur_id);
CREATE INDEX IF NOT EXISTS ix_competence_operateur_id  ON competence (operateur_id);


-- =============================================================
-- VUES
-- =============================================================

-- Vue detaillee : chaque ligne de gamme avec le contexte article + operateur.
-- C'est la vue la plus utile pour l'API (afficher une gamme complete).
CREATE OR REPLACE VIEW v_gamme_detail AS
SELECT
    g.id                AS gamme_id,
    a.id                AS article_id,
    a.code              AS article_code,
    a.nom               AS article_nom,
    gl.id               AS ligne_id,
    gl.ordre,
    gl.operation_libelle,
    gl.temps_equilibre,
    gl.target,
    gl.machine,
    o.id                AS operateur_id,
    o.nom               AS operateur_nom
FROM gamme_ligne gl
JOIN gamme   g ON g.id = gl.gamme_id
JOIN article a ON a.id = g.article_id
LEFT JOIN operateur o ON o.id = gl.operateur_id
ORDER BY g.id, gl.ordre;


-- Vue resume : une ligne par gamme, avec le nombre d'operations et le
-- temps total (= somme des temps equilibres), utile pour lister les
-- gammes sans charger toutes les lignes.
CREATE OR REPLACE VIEW v_gamme_resume AS
SELECT
    g.id                          AS gamme_id,
    a.code                        AS article_code,
    a.nom                         AS article_nom,
    g.date_creation,
    COUNT(gl.id)                  AS nb_operations,
    COALESCE(SUM(gl.temps_equilibre), 0)  AS temps_total,
    COUNT(DISTINCT gl.operateur_id) AS nb_operateurs_distincts
FROM gamme g
JOIN article a ON a.id = g.article_id
LEFT JOIN gamme_ligne gl ON gl.gamme_id = g.id
GROUP BY g.id, a.code, a.nom, g.date_creation;


-- Vue matrice de competences : lisible directement (nom operateur en
-- clair), triee par operateur puis par nombre d'occurrences decroissant
-- (= ses operations les plus maitrisees en premier).
CREATE OR REPLACE VIEW v_competence_operateur AS
SELECT
    o.id                AS operateur_id,
    o.nom               AS operateur_nom,
    o.matricule,
    c.operation_libelle,
    c.chaine,
    c.nb_occurrences,
    c.temps_moyen
FROM competence c
JOIN operateur o ON o.id = c.operateur_id
ORDER BY o.nom, c.nb_occurrences DESC;
