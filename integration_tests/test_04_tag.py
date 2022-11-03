import logging

from integration_tests.test_base import IntegrationTestsBase, ContentType

LOG = logging.getLogger(__name__)


class TagTests(IntegrationTestsBase):
    __test__ = True
    links = {}
    tags = {}

    def setUp(self):
        super().setUp()
        self.get_admin_token()

    def test_401_create_account(self):
        LOG.info("====TEST create_account====")
        self.create_account(email=self.account_emails[0])

    def test_402_create_second_account(self):
        LOG.info("====TEST create_second_account====")
        self.create_account(email=self.account_emails[1])

    def test_403_create_tag_admin(self):
        LOG.info("====TEST create_tag_admin===")
        tag = self.create_tag(tag='test1', token=self.admin_token,
                              account_id=self.accounts[self.account_emails[0]]['account_id'])
        self.store_tag(tag, self.account_emails[0])

    def test_404_create_tag_admin_no_account_id(self):
        LOG.info("====TEST create_tag_admin_no_account_id===")
        self.set_api_headers(content_type=ContentType.JSON, token=self.admin_token)
        json = {
            'tag': 'test2'
        }

        resp = self.api_client.make_request('post', 'tag', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'The account_id field is required for the admin scope')

    def test_405_create_tag_account(self):
        LOG.info("====TEST create_tag_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag = self.create_tag(tag='test2', token=account_token, account_id=account_id)
        self.store_tag(tag, self.account_emails[1])

    def test_406_create_tag_account_no_account_id(self):
        LOG.info("====TEST create_tag_account_no_account_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag = self.create_tag(tag='test3', token=account_token)
        self.store_tag(tag, self.account_emails[1])

    def test_407_create_tag_account_match_account_1(self):
        LOG.info("====TEST create_tag_account_match_account_1===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag = self.create_tag(tag='test1', token=account_token)
        self.store_tag(tag, self.account_emails[1])

    def test_408_create_tag_account_duplicate(self):
        LOG.info("====TEST create_tag_account_duplicate===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'tag': 'test2'
        }

        resp = self.api_client.make_request('post', 'tag', json=json)
        self.assertEqual(409, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Tag with name test2 exists for account {account_id}')

    def test_409_create_tag_account_wrong_account_id(self):
        LOG.info("====TEST create_tag_account_wrong_account_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_id2 = self.accounts[self.account_emails[0]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'tag': 'test2',
            'account_id': account_id2
        }

        resp = self.api_client.make_request('post', 'tag', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'The account_id field should not be provided for account scope')

    def test_410_get_tag_not_authenticated(self):
        LOG.info("====TEST get_tag_not_authenticated===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.set_api_headers(content_type=ContentType.JSON, token=None)
        resp = self.api_client.make_request('get', f'tag/{tag_id}')
        self.assertEqual(401, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'Not authenticated')

    def test_411_get_tag_admin(self):
        LOG.info("====TEST get_tag_admin===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.get_tag(tag_id=tag_id, token=self.admin_token)

    def test_412_get_tag_account(self):
        LOG.info("====TEST get_tag_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = self.tags[self.account_emails[1]][0]['tag_id']
        self.get_tag(tag_id=tag_id, token=account_token)

        # 404 if get tag belonging to another account
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        resp = self.api_client.make_request('get', f'tag/{tag_id}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Tag with tag_id {tag_id} not found')

    def test_413_get_tags_admin(self):
        LOG.info("====TEST get_tags_admin===")
        tags = self.get_tags(token=self.admin_token)
        self.assertTrue(len(tags) >= 4)

    def test_414_get_tags_account(self):
        LOG.info("====TEST get_tags_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token)
        self.assertEqual(len(tags), 3)

    def test_415_get_tags_by_account_id_admin(self):
        LOG.info("====TEST get_tags_by_account_id_admin===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        tags = self.get_tags(token=self.admin_token, account_id=account_id)
        self.assertTrue(len(tags) >= 3)

    def test_416_get_tags_by_account_id_account(self):
        LOG.info("====TEST get_tags_by_account_id_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, account_id=account_id)
        self.assertEqual(len(tags), 3)

    def test_417_get_tags_by_tag_admin(self):
        LOG.info("====TEST get_tags_by_tag_admin===")
        tags = self.get_tags(token=self.admin_token, tag='test1')
        self.assertTrue(len(tags) >= 2)

    def test_418_get_tags_by_tag_account(self):
        LOG.info("====TEST get_tags_by_tag_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, tag='test1')
        self.assertEqual(len(tags), 1)

    def test_419_delete_tag_account(self):
        LOG.info("====TEST delete_tag_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = self.tags[self.account_emails[1]][2]['tag_id']
        self.delete_tag(tag_id=tag_id, token=account_token)

        # If account doesn't own tag, a 404 is returned as if the tag doesn't exist
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        resp = self.api_client.make_request('delete', f'tag/{tag_id}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Tag with tag_id {tag_id} not found')

    def test_420_delete_tag_admin(self):
        LOG.info("====TEST delete_tag_admin===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.delete_tag(tag_id=tag_id, token=self.admin_token)

    def test_421_delete_account_deletes_tags(self):
        LOG.info("====TEST delete_account_deletes_tags===")
        account_id_1 = self.accounts[self.account_emails[0]]['account_id']
        self.delete_account(account_id=account_id_1, token=self.admin_token)
        account_id_2 = self.accounts[self.account_emails[1]]['account_id']
        self.delete_account(account_id=account_id_2, token=self.admin_token)

        tags = self.get_tags(token=self.admin_token, account_id=account_id_1)
        self.assertEqual(len(tags), 0)
        tags = self.get_tags(token=self.admin_token, account_id=account_id_2)
        self.assertEqual(len(tags), 0)













