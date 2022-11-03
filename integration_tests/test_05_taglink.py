import logging

from integration_tests.test_base import IntegrationTestsBase, ContentType

LOG = logging.getLogger(__name__)


class TagLinkTests(IntegrationTestsBase):
    __test__ = True
    links = {}
    tags = {}

    def setUp(self):
        super().setUp()
        self.get_admin_token()

    def test_501_create_account(self):
        LOG.info("====TEST create_account====")
        self.create_account(email=self.account_emails[0])

    def test_502_create_second_account(self):
        LOG.info("====TEST create_second_account====")
        self.create_account(email=self.account_emails[1])

    def test_503_create_taglink_admin(self):
        LOG.info("====TEST create_taglink_admin===")
        tag = self.create_tag(tag='test1', token=self.admin_token,
                              account_id=self.accounts[self.account_emails[0]]['account_id'])
        self.store_tag(tag, self.account_emails[0])
        link = self.create_link(link='https://test1.com', token=self.admin_token, tag='test2',
                                account_id=self.accounts[self.account_emails[0]]['account_id'])
        self.store_link(link, self.account_emails[0])
        tag_id = tag['tag_id']
        link_id = link['link_id']
        self.create_taglink(tag_id=tag_id, link_id=link_id, token=self.admin_token,
                            account_id=self.accounts[self.account_emails[0]]['account_id'])

    def test_504_create_taglink_admin_no_account_id(self):
        LOG.info("====TEST create_taglink_admin_no_account_id===")
        tag = self.create_tag(tag='test3', token=self.admin_token,
                              account_id=self.accounts[self.account_emails[0]]['account_id'])
        link = self.create_link(link='https://test2.com', token=self.admin_token, tag='test4',
                                account_id=self.accounts[self.account_emails[0]]['account_id'])
        self.set_api_headers(content_type=ContentType.JSON, token=self.admin_token)
        json = {
            'tag_id': tag['tag_id'],
            'link_id': link['link_id']
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'The account_id field is required for the admin scope')

    def test_505_create_taglink_account(self):
        LOG.info("====TEST create_taglink_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag = self.create_tag(tag='test5', token=account_token, account_id=account_id)
        self.store_tag(tag, self.account_emails[1])
        link = self.create_link(link='https://test3.com', token=account_token, tag='test4', account_id=account_id)
        self.store_link(link, self.account_emails[1])
        self.create_taglink(tag_id=tag['tag_id'], link_id=link['link_id'], token=account_token, account_id=account_id)

    def test_506_create_taglink_account_no_account_id(self):
        LOG.info("====TEST create_taglink_account_no_account_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag = self.create_tag(tag='test6', token=account_token)
        link = self.create_link(link='https://test4.com', token=account_token, tag='test4')
        self.create_taglink(tag_id=tag['tag_id'], link_id=link['link_id'], token=account_token)

    def test_507_create_taglink_account_match_account_1(self):
        LOG.info("====TEST create_taglink_account_match_account_1===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag = self.create_tag(tag='test1', token=account_token, account_id=account_id)
        link = self.create_link(link='https://test1.com', token=account_token, tag='test2', account_id=account_id)
        tag_id = tag['tag_id']
        link_id = link['link_id']
        self.create_taglink(tag_id=tag_id, link_id=link_id, token=account_token,
                            account_id=account_id)

    def test_508_create_taglink_account_duplicate(self):
        LOG.info("====TEST create_taglink_account_duplicate===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, tag='test1')
        links = self.get_links(token=account_token, tag='test1')
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        tag_id = tags[0]['tag_id']
        link_id = links[0]['link_id']
        json = {
            'tag_id': tag_id,
            'link_id': link_id
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(409, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'TagLink with tag_id {tag_id} and link_id {link_id} exists')

    def test_509_create_taglink_account_tag_not_found(self):
        LOG.info("====TEST create_taglink_account_tag_not_found===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        links = self.get_links(token=account_token, tag='test1')
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        link_id = links[0]['link_id']
        json = {
            'tag_id': tag_id,
            'link_id': link_id
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Tag with tag_id {tag_id} not found for account_id {account_id}')

    def test_510_create_taglink_account_tag_invalid(self):
        LOG.info("====TEST create_taglink_account_tag_invalid===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = 'invalid'
        links = self.get_links(token=account_token, tag='test1')
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        link_id = links[0]['link_id']
        json = {
            'tag_id': tag_id,
            'link_id': link_id
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Tag with tag_id {tag_id} not found for account_id {account_id}')

    def test_511_create_taglink_account_link_not_found(self):
        LOG.info("====TEST create_taglink_account_link_not_found===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, tag='test1')
        tag_id = tags[0]['tag_id']
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'tag_id': tag_id,
            'link_id': link_id
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Link with link_id {link_id} not found for account_id {account_id}')

    def test_512_create_taglink_account_link_invalid(self):
        LOG.info("====TEST create_taglink_account_link_invalid===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, tag='test1')
        tag_id = tags[0]['tag_id']
        link_id = 'invalid'
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'tag_id': tag_id,
            'link_id': link_id
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], f'Link with link_id {link_id} not found for account_id {account_id}')

    def test_513_create_taglink_account_wrong_account(self):
        LOG.info("====TEST create_taglink_account_wrong_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_id2 = self.accounts[self.account_emails[0]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tags = self.get_tags(token=account_token, tag='test1')
        tag_id = tags[0]['tag_id']
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        json = {
            'tag_id': tag_id,
            'link_id': link_id,
            'account_id': account_id2
        }

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'The account_id field should not be provided for account scope')

    def test_514_get_taglink_admin(self):
        LOG.info("====TEST get_taglink_admin===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.get_taglinks(token=self.admin_token, tag_id=tag_id, link_id=link_id)

    def test_515_get_taglink_account(self):
        LOG.info("====TEST get_taglink_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = self.tags[self.account_emails[1]][0]['tag_id']
        link_id = self.links[self.account_emails[1]][0]['link_id']
        self.get_taglinks(token=account_token, tag_id=tag_id, link_id=link_id)

        # Empty list if taglink belongs to another account
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        params = {
            'tag_id': tag_id,
            'link_id': link_id
        }
        resp = self.api_client.make_request('get', f'taglink', params=params)
        self.assertEqual(200, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json, [])

    def test_516_get_taglinks_admin(self):
        LOG.info("====TEST get_taglinks_admin===")
        taglinks = self.get_taglinks(token=self.admin_token)
        self.assertTrue(len(taglinks) >= 3)

    def test_517_get_taglinks_account(self):
        LOG.info("====TEST get_taglinks_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        taglinks = self.get_taglinks(token=account_token)
        self.assertEqual(len(taglinks), 6)

    def test_518_get_taglinks_by_account_id_admin(self):
        LOG.info("====TEST get_taglinks_by_account_id_admin===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        taglinks = self.get_taglinks(token=self.admin_token, account_id=account_id)
        self.assertTrue(len(taglinks) >= 6)

    def test_519_get_tags_by_account_id_account(self):
        LOG.info("====TEST get_taglinks_by_account_id_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        taglinks = self.get_taglinks(token=account_token, account_id=account_id)
        self.assertEqual(len(taglinks), 6)

    def test_520_get_taglinks_by_tag_id_admin(self):
        LOG.info("====TEST get_taglinks_by_tag_id_admin===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        taglinks = self.get_taglinks(token=self.admin_token, tag_id=tag_id)
        self.assertTrue(len(taglinks) >= 1)

    def test_521_get_taglinks_by_tag_id_account(self):
        LOG.info("====TEST get_taglinks_by_tag_id_account===")
        tag_id = self.tags[self.account_emails[1]][0]['tag_id']
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        taglinks = self.get_taglinks(token=account_token, tag_id=tag_id)
        self.assertEqual(len(taglinks), 1)

    def test_522_get_taglinks_by_link_id_admin(self):
        LOG.info("====TEST get_taglinks_by_link_id_admin===")
        link_id = self.links[self.account_emails[0]][0]['link_id']
        taglinks = self.get_taglinks(token=self.admin_token, link_id=link_id)
        self.assertTrue(len(taglinks) >= 1)

    def test_523_get_taglinks_by_link_id_account(self):
        LOG.info("====TEST get_taglinks_by_link_id_account===")
        link_id = self.links[self.account_emails[1]][0]['link_id']
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        taglinks = self.get_taglinks(token=account_token, link_id=link_id)
        self.assertEqual(len(taglinks), 2)

    def test_524_delete_taglink_account_no_tag_id_no_link_id(self):
        LOG.info("====TEST delete_taglink_account_no_tag_id_no_link_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        self.set_api_headers(content_type=ContentType.JSON, token=account_token)
        resp = self.api_client.make_request('delete', f'taglink')
        self.assertEqual(422, resp.status_code)
        resp_json = resp.json()
        self.assertEqual(resp_json['detail'], 'One or both of tag_id and link_id must be specified')

    def test_525_delete_taglink_account(self):
        LOG.info("====TEST delete_taglink_account===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = self.tags[self.account_emails[1]][0]['tag_id']
        link_id = self.links[self.account_emails[1]][0]['link_id']
        self.delete_taglinks(token=account_token, tag_id=tag_id, link_id=link_id)

        # If account doesn't own taglink, return success as taglink doesn't exist for the account
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.delete_taglinks(token=account_token, tag_id=tag_id, link_id=link_id)

    def test_526_delete_taglinks_admin_by_tag_id(self):
        LOG.info("====TEST delete_taglink_admin_by_tag_id===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.delete_taglinks(token=self.admin_token, tag_id=tag_id)

    def test_527_delete_taglink_account_by_tag_id(self):
        LOG.info("====TEST delete_taglink_account_by_tag_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        tag_id = self.tags[self.account_emails[1]][0]['tag_id']
        self.delete_taglinks(token=account_token, tag_id=tag_id)

        # If account doesn't own tag, return success as taglink doesn't exist for the account
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        self.delete_taglinks(token=account_token, tag_id=tag_id)

    def test_528_delete_taglinks_admin_by_link_id(self):
        LOG.info("====TEST delete_taglink_admin_by_link_id===")
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.delete_taglinks(token=self.admin_token, link_id=link_id)

    def test_529_delete_taglink_account_by_link_id(self):
        LOG.info("====TEST delete_taglink_account_by_link_id===")
        account_id = self.accounts[self.account_emails[1]]['account_id']
        account_token = self.get_account_token(account_id=account_id)
        link_id = self.links[self.account_emails[1]][0]['link_id']
        self.delete_taglinks(token=account_token, link_id=link_id)

        # If account doesn't own link, return success as taglink doesn't exist for the account
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.delete_taglinks(token=account_token, link_id=link_id)

    def test_530_delete_taglink_admin(self):
        LOG.info("====TEST delete_taglink_admin===")
        tag_id = self.tags[self.account_emails[0]][0]['tag_id']
        link_id = self.links[self.account_emails[0]][0]['link_id']
        self.delete_taglinks(token=self.admin_token, tag_id=tag_id, link_id=link_id)

    def test_531_delete_account_deletes_taglinks(self):
        LOG.info("====TEST delete_account_deletes_taglinks===")
        account_id_1 = self.accounts[self.account_emails[0]]['account_id']
        self.delete_account(account_id=account_id_1, token=self.admin_token)
        account_id_2 = self.accounts[self.account_emails[1]]['account_id']
        self.delete_account(account_id=account_id_2, token=self.admin_token)

        taglinks = self.get_taglinks(token=self.admin_token, account_id=account_id_1)
        self.assertEqual(len(taglinks), 0)
        taglinks = self.get_taglinks(token=self.admin_token, account_id=account_id_2)
        self.assertEqual(len(taglinks), 0)













