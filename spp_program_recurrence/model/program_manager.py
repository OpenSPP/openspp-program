# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

from odoo import models

from odoo.addons.g2p_programs.models.constants import MANAGER_CYCLE

_logger = logging.getLogger(__name__)


class DefaultProgramManager(models.Model):
    """
    Inherit g2p.program.manager.default model to overwrite below function/s:
    new_cycle
    """

    _inherit = "g2p.program.manager.default"

    def new_cycle(self):
        """
        Overwrite this function of model g2p.program.manager.default to modify the
        start date passed as an argument in the new_cycle parameter

        Create the next cycle of the program
        Returns:
            cycle: the newly created cycle
        """
        for rec in self:
            cycles = self.env["g2p.cycle"].search(
                [("program_id", "=", rec.program_id.id)]
            )
            new_cycle = None
            _logger.info("cycles: %s", cycles)
            cm = rec.program_id.get_manager(MANAGER_CYCLE)
            if len(cycles) == 0:
                _logger.info("cycle manager: %s", cm)
                new_cycle = cm.new_cycle("Cycle 1", datetime.now(), 1)
            else:
                last_cycle = rec.last_cycle()
                new_sequence = last_cycle.sequence + 1
                new_cycle = cm.new_cycle(
                    f"Cycle {new_sequence}",
                    last_cycle.end_date,
                    new_sequence,
                )

            # Copy the enrolled beneficiaries
            if new_cycle is not None:
                program_beneficiaries = rec.program_id.get_beneficiaries(
                    "enrolled"
                ).mapped("partner_id.id")
                cm.add_beneficiaries(new_cycle, program_beneficiaries, "enrolled")
            return new_cycle
