-- Clients fictifs
INSERT INTO clients (nom, age, revenu, historique_credit) VALUES
('Alexie', 28, 3500, 2),
('kevin', 40, 5000, 5),
('Antoine', 22, 2000, 1),
('Diane', 35, 4200, 3);

-- Transactions fictives
INSERT INTO transactions (client_id, montant, type, nb_transactions) VALUES
(1, 1500, 'paiement', 5),
(2, 5000, 'virement', 12),
(3, 800, 'retrait', 2),
(4, 2500, 'paiement', 7);

-- Crédits fictifs
INSERT INTO credits (client_id, montant_demande, score_credit, decision) VALUES
(1, 2000, 0.85, 'Accepté'),
(2, 7000, 0.40, 'Refusé'),
(3, 1500, 0.70, 'Accepté');

-- Alertes fictives
INSERT INTO alertes (client_id, type, message) VALUES
(2, 'fraude', 'Transaction suspecte détectée'),
(3, 'surendettement', 'Risque de défaut de paiement'),
(4, 'conformité', 'Contrôle AML requis');
