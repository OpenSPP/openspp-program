from odoo import fields, models


class G2pProgramCreateWizard(models.TransientModel):
    _inherit = "g2p.program.create.wizard"

    auto_compliance = fields.Boolean(
        string="Automated Compliance",
        default=True,
    )

    def create_program(self):
        action = super().create_program()
        model = action.get("res_model")
        _id = action.get("res_id")
        if not all([model, _id]):
            return action
        program = self.env[model].browse(_id)
        program.write(
            {
                "auto_compliance": self.auto_compliance,
            }
        )
        return action
