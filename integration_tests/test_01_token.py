import logging

from integration_tests.test_base import IntegrationTestsBase, ContentType

LOG = logging.getLogger(__name__)


class TokenTests(IntegrationTestsBase):
    __test__ = True
    admin_token = None

    def setUp(self):
        super().setUp()
        self.set_api_headers(content_type=ContentType.X_WWW_FORM_URL_ENCODED)

    def test_101_get_token_admin(self):
        LOG.info("====TEST get_token_admin====")
        self.get_admin_token()

    def test_102_get_token_invalid_password(self):
        LOG.info("====TEST get_token_invalid_password====")
        data = {
            'username': self.username,
            'password': 'invalid',
            'scope': 'admin',
            'grant_type': '',
            'client_id': '',
            'client_secret': ''
        }

        resp = self.api_client.make_request('post', 'token', data=data)
        self.assertEqual(401, resp.status_code)
        json = resp.json()
        self.assertEqual(json.get('detail'), "Incorrect username or password or invalid scopes")

    def test_103_get_token_invalid_scopes(self):
        LOG.info("====TEST get_token_invalid_scopes====")
        data = {
            'username': self.username,
            'password': self.password,
            'scope': 'admin,account',
            'grant_type': '',
            'client_id': '',
            'client_secret': ''
        }

        resp = self.api_client.make_request('post', 'token', data=data)
        self.assertEqual(401, resp.status_code)
        json = resp.json()
        self.assertEqual(json.get('detail'), "Incorrect username or password or invalid scopes")

    def test_104_get_token_incorrect_scope(self):
        LOG.info("====TEST get_token_incorrect_scope====")
        data = {
            'username': self.username,
            'password': self.password,
            'scope': 'account',
            'grant_type': '',
            'client_id': '',
            'client_secret': ''
        }

        resp = self.api_client.make_request('post', 'token', data=data)
        self.assertEqual(401, resp.status_code)
        json = resp.json()
        self.assertEqual(json.get('detail'), "Incorrect username or password or invalid scopes")

    def test_105_get_token_account(self):
        LOG.info("====TEST get_token_account====")
        # Get Admin token
        self.get_admin_token()

        # Create Account
        email = self.account_emails[0]
        self.create_account(email=email)
        account_id = self.accounts[email]['account_id']

        # Get Account Token
        account_token = self.get_account_token(account_id=account_id)

        # Delete Account with Account Token
        self.delete_account(account_id=account_id, token=account_token)
