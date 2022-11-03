import logging

from integration_tests.test_base import IntegrationTestsBase, ContentType

LOG = logging.getLogger(__name__)


class AccountTests(IntegrationTestsBase):
    __test__ = True

    def setUp(self):
        super().setUp()
        self.get_admin_token()

    def test_201_create_account(self):
        LOG.info("====TEST create_account====")
        self.create_account(email=self.account_emails[0])

    def test_202_create_second_account(self):
        LOG.info("====TEST create_second_account====")
        self.create_account(email=self.account_emails[1])

    def test_203_create_account_account_scope(self):
        LOG.info("====TEST create_account_account_scope====")
        email = self.account_emails[1]
        account_id = self.accounts[self.account_emails[0]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'email': email,
            'password': self.account_password
        }

        resp = self.api_client.make_request('post', 'account', json=json)
        self.assertEqual(401, resp.status_code)
        resp_json = resp.json()
        detail = resp_json['detail']
        self.assertEqual(detail, "Not enough permissions")

    def test_204_create_account_admin_scope_exists(self):
        LOG.info("====TEST create_account_admin_scope_exists====")
        email = self.account_emails[1]
        self.set_api_headers(content_type=ContentType.JSON, token=self.admin_token)
        json = {
            'email': email,
            'password': self.account_password
        }

        resp = self.api_client.make_request('post', 'account', json=json)
        self.assertEqual(409, resp.status_code)
        resp_json = resp.json()
        detail = resp_json['detail']
        self.assertEqual(detail, f"Account with email {email} exists")

    def test_205_get_account_admin_scope(self):
        LOG.info("====TEST get_account_admin_scope====")
        self.get_account(account_id=self.accounts[self.account_emails[0]]['account_id'], token=self.admin_token)

        account_id = 'invalid'
        resp = self.api_client.make_request('get', f'account/{account_id}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        detail = resp_json['detail']
        self.assertEqual(detail, f"Account with account_id '{account_id}' not found")

    def test_206_get_account_account_scope(self):
        LOG.info("====TEST get_account_account_scope====")
        account_id = self.accounts[self.account_emails[0]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.get_account(account_id=account_id, token=account_token)

        account_id = self.accounts[self.account_emails[1]]['account_id']
        resp = self.api_client.make_request('get', f'account/{account_id}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        detail = resp_json['detail']
        self.assertEqual(detail, f"Account with account_id '{account_id}' not found")

    def test_207_get_accounts_admin_scope(self):
        LOG.info("====TEST get_accounts_admin_scope====")
        accounts = self.get_accounts(token=self.admin_token)
        self.assertTrue(len(accounts) >= 2)

        accounts = self.get_accounts(token=self.admin_token, email=self.account_emails[0])
        self.assertEqual(len(accounts), 1)

    def test_208_get_accounts_account_scope(self):
        LOG.info("====TEST get_accounts_account_scope====")
        account_id = self.accounts[self.account_emails[0]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        accounts = self.get_accounts(token=account_token)
        self.assertEqual(len(accounts), 1)

        accounts = self.get_accounts(token=account_token, email=self.account_emails[0])
        self.assertEqual(len(accounts), 1)

        accounts = self.get_accounts(token=account_token, email=self.account_emails[1])
        self.assertEqual(len(accounts), 0)

    def test_209_delete_account_account_scope(self):
        LOG.info("====TEST delete_account_account_scope====")
        account_id = self.accounts[self.account_emails[0]]['account_id']
        account_id_2 = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)

        resp = self.api_client.make_request('delete', f'account/{account_id_2}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        detail = resp_json['detail']
        self.assertEqual(detail, f"Account with account_id '{account_id_2}' not found")

        self.delete_account(account_id=account_id, token=account_token)

    def test_210_delete_account_admin_scope(self):
        LOG.info("====TEST delete_account_admin_scope====")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        self.delete_account(account_id=account_id, token=self.admin_token)





