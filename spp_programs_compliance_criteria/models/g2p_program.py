import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


class G2pProgram(models.Model):
    _inherit = "g2p.program"

    auto_compliance = fields.Boolean(
        string="Automated Compliance",
    )
    ongoing_cycle = fields.Boolean(
        string="On-going Cycle",
        compute="_compute_ongoing_cycle",
        search="_search_ongoing_cycle",
        store=False,
        compute_sudo=True,
    )

    @api.model
    def _get_filtering_mechanism(self):
        filtering_mechanism = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("spp_programs.beneficiaries_filtering_mechanism", "1")
        )
        if filtering_mechanism != "1":
            _logger.warning(
                "Filtering beneficiaries by all eligibility "
                "managers is not yet completely developed!"
            )
            filtering_mechanism = "1"
        return filtering_mechanism

    @api.depends(
        "cycle_ids",
        "cycle_ids.state",
        "cycle_ids.start_date",
        "cycle_ids.end_date",
    )
    def _compute_ongoing_cycle(self):
        for rec in self:
            ongoing_cycle = False
            for cycle in rec.cycle_ids:
                if cycle.state != "approved":
                    continue
                if cycle.start_date <= fields.Date.today() <= cycle.end_date:
                    ongoing_cycle = True
                    break
            rec.ongoing_cycle = ongoing_cycle

    def _search_ongoing_cycle(self, operator, value):
        if operator not in ["=", "!="] or not isinstance(value, bool):
            raise ValidationError(_("Operation not supported!"))
        if operator != "=":
            value = not value
        self._cr.execute(
            """
                SELECT
                    DISTINCT program_id
                FROM
                    g2p_cycle
                WHERE
                    state = 'approved'
                    AND start_date <= CURRENT_DATE
                    AND CURRENT_DATE <= end_date;
            """
        )
        res_ids = [r["program_id"] for r in self._cr.dictfetchall()]
        opr = "in" if value else "not in"
        return [("id", opr, res_ids)]

    def _get_final_compliance_criteria_domain(self, condition="in"):
        if condition not in ("in", "not in"):
            condition = "in"
            _logger.warning(
                "_get_final_compliance_criteria_domain is "
                "called with non-supported condition!"
            )
        self.ensure_one()
        filtering_mechanism = self._get_filtering_mechanism()
        operator = OR if filtering_mechanism == "1" else AND
        final_domain = []
        for manager in self.eligibility_managers:
            final_domain.append(manager.manager_ref_id._prepare_eligible_domain())
        final_domain = operator(final_domain)
        registrant_ids = self.env["res.partner"].search(final_domain).ids
        return [["partner_id", condition, registrant_ids]]

    @api.model
    def compliance_criteria(self):
        records = self.search(
            [
                ("auto_compliance", "=", True),
                ("state", "=", "active"),
            ]
        )
        for rec in records:
            rec.with_delay()._compliance_criteria()

    def _compliance_criteria(self):
        self.ensure_one()
        compliance_criteria_domain = self._get_final_compliance_criteria_domain(
            condition="not in"
        )
        beneficiaries_to_paused = (
            self.env["g2p.program_membership"]
            .sudo()
            .search(
                AND(
                    [
                        compliance_criteria_domain,
                        [
                            ["program_id", "=", self.id],
                            ["state", "=", "enrolled"],
                        ],
                    ]
                )
            )
        )
        beneficiaries_to_paused.write({"state": "paused"})
        ongoing_cycles = self.cycle_ids.filtered(
            lambda cycle: fields.Date.today() <= cycle.end_date
            and cycle.state in ["draft", "to_approve"]
        )
        cycle_beneficiaries_to_paused = (
            self.env["g2p.cycle.membership"]
            .sudo()
            .search(
                AND(
                    [
                        compliance_criteria_domain,
                        [
                            ["cycle_id", "in", ongoing_cycles.ids],
                            ["state", "=", "enrolled"],
                        ],
                    ]
                )
            )
        )
        cycle_beneficiaries_to_paused.write({"state": "paused"})
