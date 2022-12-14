# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.g2p_programs.models.constants import MANAGER_PROGRAM


@freeze_time("2022-12-02")
@tagged("post_install", "-at_install")
class DefaultProgramManagerTest(TransactionCase):
    RRULE_TYPE = "yearly"
    CYCLE_DURATION = 2

    @classmethod
    def setUpClass(cls):
        super(DefaultProgramManagerTest, cls).setUpClass()

        program_wizard = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "My test program",
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
                "rrule_type": cls.RRULE_TYPE,
                "cycle_duration": cls.CYCLE_DURATION,
            }
        )

        result = program_wizard.create_program()

        program = cls.env[result["res_model"]].browse(result["res_id"])
        cls.program_manager = program.get_manager(MANAGER_PROGRAM)

    def test_new_cycle_success(self):
        date_now = datetime.now()
        first_cycle = self.program_manager.new_cycle()
        self.assertIsNotNone(first_cycle)

        second_cycle = self.program_manager.new_cycle()
        self.assertIsNotNone(second_cycle)

        self.assertNotEqual(first_cycle, second_cycle)

        self.assertEqual(first_cycle.start_date, date_now.date())
        self.assertEqual(
            first_cycle.end_date,
            date_now.date() + relativedelta(years=self.CYCLE_DURATION),
        )

        self.assertEqual(second_cycle.start_date, first_cycle.end_date)
        self.assertEqual(
            second_cycle.end_date,
            first_cycle.end_date + relativedelta(years=self.CYCLE_DURATION),
        )
