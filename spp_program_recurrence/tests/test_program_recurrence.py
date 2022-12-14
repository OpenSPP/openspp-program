# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class G2PCreateNewProgramWizTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(G2PCreateNewProgramWizTest, cls).setUpClass()

        cls.program_wizard_1 = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "My program",
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
            }
        )

        cls.program_wizard_2 = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "My program 2",
            }
        )

    def test_create_program_success(self):
        result = self.program_wizard_1.create_program()
        self.assertIsNotNone(result)

    def test_create_program_user_error(self):
        with self.assertRaises(UserError):
            self.program_wizard_2.create_program()
