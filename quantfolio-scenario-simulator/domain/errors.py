"""
domain.entities/errors.py

Hiérarchie d'exceptions métier pour QuantFolio.

Règle de dépendance : ce module ne dépend de rien d'autre dans le projet
(ni services, ni repositories, ni UI). Il constitue le vocabulaire d'erreurs
partagé entre toutes les couches.

Convention :
- QuantFolioError est la classe mère unique -> point d'entrée pour un
  `except QuantFolioError` générique côté UI.
- Les classes de catégorie (ValidationError, NotFoundError, IntegrityError,
  ConcurrencyError) définissent une *réaction UI* commune.
- Les classes filles concrètes ne sont créées que lorsque l'UI a besoin
  d'une information structurée (ex: quel champ surligner) ou d'un message
  spécifique. Sinon, on lève directement la classe de catégorie avec un
  message clair.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class QuantFolioError(Exception):
    """Classe mère de toutes les erreurs métier de QuantFolio."""


# ---------------------------------------------------------------------------
# Catégorie 1 — Validation (entrée utilisateur invalide)
# Réaction UI attendue : surligner le champ concerné / message inline.
# ---------------------------------------------------------------------------

class ValidationError(QuantFolioError):
    """Erreur générique de validation. Lever directement si aucune
    sous-classe dédiée n'existe pour ce cas précis."""


class NegativeAmountError(ValidationError):
    def __init__(self, montant: float, champ: str = "montant"):
        self.montant = montant
        self.champ = champ
        super().__init__(f"Montant négatif refusé pour '{champ}' : {montant}")


class InvalidFrequencyError(ValidationError):
    def __init__(self, frequence: str):
        self.frequence = frequence
        super().__init__(f"Fréquence invalide : {frequence}")


class InvalidDateError(ValidationError):
    def __init__(self, date_value, raison: str = "date invalide"):
        self.date_value = date_value
        self.raison = raison
        super().__init__(f"Date invalide ({raison}) : {date_value}")


class InvalidDateRangeError(ValidationError):
    """Ex: date de fin antérieure à la date de début."""
    def __init__(self, date_debut, date_fin):
        self.date_debut = date_debut
        self.date_fin = date_fin
        super().__init__(
            f"Plage de dates invalide : début={date_debut} > fin={date_fin}"
        )


class InvalidRateError(ValidationError):
    """Taux (intérêt, inflation, valorisation) hors plage plausible."""
    def __init__(self, taux: float, champ: str = "taux"):
        self.taux = taux
        self.champ = champ
        super().__init__(f"Taux invalide pour '{champ}' : {taux}")


class MissingRequiredFieldError(ValidationError):
    def __init__(self, champ: str, entite: str = ""):
        self.champ = champ
        self.entite = entite
        cible = f" ({entite})" if entite else ""
        super().__init__(f"Champ requis manquant{cible} : {champ}")


class InvalidNatureError(ValidationError):
    """Valeur de `nature` (ClassVar) non reconnue pour un type d'objet."""
    def __init__(self, nature: str, natures_valides: tuple[str, ...] = ()):
        self.nature = nature
        self.natures_valides = natures_valides
        super().__init__(
            f"Nature invalide : {nature} (attendu parmi {natures_valides})"
        )


# ---------------------------------------------------------------------------
# Catégorie 2 — Introuvable (entité inexistante)
# Réaction UI attendue : message "introuvable" / navigation arrière.
# ---------------------------------------------------------------------------

class NotFoundError(QuantFolioError):
    """Erreur générique d'entité introuvable."""


class UtilisateurNotFoundError(NotFoundError):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"Utilisateur {user_id} introuvable")


class ScenarioNotFoundError(NotFoundError):
    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        super().__init__(f"Scénario {scenario_id} introuvable")


class ProfilNotFoundError(NotFoundError):
    def __init__(self, profil_id: str):
        self.profil_id = profil_id
        super().__init__(f"Profil {profil_id} introuvable")


class MetierNotFoundError(NotFoundError):
    def __init__(self, metier_id: str):
        self.metier_id = metier_id
        super().__init__(f"Métier {metier_id} introuvable")


class BanqueNotFoundError(NotFoundError):
    def __init__(self, banque_id: str):
        self.banque_id = banque_id
        super().__init__(f"Banque {banque_id} introuvable")


class CompteBancaireNotFoundError(NotFoundError):
    def __init__(self, compte_id: str):
        self.compte_id = compte_id
        super().__init__(f"Compte bancaire {compte_id} introuvable")


class CreditNotFoundError(NotFoundError):
    def __init__(self, credit_id: str):
        self.credit_id = credit_id
        super().__init__(f"Crédit {credit_id} introuvable")


class InvestissementNotFoundError(NotFoundError):
    def __init__(self, invest_id: str):
        self.invest_id = invest_id
        super().__init__(f"Investissement {invest_id} introuvable")


class RecetteNotFoundError(NotFoundError):
    def __init__(self, recette_id: str):
        self.recette_id = recette_id
        super().__init__(f"Recette {recette_id} introuvable")


