from odoo import fields
from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_individual = self.env["res.partner"].create(
            {
                "name": "Individual 1",
                "is_registrant": True,
                "is_group": False,
            }
        )
        self._test_group_1 = self.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_registrant": True,
                "is_group": True,
                "group_membership_ids": [
                    (0, 0, {"individual": self._test_individual.id})
                ],
            }
        )
        self._test_group_2 = self.env["res.partner"].create(
            {
                "name": "Group 2",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self.program = self.env["g2p.program"].create(
            {
                "name": "Test Program",
                "target_type": "group",
            }
        )
        self.manager_default = self.env[
            "g2p.program_membership.manager.default"
        ].create(
            {
                "name": "Default",
                "program_id": self.program.id,
                "eligibility_domain": "[]",
            }
        )
        eligibility_manager = self.env["g2p.eligibility.manager"].create(
            {
                "program_id": self.program.id,
                "manager_ref_id": "%s,%s"
                % (self.manager_default._name, str(self.manager_default.id)),
            }
        )
        self.program.write(
            {
                "eligibility_managers": [(4, eligibility_manager.id)],
                "program_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self._test_group_1.id,
                            "state": "enrolled",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self._test_group_2.id,
                            "state": "enrolled",
                        },
                    ),
                ],
            }
        )
        self.cycle = self.env["g2p.cycle"].create(
            {
                "name": "Cycle 1",
                "program_id": self.program.id,
                "start_date": fields.Date.add(fields.Date.today(), days=-100),
                "end_date": fields.Date.add(fields.Date.today(), days=100),
                "state": "approved",
                "cycle_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self._test_group_1.id,
                            "state": "enrolled",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": self._test_group_2.id,
                            "state": "enrolled",
                        },
                    ),
                ],
            }
        )
