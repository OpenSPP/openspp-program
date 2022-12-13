# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)

# Same value with openg2p_program.g2p_programs.models.constants.MANAGER_CYCLE
MANAGER_CYCLE = 2


class DefaultProgramManager(models.Model):
    _inherit = "g2p.program.manager.default"

    def new_cycle(self):
        """
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
