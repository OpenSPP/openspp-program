from odoo import api, models
from odoo.osv.expression import AND


class G2pProgramMembership(models.Model):
    _inherit = "g2p.program_membership"

    @api.model
    def filter_valid_enrolled_beneficiaries(self, domain):
        records = self.search(domain)
        program = records.program_id
        final_compliance_criteria_domain = (
            program._get_final_compliance_criteria_domain()
        )
        res = program.open_eligible_beneficiaries_form()
        res["views"] = [[False, "list"], [False, "form"]]
        res["domain"] = AND([domain, final_compliance_criteria_domain])
        return res
