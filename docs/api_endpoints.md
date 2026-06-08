# SmartFlow PME — Documentation des Endpoints API

## Base URL
http://127.0.0.1:8000

---

## 1. Clients

### POST /clients/ — Créer un client
```json
{
  "nom": "PME Kaboré",
  "age": 35,
  "revenu": 8000000,
  "historique_credit": 2
}
```
**Réponse :**
```json
{
  "id": 1,
  "nom": "PME Kaboré",
  "age": 35,
  "revenu": 8000000,
  "historique_credit": 2,
  "date_creation": "2026-06-08T14:20:04"
}
```

---

### GET /clients/ — Lister tous les clients
**Réponse :** Liste de tous les clients enregistrés.

---

### GET /clients/{client_id} — Obtenir un client
**Réponse :** Détails du client correspondant à l'ID.

---

## 2. Transactions

### POST /transactions/ — Créer une transaction
```json
{
  "client_id": 1,
  "montant": 500000,
  "type": "paiement",
  "nb_transactions": 3
}
```

---

### GET /transactions/ — Lister toutes les transactions

---

### GET /transactions/{client_id} — Transactions d'un client

---

## 3. Crédits IA

### POST /credits/ — Demande de crédit
```json
{
  "client_id": 1,
  "montant_demande": 5000000,
  "secteur": "commerce",
  "nb_employes": 12,
  "retards_paiement": 1,
  "montant_dette": 2000000,
  "transactions_mobile": 250
}
```
**Réponse :**
```json
{
  "id": 1,
  "client_id": 1,
  "montant_demande": 5000000,
  "score_credit": 1,
  "decision": "Accepté",
  "date_demande": "2026-06-08T14:21:24"
}
```

---

### GET /credits/ — Lister tous les crédits

---

## 4. Détection de Fraude IA

### POST /fraud/ — Analyser une transaction
```json
{
  "client_id": 1,
  "montant": 4500000,
  "heure_transaction": 3,
  "nb_transactions_jour": 25,
  "distance_km": 450,
  "nouveau_destinataire": 1,
  "echecs_recents": 3,
  "type_transaction": "transfert"
}
```
**Réponse :**
```json
{
  "decision": "Fraude suspectée",
  "risque": "100.0%",
  "action": "Bloquer et alerter le propriétaire",
  "alerte": {
    "id": 1,
    "type": "fraude",
    "message": "Transaction suspecte : transfert de 4,500,000 FCFA — risque 100.0%",
    "client_id": 1,
    "date": "2026-06-08T14:22:50"
  }
}
```

---

### GET /fraud/alertes — Lister toutes les alertes

---

### GET /fraud/alertes/{client_id} — Alertes d'un client

---

## Codes de réponse

| Code | Signification |
|------|---------------|
| 200 | ✅ Succès |
| 400 | ❌ Données invalides |
| 404 | ❌ Ressource introuvable |
| 500 | ❌ Erreur serveur |

