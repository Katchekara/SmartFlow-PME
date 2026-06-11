-- Table des clients
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    solde REAL NOT NULL
);

-- Table des crédits
CREATE TABLE IF NOT EXISTS credits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    montant REAL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Table des transactions
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    montant REAL,
    type TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Table des alertes de fraude
CREATE TABLE IF NOT EXISTS alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    description TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- ============================
-- Données de test
-- ============================

-- Clients
INSERT INTO clients (id, nom, solde) VALUES (1, 'Alice', 2500);
INSERT INTO clients (id, nom, solde) VALUES (2, 'Bob', 1800);
INSERT INTO clients (id, nom, solde) VALUES (3, 'Charlie', -200); -- client à risque
INSERT INTO clients (id, nom, solde) VALUES (4, 'Diane', 5000);

-- Transactions (revenus et dépenses)
INSERT INTO transactions (client_id, montant, type) VALUES (1, 3000, 'revenu');
INSERT INTO transactions (client_id, montant, type) VALUES (1, 500, 'paiement');
INSERT INTO transactions (client_id, montant, type) VALUES (2, 2000, 'revenu');
INSERT INTO transactions (client_id, montant, type) VALUES (2, 1200, 'retrait');
INSERT INTO transactions (client_id, montant, type) VALUES (3, 500, 'revenu');
INSERT INTO transactions (client_id, montant, type) VALUES (3, 700, 'paiement');
INSERT INTO transactions (client_id, montant, type) VALUES (4, 6000, 'revenu');
INSERT INTO transactions (client_id, montant, type) VALUES (4, 1000, 'paiement');

-- Crédits
INSERT INTO credits (client_id, montant) VALUES (1, 1000);
INSERT INTO credits (client_id, montant) VALUES (2, 1500);
INSERT INTO credits (client_id, montant) VALUES (3, 500); -- client déjà endetté

-- Alertes de fraude
INSERT INTO alertes (client_id, description) VALUES (3, 'Suspicion de fraude sur retrait');
