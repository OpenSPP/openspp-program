# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EntitlementManager(models.Model):
    _inherit = "g2p.program.entitlement.manager"
    _description = "In-Kind Entitlement Manager"

    @api.model
    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = ("g2p.program.entitlement.manager.inkind", "In-Kind")
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class G2PInKindEntitlementManager(models.Model):
    _name = "g2p.program.entitlement.manager.inkind"
    _inherit = [
        "g2p.base.program.entitlement.manager",
        "g2p.manager.source.mixin",
    ]
    _description = "In-Kind Entitlement Manager"

    # Set to False so that the UI will not display the payment management components
    IS_CASH_ENTITLEMENT = False

    @api.model
    def _default_warehouse_id(self):
        return self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

    # In-Kind Entitlement Manager
    evaluate_single_item = fields.Boolean("Evaluate one item", default=False)
    entitlement_item_ids = fields.One2many(
        "g2p.program.entitlement.manager.inkind.item",
        "entitlement_id",
        "Entitlement Items",
    )

    # Inventory integration fields
    manage_inventory = fields.Boolean(default=False)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        default=_default_warehouse_id,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company", string="Company", related="program_id.company_id"
    )

    # Group able to validate the payment
    # Todo: Create a record rule for payment_validation_group
    entitlement_validation_group_id = fields.Many2one(
        "res.groups", string="Entitlement Validation Group"
    )

    def prepare_entitlements(self, cycle, beneficiaries):
        if not self.entitlement_item_ids:
            raise UserError(
                _("There are no items entered for this entitlement manager.")
            )

        # Prepare Inventory
        if self.manage_inventory:
            # Prepare stock.picking record
            pass

        all_beneficiaries_ids = beneficiaries.mapped("partner_id.id")
        for rec in self.entitlement_item_ids:

            if rec.condition:
                # Filter res.partner based on entitlement condition and get ids
                domain = [("id", "in", all_beneficiaries_ids)]
                domain += self._safe_eval(rec.condition)
                beneficiaries_ids = self.env["res.partner"].search(domain).ids

                # Check if single evaluation
                if self.evaluate_single_item:
                    # Remove beneficiaries_ids from all_beneficiaries_ids
                    for bid in beneficiaries_ids:
                        if bid in all_beneficiaries_ids:
                            all_beneficiaries_ids.remove(bid)
            else:
                beneficiaries_ids = all_beneficiaries_ids

            # Get beneficiaries_with_entitlements to prevent generating
            # the same entitlement for beneficiaries
            beneficiaries_with_entitlements = (
                self.env["g2p.entitlement"]
                .search(
                    [
                        ("cycle_id", "=", cycle.id),
                        ("partner_id", "in", beneficiaries_ids),
                        ("inkind_item_id", "=", rec.id),
                    ]
                )
                .mapped("partner_id.id")
            )
            entitlements_to_create = [
                beneficiaries_id
                for beneficiaries_id in beneficiaries_ids
                if beneficiaries_id not in beneficiaries_with_entitlements
            ]

            entitlement_start_validity = cycle.start_date
            entitlement_end_validity = cycle.end_date

            beneficiaries_with_entitlements_to_create = self.env["res.partner"].browse(
                entitlements_to_create
            )

            entitlements = []

            for beneficiary_id in beneficiaries_with_entitlements_to_create:
                multiplier = 1
                if rec.multiplier_field:
                    # Get the multiplier value from multiplier_field else return the default multiplier=1
                    multiplier = beneficiary_id.mapped(rec.multiplier_field.name)
                    if multiplier:
                        multiplier = multiplier[0] or 1
                if rec.max_multiplier > 0 and multiplier > rec.max_multiplier:
                    multiplier = rec.max_multiplier
                qty = multiplier * rec.qty

                entitlements.append(
                    {
                        "cycle_id": cycle.id,
                        "partner_id": beneficiary_id.id,
                        "initial_amount": 0.0,
                        "product_id": rec.product_id.id,
                        "qty": qty,
                        "uom_id": rec.uom_id.id,
                        "manage_inventory": self.manage_inventory,
                        "warehouse_id": self.warehouse_id
                        and self.warehouse_id.id
                        or None,
                        "inkind_item_id": rec.id,
                        "state": "draft",
                        "is_cash_entitlement": False,
                        "valid_from": entitlement_start_validity,
                        "valid_until": entitlement_end_validity,
                    }
                )
            self.env["g2p.entitlement"].create(entitlements)

    def validate_entitlements(self, cycle, cycle_memberships):
        # TODO: Change the status of the entitlements to `validated` for this members.
        # move the funds from the program's wallet to the wallet of each Beneficiary that are validated
        pass

    def approve_entitlements(self, entitlements):
        state_err = 0
        message = ""
        sw = 0
        for rec in entitlements:
            if rec.state in ("draft", "pending_validation"):
                # _logger.info("DEBUG: _process_noncash_base_entitlement: rec: %s", rec)
                if rec.manage_inventory:
                    rec._action_launch_stock_rule()
                rec.update(
                    {
                        "state": "approved",
                        "date_approved": fields.Date.today(),
                    }
                )
            else:
                state_err += 1
                if sw == 0:
                    sw = 1
                    message = _(
                        "Entitlement State Error! Entitlements not in 'pending validation' state:\n"
                    )
                message += _("Program: %(prg)s, Beneficiary: %(partner)s.\n") % {
                    "prg": rec.cycle_id.program_id.name,
                    "partner": rec.partner_id.name,
                }

        return (state_err, message)

    def open_entitlements_form(self, cycle):
        self.ensure_one()
        action = {
            "name": _("Cycle In-Kind Entitlements"),
            "type": "ir.actions.act_window",
            "res_model": "g2p.entitlement",
            "context": {
                "create": False,
                "default_cycle_id": cycle.id,
                # "search_default_approved_state": 1,
            },
            "view_mode": "list,form",
            "views": [
                [self.env.ref("g2p_programs.view_entitlement_tree").id, "tree"],
                [
                    self.env.ref(
                        "spp_entitlement_in_kind.view_entitlement_inkind_form"
                    ).id,
                    "form",
                ],
            ],
            "domain": [("cycle_id", "=", cycle.id)],
        }
        return action

    def open_entitlement_form(self, rec):
        return {
            "name": "Entitlement",
            "view_mode": "form",
            "res_model": "g2p.entitlement",
            "res_id": rec.id,
            "view_id": self.env.ref(
                "spp_entitlement_in_kind.view_entitlement_inkind_form"
            ).id,
            "type": "ir.actions.act_window",
            "target": "new",
        }


