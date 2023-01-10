# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.g2p_programs.models.constants import MANAGER_CYCLE


@freeze_time("2022-12-02")
@tagged("post_install", "-at_install")
class DefaultCycleManagerTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(DefaultCycleManagerTest, cls).setUpClass()

        program_wizard = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "My test program",
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
                "rrule_type": "daily",
                "cycle_duration": 30,
            }
        )

        result = program_wizard.create_program()

        program = cls.env[result["res_model"]].browse(result["res_id"])
        cls.cycle_manager = program.get_manager(MANAGER_CYCLE)

    def test_new_cycle_daily(self):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=self.cycle_manager.cycle_duration)
        sequence = 1

        cycle = self.cycle_manager.new_cycle("Cycle 1", start_date, sequence)

        self.assertEqual(cycle.start_date, start_date.date())
        self.assertEqual(cycle.end_date, end_date.date())
        self.assertEqual(cycle.sequence, sequence)

    def test_new_cycle_yearly(self):

        self.cycle_manager.rrule_type = "yearly"
        self.cycle_manager.cycle_duration = 1

        start_date = datetime.now()
        end_date = start_date + relativedelta(years=self.cycle_manager.cycle_duration)
        sequence = 2

        cycle = self.cycle_manager.new_cycle("Cycle 1", start_date, sequence)

        self.assertEqual(cycle.start_date, start_date.date())
        self.assertEqual(cycle.end_date, end_date.date())
        self.assertEqual(cycle.sequence, sequence)

    def test_new_cycle_monthly(self):

        self.cycle_manager.rrule_type = "monthly"
        self.cycle_manager.cycle_duration = 1

        start_date = datetime.now()
        end_date = start_date + relativedelta(months=self.cycle_manager.cycle_duration)
        sequence = 3

        cycle = self.cycle_manager.new_cycle("Cycle 1", start_date, sequence)

        self.assertEqual(cycle.start_date, start_date.date())
        self.assertEqual(cycle.end_date, end_date.date())
        self.assertEqual(cycle.sequence, sequence)

    def test_new_cycle_weekly(self):

        self.cycle_manager.rrule_type = "weekly"
        self.cycle_manager.cycle_duration = 1

        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=self.cycle_manager.cycle_duration)
        sequence = 3

        cycle = self.cycle_manager.new_cycle("Cycle 1", start_date, sequence)

        self.assertEqual(cycle.start_date, start_date.date())
        self.assertEqual(cycle.end_date, end_date.date())
        self.assertEqual(cycle.sequence, sequence)