class DepenseNotFoundError(NotFoundError):
    def __init__(self, depense_id: str):
        self.depense_id = depense_id
        super().__init__(f"Dépense {depense_id} introuvable")


# ---------------------------------------------------------------------------
# Catégorie 3 — Règles métier / cohérence relationnelle
# Réaction UI attendue : message explicatif, généralement bloquant une action.
# Distincte de ValidationError car il ne s'agit pas d'un champ mal rempli,
# mais d'une règle qui dépend de l'état d'autres entités.
# ---------------------------------------------------------------------------

class BusinessRuleError(QuantFolioError):
    """Erreur générique de règle métier. Lever directement si aucune
    sous-classe dédiée n'existe pour ce cas précis."""


class CreditSansProjetError(BusinessRuleError):
    """Un Crédit doit toujours référencer un projet_id (entité faible)."""
    def __init__(self, credit_id: str | None = None):
        self.credit_id = credit_id
        super().__init__(
            f"Impossible de créer un Crédit sans projet_id associé "
            f"(credit_id={credit_id})"
        )


class ProjetDejaFinaliseError(BusinessRuleError):
    def __init__(self, projet_id: str, mode_financement: str):
        self.projet_id = projet_id
        self.mode_financement = mode_financement
        super().__init__(
            f"Le projet {projet_id} est déjà finalisé "
            f"(mode_financement={mode_financement})"
        )


class SoldeInsuffisantError(BusinessRuleError):
    def __init__(self, compte_id: str, solde: float, montant_demande: float):
        self.compte_id = compte_id
        self.solde = solde
        self.montant_demande = montant_demande
        super().__init__(
            f"Solde insuffisant sur le compte {compte_id} : "
            f"{solde} < {montant_demande}"
        )


class ScenarioVerrouilleError(BusinessRuleError):
    """Ex: scénario archivé/figé qu'on tente de modifier."""
    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        super().__init__(f"Le scénario {scenario_id} est verrouillé en écriture")


class EntiteDejaExistanteError(BusinessRuleError):
    """Ex: tentative de créer un compte utilisateur avec un identifiant/email
    déjà pris."""
    def __init__(self, entite: str, identifiant: str):
        self.entite = entite
        self.identifiant = identifiant
        super().__init__(f"{entite} déjà existant : {identifiant}")


# ---------------------------------------------------------------------------
# Catégorie 4 — Intégrité / système
# Réaction UI attendue : message générique "une erreur est survenue",
# log complet côté dev. Ne jamais afficher le détail technique brut à
# l'utilisateur final.
# ---------------------------------------------------------------------------

class IntegrityError(QuantFolioError):
    """Erreur de cohérence des données de persistance (colonne manquante,
    feuille corrompue, schéma inattendu)."""


class MissingColumnError(IntegrityError):
    def __init__(self, colonne: str, feuille: str = ""):
        self.colonne = colonne
        self.feuille = feuille
        cible = f" dans la feuille '{feuille}'" if feuille else ""
        super().__init__(f"Colonne manquante{cible} : {colonne}")


class CorruptedSheetError(IntegrityError):
    def __init__(self, feuille: str, detail: str = ""):
        self.feuille = feuille
        self.detail = detail
        super().__init__(f"Feuille corrompue : {feuille}. {detail}")


class UnknownEntityTypeError(IntegrityError):
    """Ex: `nature` inconnu lors de la lecture générique d'Investissement."""
    def __init__(self, type_value: str, entite: str = ""):
        self.type_value = type_value
        self.entite = entite
        super().__init__(f"Type inconnu pour {entite or 'entité'} : {type_value}")


# ---------------------------------------------------------------------------
# Catégorie 5 — Concurrence / écriture (pertinent avant migration SQLite,
# tant que l'atomicité multi-écriture est gérée à la main dans les services)
# Réaction UI attendue : proposer de réessayer / recharger les données.
# ---------------------------------------------------------------------------

class ConcurrencyError(QuantFolioError):
    """Erreur liée à un accès concurrent ou une écriture partielle."""


class PartialWriteError(ConcurrencyError):
    """Une opération multi-feuilles a échoué après une écriture partielle
    (ex: Credit créé mais mode_financement non mis à jour)."""
    def __init__(self, operation: str, etapes_completees: list[str]):
        self.operation = operation
        self.etapes_completees = etapes_completees
        super().__init__(
            f"Écriture partielle lors de '{operation}'. "
            f"Étapes complétées : {etapes_completees}"
        )


class FileLockedError(ConcurrencyError):
    def __init__(self, fichier: str):
        self.fichier = fichier
        super().__init__(f"Fichier verrouillé (probablement ouvert dans Excel) : {fichier}")
        
# ---------------------------------------------------------------------------
# Catégorie 6 — Authentification
# Réaction UI attendue : message générique sur le formulaire de connexion,
# sans révéler si c'est le nom d'utilisateur ou le mot de passe qui est en
# cause (évite l'énumération de comptes existants).
# ---------------------------------------------------------------------------

class AuthenticationError(QuantFolioError):
    """Erreur générique d'authentification."""


class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        super().__init__("Nom d'utilisateur ou mot de passe incorrect")