class G2PInKindEntitlementItem(models.Model):
    _name = "g2p.program.entitlement.manager.inkind.item"
    _description = "In-Kind Entitlement Manager Items"
    _order = "sequence,id"

    sequence = fields.Integer(default=1000)
    entitlement_id = fields.Many2one(
        "g2p.program.entitlement.manager.inkind", "In-kind Entitlement", required=True
    )

    product_id = fields.Many2one(
        "product.product", "Product", domain=[("type", "=", "product")], required=True
    )

    # non-mandatory field to store a domain that is used to verify if this item is valid for a beneficiary
    # For example, it could be: [('is_woman_headed_household, '=', True)]
    # If the condition is not met, this calculation is not used
    condition = fields.Char("Condition Domain")

    # any field that is an integer of `res.partner`
    # It could be the number of members, children, elderly, or any other metrics.
    # if no multiplier field is set, it is considered as 1.
    multiplier_field = fields.Many2one(
        "ir.model.fields",
        "Multiplier",
        domain=[("model_id.model", "=", "res.partner"), ("ttype", "=", "integer")],
    )
    max_multiplier = fields.Integer(
        default=0,
        string="Maximum number",
        help="0 means no limit",
    )

    qty = fields.Integer("QTY", default=1, required=True)
    uom_id = fields.Many2one(
        "uom.uom", "Unit of Measure", related="product_id.uom_id", store=True
    )
