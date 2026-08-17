from datetime import date
from utils.finance_format import euro
from domain.errors import BusinessRuleError, NotFoundError
from domain.enums import DependentType
from .domain_services import (CreditService, 
                              InvestissementService, 
                              CompteBancaireService, 
                              DepenseService, 
                              RecetteService, 
                              MetierService)
from .transactionService import TransactionService

class PatrimoineService:
    """Cross-entity deletion policy: bilateral Crédit <-> Investissement coupling,
    and downstream dependency detection via simulated affordability."""

    def __init__(self, credit_service : CreditService, invest_service : InvestissementService, cb_service : CompteBancaireService,
                 transaction_service :TransactionService, depense_service : DepenseService, recette_service : RecetteService, metier_service : MetierService):
        self.credit_service = credit_service
        self.invest_service = invest_service
        self.cb_service = cb_service
        self.transaction_service = transaction_service
        self.depense_service = depense_service
        self.recette_service = recette_service
        self.metier_service = metier_service

    # ------------------------------------------------------------------
    # DETECTION
    # ------------------------------------------------------------------
    def propagate_downstream(self, scenario, root_entity):
        root_id = root_entity.id
        root_type = root_entity.get_dependent_type()

        if root_type in (DependentType.DEPENSE, DependentType.RECETTE):
            self._guard_standalone(root_entity)

        deletion_date = self._get_origination_date(root_id, root_type)

        excluded_ids = {root_id}
        visited_ids = {root_id}
        dependents = [(root_id, root_type)]

        for dep_id, dep_type in self._resolve_pair(root_id, root_type):
            excluded_ids.add(dep_id)
            visited_ids.add(dep_id)
            dependents.append((dep_id, dep_type))
            for child_id in self._resolve_generated_children(dep_id, dep_type):
                excluded_ids.add(child_id)

        for child_id in self._resolve_generated_children(root_id, root_type):
            excluded_ids.add(child_id)
                     
        result = self.next_dated_entity_from(scenario.id, deletion_date, visited_ids)
        while result is not None:
            entity, entity_type = result
            visited_ids.add(entity.id)

            if not self.passes_both_legs(scenario, entity, excluded_ids):
                dependents.append((entity.id, entity_type))
                excluded_ids.add(entity.id)

                for dep_id, dep_type in self._resolve_pair(entity.id, entity_type):
                    excluded_ids.add(dep_id)
                    visited_ids.add(dep_id)
                    dependents.append((dep_id, dep_type))
                    for child_id in self._resolve_generated_children(dep_id, dep_type):
                        excluded_ids.add(child_id)
                            
                for child_id in self._resolve_generated_children(entity.id, entity_type):
                    excluded_ids.add(child_id)

            current_date = self._get_origination_date(entity.id, entity_type)
            result = self.next_dated_entity_from(scenario.id, current_date, visited_ids)

        return dependents, excluded_ids
       
    def next_dated_entity_from(self, scenario_id: int, date_ref: date,
                               excluded_ids: set) -> tuple | None:
        """P.P.S.-only lookup: Investissement, Crédit, standalone Dépense.
        Returns the nearest one on/after date_ref, skipping excluded_ids."""
        candidates = []

        for repo in self.invest_service.repos.values():
            for inv in repo.get_by_({"ID SCENARIO": scenario_id}) or []:
                if inv.id not in excluded_ids and inv.date_in >= date_ref:
                    candidates.append((inv, DependentType.INVESTISSEMENT, inv.date_in))

        for cr in self.credit_service.get_all_credits_from_scenario(scenario_id) or []:
            if cr.id not in excluded_ids and cr.debut >= date_ref:
                candidates.append((cr, DependentType.CREDIT, cr.debut))

        for dep in self.depense_service.get_by_scenario(scenario_id) or []:
            if dep.id_source is not None and dep.nature != "Locataires":
                continue  # levitating: never an independent node
            if dep.id not in excluded_ids and dep.date_in >= date_ref:
                candidates.append((dep, DependentType.DEPENSE, dep.date_in))
        if not candidates:
            return None

        entity, entity_type, _ = min(candidates, key=lambda c: c[2])
        return entity, entity_type

    def passes_both_legs(self, scenario, entity, excluded_ids: set) -> bool:
        entity_type = entity.get_dependent_type()
        date_check = self._get_origination_date(entity.id, entity_type)

        self_and_pair = {entity.id}
        for dep_id, dep_type in self._resolve_pair(entity.id, entity_type):
            self_and_pair.add(dep_id)

        if entity_type == DependentType.CREDIT:
            capacite = self.credit_service.capacite_emprunt(
                id_scenario=scenario.id,
                date_credit=date_check,
                excluded_ids=excluded_ids | self_and_pair
            )
            return capacite >= entity.mensualite_constante

        # INVESTISSEMENT or DEPENSE — cash leg only
        compte_id = entity.id_compte
        montant_requis = self._get_montant_requis(entity, entity_type)

        solde_avec = self.cb_service.solde_from_cb(
            date_in_scenario=scenario.date_in, cbs_id=compte_id,
            date_valide=date_check, excluded_ids=excluded_ids | self_and_pair
        ).solde

        solde_sans = self.cb_service.solde_from_cb(
            date_in_scenario=scenario.date_in, cbs_id=compte_id,
            date_valide=date_check, excluded_ids=self_and_pair
        ).solde

        return solde_avec >= montant_requis or solde_sans < montant_requis    
    # ------------------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------------------

    def delete_financement(self,
                           list_to_suppress: list[tuple[int, DependentType]]):
        """Pure executor. Trusts the list as confirmed — runs no detection."""
        for entity_id, entity_type in list_to_suppress:
            self._suppress_one(entity_id, entity_type)

    def _suppress_one(self, entity_id: int, entity_type: DependentType):
        if entity_type == DependentType.INVESTISSEMENT:
            self.invest_service.delete_invest(entity_id)
        elif entity_type == DependentType.CREDIT:
            self.credit_service.delete_credit(entity_id)
        elif entity_type == DependentType.METIER:
            self.metier_service.delete(entity_id)
        elif entity_type == DependentType.DEPENSE:
            self._guard_standalone(self.depense_service.get_depense_by_id(entity_id))
            self.depense_service.delete_depense(entity_id)
        elif entity_type == DependentType.RECETTE:
            self._guard_standalone(self.recette_service.get_recette_by_id(entity_id))
            self.recette_service.delete_recette(entity_id)
        else:
            raise ValueError(f"Unhandled entity type: {entity_type}")
        
    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _resolve_pair(self, entity_id, entity_type) -> list[tuple[int, DependentType]]:
        """Genuine dependents — entities delete_financement must explicitly delete.
        Investissement<->Crédit, Dépense<->Recette (transaction-linked)."""
        if entity_type == DependentType.INVESTISSEMENT:
            invest = self.invest_service.get_by_id(entity_id)
            credit_id = getattr(invest, "id_credit", None)
            return [(credit_id, DependentType.CREDIT)] if credit_id is not None else []

        if entity_type == DependentType.CREDIT:
            credit = self.credit_service.get_credit_by_id(entity_id)
            invest_id = getattr(credit, "id_source", None)
            return [(invest_id, DependentType.INVESTISSEMENT)] if invest_id is not None else []

        if entity_type == DependentType.DEPENSE:
            depense = self.depense_service.get_depense_by_id(entity_id)
            id_transaction = getattr(depense, "id_transaction", None)
            if id_transaction is not None:
                recette = self.recette_service.get_by_criterias({"ID TRANSACTION": id_transaction})
                if recette:
                    return [(recette[0].id, DependentType.RECETTE)]
            return []

        if entity_type == DependentType.RECETTE:
            recette = self.recette_service.get_recette_by_id(entity_id)
            id_transaction = getattr(recette, "id_transaction", None)
            if id_transaction is not None:
                depense = self.depense_service.get_by_criterias({"ID TRANSACTION": id_transaction})
                if depense:
                    return [(depense[0].id, DependentType.DEPENSE)]
            return []

        return []

    def _resolve_generated_children(self, entity_id, entity_type) -> list[int]:
        """Generated children — never deleted directly by PatrimoineService, only
        virtually excluded, since their own generator cascades their real deletion."""
        if entity_type == DependentType.METIER:
            ids = [d.id for d in (self.depense_service.get_by_criterias({"ID SOURCE": entity_id}) or [])]
            ids += [r.id for r in (self.recette_service.get_by_criterias({"ID SOURCE": entity_id}) or [])]
            return ids

        if entity_type == DependentType.CREDIT:
            ids = [d.id for d in (self.depense_service.get_by_criterias({"ID SOURCE": entity_id}) or [])]
            ids += [r.id for r in (self.recette_service.get_by_criterias({"ID SOURCE": entity_id}) or [])]
            return ids

        if entity_type == DependentType.INVESTISSEMENT:
            ids = [d.id for d in (self.depense_service.get_by_criterias({"ID SOURCE": entity_id}) or [])]
            ids += [r.id for r in (self.recette_service.get_by_criterias({"ID SOURCE": entity_id}) or [])]
            return ids

        return []    
    
    def _get_origination_date(self, entity_id: int, entity_type: DependentType) -> date:
        if entity_type == DependentType.INVESTISSEMENT:
            return self.invest_service.get_by_id(entity_id).date_in
        if entity_type == DependentType.CREDIT:
            return self.credit_service.get_credit_by_id(entity_id).debut
        if entity_type == DependentType.DEPENSE:
            return self.depense_service.get_depense_by_id(entity_id).date_in
        if entity_type == DependentType.RECETTE:
            return self.recette_service.get_recette_by_id(entity_id).date_in
        if entity_type == DependentType.METIER:
            return self.metier_service.get_metier_by_id(entity_id).date_in
        raise ValueError(f"No origination date for type: {entity_type}")

    def _get_montant_requis(self, entity, entity_type: DependentType) -> float:
        if entity_type == DependentType.INVESTISSEMENT:
            return entity.apport_personnel
        if entity_type == DependentType.DEPENSE:
            return entity.montant
        raise ValueError(f"No required amount for type: {entity_type}")

    def _guard_standalone(self, entity):
        """Levitating entities are never independently deletable."""
        if entity is None:
            raise NotFoundError("Entity not found")
        if getattr(entity, "id_source", None) is not None and getattr(entity,"nature") != "Locataires":
            raise BusinessRuleError(
                "Cannot delete a generated entity directly — delete its source instead."
            )
            
    def _infer_type_from_id(self, entity_id: int) -> DependentType:
        leading_digit = int(str(entity_id)[0])

        mapping = {
            7: DependentType.INVESTISSEMENT,
            4: DependentType.CREDIT,
            5: DependentType.METIER,
            8: DependentType.DEPENSE,
            9: DependentType.RECETTE,
        }

        entity_type = mapping.get(leading_digit)
        if entity_type is None:
            raise ValueError(f"Cannot infer entity type from id: {entity_id}")
        return entity_type


    def resolve_label(self, entity_id: int, entity_type: DependentType | None = None) -> str:
        if entity_type is None:
            entity_type = self._infer_type_from_id(entity_id)

        if entity_type == DependentType.INVESTISSEMENT:
            inv = self.invest_service.get_by_id(entity_id)
            return f"{inv.type} — {inv.titre} {inv.prix_achat} ({inv.date_in.strftime('%d/%m/%Y')})"
        if entity_type == DependentType.CREDIT:
            cr = self.credit_service.get_credit_by_id(entity_id)
            return f"Crédit — {cr.montant}€ (attribué {cr.debut.strftime('%d/%m/%Y')})"
        if entity_type == DependentType.METIER:
            met = self.metier_service.get_metier_by_id(entity_id)
            return f"Métier — {met.intitule_métier} ({euro(met.annuel_net)})"
        if entity_type == DependentType.DEPENSE:
            dep = self.depense_service.get_depense_by_id(entity_id)
            return f"Dépense — {dep.intitule} ({dep.montant}€)"
        if entity_type == DependentType.RECETTE:
            rec = self.recette_service.get_recette_by_id(entity_id)
            return f"Recette — {rec.intitule} ({rec.montant}€)"
        return f"{entity_type.value} #{entity_id}"