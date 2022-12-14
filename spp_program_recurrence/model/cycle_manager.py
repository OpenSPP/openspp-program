# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models

from odoo.addons.calendar.models.calendar_recurrence import RRULE_TYPE_SELECTION

_logger = logging.getLogger(__name__)


class DefaultCycleManager(models.Model):
    """
    Inherits the g2p.cycle.manager.default model to add below field/s:
    rrule_type

    to overwrite function/s:
    new_cycle
    """

    _inherit = "g2p.cycle.manager.default"

    rrule_type = fields.Selection(
        RRULE_TYPE_SELECTION,
        string="Recurrence",
        default="daily",
        help="Let the event automatically repeat at that interval",
        readonly=False,
    )

    def new_cycle(self, name: str, new_start_date: date, sequence: int):
        """
        Create a cycle record for cycle manager

        Overwrite this function of model g2p.cycle.manager.default to modify the
        end date based on the rrule_type value

        :param str name: Name of the cycle.
        :param datetime new_start_date: start date of the cycle.
        :param int sequence: number of sequnce of a cycle per program
        :return: record of g2p.cycle
        :rtype: g2p.cycle object

        :example:

        >>> name = "Cycle 1"
        >>> start_date = datetime.now()
        >>> sequence = 1
        >>> cycle = self.new_cycle(name, start_date, sequence)

        """
        _logger.info("Creating new cycle for program %s", self.program_id.name)
        _logger.info("New start date: %s", new_start_date)

        for rec in self:
            if rec.rrule_type == "daily":
                end_date = new_start_date + timedelta(days=rec.cycle_duration)
            elif rec.rrule_type == "yearly":
                end_date = new_start_date + relativedelta(years=rec.cycle_duration)
            elif rec.rrule_type == "monthly":
                end_date = new_start_date + relativedelta(months=rec.cycle_duration)
            else:
                end_date = new_start_date + timedelta(weeks=rec.cycle_duration)

            cycle = self.env["g2p.cycle"].create(
                {
                    "program_id": rec.program_id.id,
                    "name": name,
                    "state": "draft",
                    "sequence": sequence,
                    "start_date": new_start_date,
                    "end_date": end_date,
                }
            )
            _logger.info("New cycle created: %s", cycle.name)
            return cycle
