CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    age INTEGER,
    revenu REAL,
    historique_credit INTEGER,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    montant REAL,
    type TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    nb_transactions INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE credits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    montant_demande REAL,
    score_credit REAL,
    decision TEXT,
    date_demande DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    type TEXT,
    message TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
