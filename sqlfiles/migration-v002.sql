-- Création de la table si elle n'existe pas
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    promo VARCHAR(50)
);

-- Insertion de données de test (uniquement si la table est vide)
INSERT INTO students (nom, promo)
SELECT 'Alice Dupont', 'M2 TI'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE nom = 'Alice Dupont');

INSERT INTO students (nom, promo)
SELECT 'Bob Martin', 'M2 GL'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE nom = 'Bob Martin');

INSERT INTO students (nom, promo)
SELECT 'Charlie Durand', 'M2 DATA'
WHERE NOT EXISTS (SELECT 1 FROM students WHERE nom = 'Charlie Durand');