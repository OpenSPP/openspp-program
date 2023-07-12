odoo.define("spp_programs_compliance_criteria.filter_valid_enrolled_beneficiaries", function (require) {
    var ListController = require("web.ListController");
    var session = require("web.session");

    ListController.include({
        init: function () {
            this._super.apply(this, arguments);
            this.programCycleBeneficiaries = ["g2p.program_membership", "g2p.cycle.membership"].includes(
                this.modelName
            );
        },

        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                const membershipFilteringButton = this.$buttons.find(
                    ".o_list_button_filter_valid_enrolled_beneficiaries"
                );
                if (!this.programCycleBeneficiaries) {
                    return membershipFilteringButton.hide();
                }
                membershipFilteringButton.click(this._filterValidEnrolledBeneficiaries.bind(this));
            }
        },

        _filterValidEnrolledBeneficiaries: async function () {
            const context = {
                ...session.user_context,
                uid: session.uid,
            };
            const res = await session.rpc("/web/dataset/call_kw/", {
                model: this.modelName,
                method: "filter_valid_enrolled_beneficiaries",
                args: [this.model.loadParams.domain],
                kwargs: {context},
            });
            return this.do_action(res);
        },
    });
});
