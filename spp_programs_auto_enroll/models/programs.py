# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, models, fields
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class CustomG2PProgram(models.Model):
    _inherit = "g2p.program"

    auto_enroll = fields.Boolean(default=False)
    auto_enroll_status = fields.Selection(
        selection=[("draft", "Draft"), ("enrolled", "Enrolled")], default="draft"
    )
    last_updated_date = fields.Datetime()

    def cron_auto_enroll(self):
        future_last_updated_date = fields.Datetime.now() - timedelta(minutes=5)
        programs = self.env["g2p.program"].search([("state", "=", "active"),
                                                   ("auto_enroll", "=", True)])
        if programs:
            for program in programs:
                program.import_eligible_registrants()
                if program.auto_enroll_status == "enrolled":
                    program.enroll_eligible_registrants()

                program.last_updated_date = future_last_updated_date
        return

