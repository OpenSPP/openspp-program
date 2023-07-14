from odoo import fields
from odoo.exceptions import ValidationError

from .common import Common


class TestG2pProgram(Common):
    def test_01_get_filtering_mechanism(self):
        res = self.program._get_filtering_mechanism()
        self.assertEqual(res, "1", "Filtering mechanism should be 1")
        self.env["ir.config_parameter"].set_param(
            "spp_programs.beneficiaries_filtering_mechanism", "2"
        )
        with self.assertLogs(
            "odoo.addons.spp_programs_compliance_criteria.models.g2p_program",
            level="WARNING",
        ) as log:
            res = self.program._get_filtering_mechanism()
            for out in log.output:
                self.assertRegex(
                    out,
                    r"^.*Filtering beneficiaries by all eligibility managers is not yet completely developed!$",
                    "Warning should be raised!",
                )
            self.assertEqual(res, "1", "Filtering mechanism should be 1")

    def test_02_compute_ongoing_cycle(self):
        self.assertTrue(
            self.program.ongoing_cycle, "Program should be marked as ongoing cycle!"
        )
        self.cycle.state = "ended"
        self.assertFalse(
            self.program.ongoing_cycle, "Program should not be marked as ongoing cycle!"
        )
        self.cycle.state = "approved"
        self.cycle.start_date = fields.Date.add(fields.Date.today(), days=10)
        self.assertFalse(
            self.program.ongoing_cycle, "Program should not be marked as ongoing cycle!"
        )

    def test_03_search_ongoing_cycle(self):
        with self.assertRaisesRegex(ValidationError, r"^Operation not supported!$"):
            self.env["g2p.program"].search([("ongoing_cycle", "not in", [True])])
        with self.assertRaisesRegex(ValidationError, r"^Operation not supported!$"):
            self.env["g2p.program"].search([("ongoing_cycle", "=", "1")])
        ongoing_cycle_programs = self.env["g2p.program"].search(
            [("ongoing_cycle", "=", True)]
        )
        self.assertIn(
            self.program,
            ongoing_cycle_programs,
            "Program should be found in ongoing cycles!",
        )
        ongoing_cycle_programs = self.env["g2p.program"].search(
            [("ongoing_cycle", "!=", False)]
        )
        self.assertIn(
            self.program,
            ongoing_cycle_programs,
            "Program should be found in ongoing cycles!",
        )

    def test_04_get_final_compliance_criteria_domain(self):
        with self.assertLogs(
            "odoo.addons.spp_programs_compliance_criteria.models.g2p_program",
            level="WARNING",
        ) as log:
            self.program._get_final_compliance_criteria_domain(condition="=")
            for out in log.output:
                self.assertRegex(
                    out,
                    r"^.*_get_final_compliance_criteria_domain is called with non-supported condition!$",
                    "warning should be raised!",
                )
        res = self.program._get_final_compliance_criteria_domain()
        self.assertEqual(
            res,
            [["partner_id", "in", [self._test_group_1.id, self._test_group_2.id]]],
            "Group ids should be return in final compliance criteria domain",
        )

    def test_05___compliance_criteria(self):
        self.manager_default.write(
            {
                "eligibility_domain": f"[['id', '!=', {self._test_group_2.id}]]",
            }
        )
        self.program._compliance_criteria()
        program_group_1_beneficiary = self.program.program_membership_ids.filtered(
            lambda pm: pm.partner_id == self._test_group_1
        )
        program_group_2_beneficiary = self.program.program_membership_ids.filtered(
            lambda pm: pm.partner_id == self._test_group_2
        )
        self.assertEqual(
            program_group_1_beneficiary.state,
            "enrolled",
            "Group 1 should be stayed as enrolled beneficiary!",
        )
        self.assertEqual(
            program_group_2_beneficiary.state,
            "paused",
            "Group 2 beneficiary should be paused!",
        )
        cycle_group_1_beneficiary = self.cycle.cycle_membership_ids.filtered(
            lambda pm: pm.partner_id == self._test_group_1
        )
        cycle_group_2_beneficiary = self.cycle.cycle_membership_ids.filtered(
            lambda pm: pm.partner_id == self._test_group_2
        )
        self.assertEqual(
            cycle_group_1_beneficiary.state,
            "enrolled",
            "Group 1 should be stayed as enrolled beneficiary!",
        )
        self.assertEqual(
            cycle_group_2_beneficiary.state,
            "paused",
            "Group 2 beneficiary should be paused!",
        )

    def test_06_compliance_criteria(self):
        self.program.compliance_criteria()
        program_create_queue_jobs = self.env["queue.job"].search(
            [("model_name", "=", "g2p.program")]
        )
        self.assertFalse(
            bool(program_create_queue_jobs.ids),
            "Job should not be created since auto compliance is False!",
        )
        self.program.auto_compliance = True
        self.program.compliance_criteria()
        program_create_queue_jobs = self.env["queue.job"].search(
            [("model_name", "=", "g2p.program")]
        )
        self.assertTrue(
            bool(program_create_queue_jobs.ids),
            "Job should not be created since auto compliance is True!",
        )
