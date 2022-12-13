# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, fields, models

from odoo.addons.calendar.models.calendar_recurrence import RRULE_TYPE_SELECTION

_logger = logging.getLogger(__name__)


class G2PCreateNewProgramWiz(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    rrule_type = fields.Selection(
        RRULE_TYPE_SELECTION,
        string="Recurrence",
        default="daily",
        help="Let the event automatically repeat at that interval",
        readonly=False,
        required=True,
    )

    def create_program(self):
        self._check_required_fields()
        for rec in self:
            # Create a new journal for this program
            journal_id = self.create_journal(rec.name, rec.currency_id.id)

            program = self.env["g2p.program"].create(
                {
                    "name": rec.name,
                    "journal_id": journal_id,
                    "target_type": rec.target_type,
                }
            )
            program_id = program.id
            vals = {}

            # Set Default Eligibility Manager settings
            # Add a new record to default eligibility manager model
            def_mgr_obj = "g2p.program_membership.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "eligibility_domain": rec.eligibility_domain,
                }
            )
            # Add a new record to eligibility manager parent model
            man_obj = self.env["g2p.eligibility.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            vals.update({"eligibility_managers": [(4, mgr.id)]})

            # Set Default Cycle Manager settings
            # Add a new record to default cycle manager model
            def_mgr_obj = "g2p.cycle.manager.default"
            def_mgr = self.env[def_mgr_obj].create(
                {
                    "name": "Default",
                    "program_id": program_id,
                    "auto_approve_entitlements": rec.auto_approve_entitlements,
                    "cycle_duration": rec.cycle_duration,
                    "approver_group_id": rec.approver_group_id.id or None,
                    "rrule_type": rec.rrule_type,
                }
            )
            # Add a new record to cycle manager parent model
            man_obj = self.env["g2p.cycle.manager"]
            mgr = man_obj.create(
                {
                    "program_id": program_id,
                    "manager_ref_id": "%s,%s" % (def_mgr_obj, str(def_mgr.id)),
                }
            )
            vals.update({"cycle_managers": [(4, mgr.id)]})

            # Set Default Entitlement Manager
            vals.update(rec._get_entitlement_manager(program_id))

            # Enroll beneficiaries
            if rec.gen_benificiaries == "yes":
                domain = [("is_registrant", "=", True)]
                if rec.target_type == "group":
                    domain += [("is_group", "=", True)]
                else:
                    domain += [("is_group", "=", False)]
                domain += self._safe_eval(rec.eligibility_domain)
                # Filter res.partner and get ids
                partners = self.env["res.partner"].search(domain)
                if partners:
                    partner_vals = []
                    for p in partners.ids:
                        partner_vals.append((0, 0, {"partner_id": p}))
                    vals.update({"program_membership_ids": partner_vals})
                    _logger.info("DEBUG: %s" % partner_vals)

            # Complete the program data
            program.update(vals)

            # Open the newly created program
            action = {
                "name": _("Programs"),
                "type": "ir.actions.act_window",
                "res_model": "g2p.program",
                "view_mode": "form,list",
                "res_id": program_id,
            }
            return action
