import logging

from integration_tests.test_base import IntegrationTestsBase, ContentType

LOG = logging.getLogger(__name__)


class LinkTests(IntegrationTestsBase):
    __test__ = True
    links = {}
    tags = {}

    def setUp(self):
        super().setUp()
        self.get_admin_token()

    def test_301_create_account(self):
        LOG.info("====TEST create_account====")
        self.create_account(email=self.account_emails[0])

    def test_302_create_second_account(self):
        LOG.info("====TEST create_second_account====")
        self.create_account(email=self.account_emails[1])

    def test_303_create_link_admin(self):
        LOG.info("====TEST create_link_admin===")
        link = self.create_link(link='https://test1.com', token=self.admin_token, tag='test1',
                                account_id=self.accounts[self.account_emails[0]]['account_id'])
        self.store_link(link, self.account_emails[0])

    def test_304_create_link_admin_no_account_id(self):
        LOG.info("====TEST create_link_admin_no_account_id===")
        self.set_api_headers(content_type=ContentType.JSON, token=self.admin_token)
        json = {
            'link': 'https://test2.com',
            'tag': 'test2'
        }

        resp = self.api_client.make_request('post', 'link', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'The account_id field is required for the admin scope')

    def test_305_create_link_account(self):
        LOG.info("====TEST create_link_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        link = self.create_link(link='https://test2.com', token=account_token, tag='test2',
                                account_id=account_id)
        self.store_link(link, self.account_emails[1])

    def test_306_create_link_account_no_account_id(self):
        LOG.info("====TEST create_link_account_no_account_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        link = self.create_link(link='https://test3.com', token=account_token, tag='test3')
        self.store_link(link, self.account_emails[1])

    def test_307_create_link_account_match_account_1(self):
        LOG.info("====TEST create_link_account_match_account_1===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        link = self.create_link(link='https://test1.com', token=account_token, tag='test1')
        self.store_link(link, self.account_emails[1])

    def test_308_create_link_account_with_tag_id(self):
        LOG.info("====TEST create_link_account_with_tag_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token)
        tag_id = tags[0]['tag_id']
        link = self.create_link(link='https://test4.com', token=account_token, tag_id=tag_id,
                                account_id=account_id)
        self.store_link(link, self.account_emails[1])

    def test_309_create_link_account_with_existing_tag(self):
        LOG.info("====TEST create_link_account_with_tag===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token)
        tag = tags[0]['tag']
        link = self.create_link(link='https://test5.com', token=account_token, tag=tag,
                                account_id=account_id)
        self.store_link(link, self.account_emails[1])

    def test_310_create_link_account_invalid_tag(self):
        LOG.info("====TEST create_link_invalid_tag===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'link': 'https://test2.com',
            'tag_id': 'invalid'
        }

        resp = self.api_client.make_request('post', 'link', json=json)
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Tag with tag_id invalid not found for account_id {account_id}')

    def test_311_create_link_account_wrong_account_id(self):
        LOG.info("====TEST create_link_account_wrong_account_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_id2 = self.accounts[self.account_emails[0]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'link': 'https://test2.com',
            'tag': 'test6',
            'account_id': account_id2
        }

        resp = self.api_client.make_request('post', 'link', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'The account_id field should not be provided for account scope')

    def test_312_get_link_admin(self):
        LOG.info("====TEST get_link_admin===")
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.get_link(link_id=link_id, token=self.admin_token)

    def test_313_get_link_account(self):
        LOG.info("====TEST get_link_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        link_id = self.links[self.account_emails[1]][0]['link_id']
        self.get_link(link_id=link_id, token=account_token)

        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        resp = self.api_client.make_request('get', f'link/{link_id}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Link with link_id {link_id} not found')

    def test_314_get_links_admin(self):
        LOG.info("====TEST get_links_admin===")
        links = self.get_links(token=self.admin_token)
        self.assertTrue(len(links) >= 6)

    def test_315_get_links_account(self):
        LOG.info("====TEST get_links_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        links = self.get_links(token=account_token)
        self.assertEqual(len(links), 5)

    def test_316_get_links_by_account_id_admin(self):
        LOG.info("====TEST get_links_by_account_id_admin===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        links = self.get_links(token=self.admin_token, account_id=account_id)
        self.assertTrue(len(links) >= 5)

    def test_317_get_links_by_account_id_account(self):
        LOG.info("====TEST get_links_by_account_id_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        links = self.get_links(token=account_token, account_id=account_id)
        self.assertEqual(len(links), 5)

    def test_318_get_links_by_tag_admin(self):
        LOG.info("====TEST get_links_by_tag_admin===")
        links = self.get_links(token=self.admin_token, tag='test1')
        self.assertTrue(len(links) >= 2)

    def test_319_get_links_by_tag_account(self):
        LOG.info("====TEST get_links_by_tag_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        links = self.get_links(token=account_token, tag='test1')
        self.assertTrue(len(links) >= 1)

    def test_320_get_links_by_tag_id_admin(self):
        LOG.info("====TEST get_links_by_tag_id_admin===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        tags = self.get_tags(token=self.admin_token, tag='test1', account_id=account_id)
        tag_id = tags[0]['tag_id']
        links = self.get_links(token=self.admin_token, tag_id=tag_id)
        self.assertTrue(len(links) >= 1)

    def test_321_get_links_by_tag_id_account(self):
        LOG.info("====TEST get_links_by_tag_id_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, tag='test1')
        tag_id = tags[0]['tag_id']
        links = self.get_links(token=account_token, tag_id=tag_id)
        self.assertTrue(len(links) >= 1)

    def test_322_delete_link_account(self):
        LOG.info("====TEST delete_link_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        link_id = self.links[self.account_emails[1]][2]['link_id']
        self.delete_link(link_id=link_id, token=account_token)

        # If account doesn't own link, a 404 is returned as if the link doesn't exist
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        resp = self.api_client.make_request('delete', f'link/{link_id}')
        self.assertEqual(404, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Link with link_id {link_id} not found')

    def test_323_delete_link_admin(self):
        LOG.info("====TEST delete_link_admin===")
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.delete_link(link_id=link_id, token=self.admin_token)

    def test_324_delete_account_deletes_links(self):
        LOG.info("====TEST delete_account_deletes_links===")
        account_id_1 = self.accounts[self.account_emails[0]]['account_id']
        self.delete_account(account_id=account_id_1, token=self.admin_token)
        account_id_2 = self.accounts[self.account_emails[1]]['account_id']
        self.delete_account(account_id=account_id_2, token=self.admin_token)

        links = self.get_links(token=self.admin_token, account_id=account_id_1)
        self.assertEqual(len(links), 0)
        links = self.get_links(token=self.admin_token, account_id=account_id_2)
        self.assertEqual(len(links), 0)













