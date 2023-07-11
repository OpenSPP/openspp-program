from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    beneficiaries_filtering_mechanism = fields.Selection(
        selection=[
            ("1", "Satisfy One Eligibility Manager"),
            ("2", "Satisfy All Eligibility Managers"),
        ],
        default="1",
        required=True,
        config_parameter="spp_programs.beneficiaries_filtering_mechanism",
        help="Filtering Beneficiaries Mechanism:\n"
        "1. Satisfy One Eligibility Manager in Program\n"
        "2. Satisfy All Eligibility Managers in Program [not yet implemented!]\n",
    )

    @api.constrains("beneficiaries_filtering_mechanism")
    def _check_beneficiaries_filtering_mechanism(self):
        if self.beneficiaries_filtering_mechanism == "2":
            raise ValidationError(
                _(
                    "Filtering beneficiaries by all eligibility "
                    "managers is not yet completely developed!"
                )
            )
