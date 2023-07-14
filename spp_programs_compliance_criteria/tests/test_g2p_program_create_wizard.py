from odoo.tests import TransactionCase


class TestG2pProgramCreateWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        create_wiz = self.env["g2p.program.create.wizard"]
        self._test_create_wiz_auto_compliance = create_wiz.create(
            {
                "name": "Prog1",
                "auto_compliance": True,
                "amount_per_cycle": 5.0,
            }
        )
        self._test_create_wiz_non_auto_compliance = create_wiz.create(
            {
                "name": "Prog1",
                "auto_compliance": False,
                "amount_per_cycle": 5.0,
            }
        )

    def test_01_create_program(self):
        res = self._test_create_wiz_auto_compliance.create_program()
        auto_compliance_program = self.env["g2p.program"].browse(res["res_id"])
        self.assertTrue(
            auto_compliance_program.auto_compliance,
            "Program created should have auto_compliance "
            "equals with the create wizard.",
        )

        res = self._test_create_wiz_non_auto_compliance.create_program()
        non_auto_compliance_program = self.env["g2p.program"].browse(res["res_id"])
        self.assertFalse(
            non_auto_compliance_program.auto_compliance,
            "Program created should have auto_compliance "
            "equals with the create wizard.",
        )
