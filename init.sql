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

-- Données de test
INSERT INTO clients (id, nom, solde) VALUES (1, 'Alice', 2500);
INSERT INTO clients (id, nom, solde) VALUES (2, 'Bob', 1800);

INSERT INTO transactions (client_id, montant, type) VALUES (1, 200, 'paiement');
INSERT INTO transactions (client_id, montant, type) VALUES (2, 500, 'retrait');

INSERT INTO credits (client_id, montant) VALUES (1, 1000);
INSERT INTO credits (client_id, montant) VALUES (2, 1500);

INSERT INTO alertes (client_id, description) VALUES (2, 'Suspicion de fraude sur retrait');
