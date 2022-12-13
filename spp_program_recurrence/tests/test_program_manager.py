# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.g2p_programs.models.constants import MANAGER_PROGRAM


@tagged("post_install", "-at_install")
class DefaultProgramManagerTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(DefaultProgramManagerTest, cls).setUpClass()

        program_wizard = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "My test program",
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
            }
        )

        result = program_wizard.create_program()

        program = cls.env[result["res_model"]].browse(result["res_id"])
        cls.program_manager = program.get_manager(MANAGER_PROGRAM)

    def test__method__new_cycle__success(self):
        first_cycle = self.program_manager.new_cycle()
        self.assertIsNotNone(first_cycle)

        second_cycle = self.program_manager.new_cycle()
        self.assertIsNotNone(second_cycle)

        self.assertNotEqual(first_cycle, second_cycle)
