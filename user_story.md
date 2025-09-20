# 🛍️ User Stories – NextGen Shop

> Application e-commerce multi-tenant avec gestion de boutiques personnelles.

---

## 🧑‍💼 Acteurs

| Acteur | Description |
|-------|-------------|
| Utilisateur non connecté | Visiteur du site |
| Utilisateur connecté | Client ou futur propriétaire de boutique |
| Propriétaire de boutique | Gère sa propre boutique |
| Administrateur global | Gère la plateforme entière |
| Système externe | Services de paiement, notification, etc. |

---

## 📚 Épics & User Stories

### Epic 1: Navigation & Découverte

#### US-01 : Consulter le catalogue
> En tant qu’utilisateur non connecté, je veux consulter le catalogue de produits pour découvrir ce qui est disponible.

**Conditions d’acceptation :**
- Voir une liste de produits avec nom, image, prix, disponibilité
- Aucune authentification requise
- Chargement rapide (< 2s)

---

#### US-02 : Rechercher un produit
> En tant qu’utilisateur non connecté, je veux rechercher un produit par mot-clé pour trouver rapidement ce que je cherche.

**Conditions d’acceptation :**
- Barre de recherche visible en haut de page
- Résultats filtrés en temps réel ou après soumission
- Filtre par nom et description

---

### Epic 2: Compte utilisateur

#### US-03 : Créer un compte
> En tant qu’utilisateur non connecté, je veux créer un compte pour accéder à mes commandes et créer une boutique.

**Conditions d’acceptation :**
- Formulaire avec email, mot de passe, confirmation
- Validation du format de l'email
- Compte créé, redirection vers connexion
- Pas de vérification par email (MVP)

---

### Epic 3: Panier & Commande

#### US-04 : Ajouter au panier
> En tant qu’utilisateur connecté, je veux ajouter un produit à mon panier pour préparer mon achat.

**Conditions d’acceptation :**
- Bouton "Ajouter au panier" sur chaque fiche produit
- Quantité personnalisable
- Le panier persiste entre les sessions (via session ou base)

---

#### US-05 : Voir son panier
> En tant qu’utilisateur connecté, je veux voir mon panier pour vérifier mes choix avant d’acheter.

**Conditions d’acceptation :**
- Page dédiée `/cart`
- Liste des produits avec quantité, prix unitaire, total
- Possibilité de modifier/supprimer un article
- Total général affiché clairement

---

#### US-06 : Passer commande
> En tant qu’utilisateur connecté, je veux passer commande pour acheter les produits de mon panier.

**Conditions d’acceptation :**
- Formulaire d’adresse de livraison
- Sélection du mode de paiement
- Récapitulatif avant validation
- Confirmation par email
- Statut initial : "pending"

---

### Epic 4: Boutique (Multi-tenancy)

#### US-07 : Créer une boutique
> En tant qu’utilisateur connecté, je veux créer ma propre boutique pour vendre mes produits.

**Conditions d’acceptation :**
- Formulaire avec nom, sous-domaine, plan tarifaire
- Sous-domaine doit être unique (`maboutique.nextgen.shop`)
- Boutique créée avec `tenant_id`
- Accès automatique au tableau de bord

---

#### US-08 : Gérer ses produits
> En tant que propriétaire de boutique, je veux ajouter, modifier ou supprimer des produits dans ma boutique.

**Conditions d’acceptation :**
- Interface simple d’ajout (nom, description, prix, stock, image)
- Publication immédiate ou brouillon
- Suppression avec confirmation
- Seuls les produits de ma boutique sont visibles

---

#### US-09 : Visualiser les ventes
> En tant que propriétaire de boutique, je veux voir mes ventes pour suivre mes performances.

**Conditions d’acceptation :**
- Tableau de bord avec chiffre d'affaires, nombre de commandes
- Filtres par date (jour/semaine/mois)
- Export CSV possible

---

### Epic 5: Administration

#### US-10 : Approuver une boutique
> En tant qu’administrateur, je veux approuver ou rejeter une nouvelle boutique pour garantir la qualité de la plateforme.

**Conditions d’acceptation :**
- Liste des boutiques en attente
- Boutons "Approuver" / "Rejeter"
- Notification envoyée à l’utilisateur

---

#### US-11 : Gérer les utilisateurs
> En tant qu’administrateur, je veux bloquer ou supprimer un utilisateur malveillant.

**Conditions d’acceptation :**
- Liste des utilisateurs avec statut actif/inactif
- Action rapide (bloquer/débloquer)
- Journal des actions conservé pendant 90 jours

---

### Epic 6: Systèmes externes

#### US-12 : Traiter un paiement
> En tant que système de paiement, je veux recevoir les données de paiement et confirmer la transaction.

**Conditions d’acceptation :**
- Intégration avec Stripe ou simulateur
- Webhook pour confirmation
- Mise à jour du statut de la commande à "paid"

---

#### US-13 : Envoyer une notification
> En tant que système de notification, je veux envoyer un email lors d’une action importante.

**Conditions d’acceptation :**
- Déclencheurs : création de commande, approbation de boutique
- Templates paramétrés (ex: `order_confirmation.html`)
- File d’attente via RabbitMQ

---

## 🏁 Priorisation (MoSCoW)

| Must have | Should have | Could have | Won't have |
|----------|-------------|------------|------------|
| US-01, US-03, US-04, US-05, US-06, US-07, US-08 | US-09, US-10, US-11 | US-12, US-13 | Fonctionnalités IA avancées (NLP), marketplace |
