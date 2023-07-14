from .common import Common


class TestG2pCycleMembership(Common):
    def test_01_filter_valid_enrolled_beneficiaries(self):
        domain = [["cycle_id", "=", self.cycle.id]]
        res = self.env["g2p.cycle.membership"].filter_valid_enrolled_beneficiaries(
            domain
        )
        self.assertTrue(bool(res.get("views")), "Should have key views")
        self.assertTrue(bool(res.get("domain")), "Should have key domain")
        self.assertNotEqual(domain, res["domain"], "Domain should be implemented!")
