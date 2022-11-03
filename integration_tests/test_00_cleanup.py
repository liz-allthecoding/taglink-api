import logging

from integration_tests.test_base import IntegrationTestsBase

LOG = logging.getLogger(__name__)


class AccountTests(IntegrationTestsBase):
    __test__ = True

    def setUp(self):
        super().setUp()
        self.get_admin_token()

    def test_001_delete_accounts(self):
        LOG.info("====TEST delete_accounts====")
        self.delete_accounts()
