from odoo import api, models
from odoo.osv.expression import AND


class G2pCycleMembership(models.Model):
    _inherit = "g2p.cycle.membership"

    @api.model
    def filter_valid_enrolled_beneficiaries(self, domain):
        records = self.search(domain)
        cycle = records.cycle_id
        program = cycle.program_id
        final_compliance_criteria_domain = (
            program._get_final_compliance_criteria_domain()
        )
        res = cycle.open_members_form()
        res["views"] = [[False, "list"], [False, "form"]]
        res["domain"] = AND([domain, final_compliance_criteria_domain])
        return res
