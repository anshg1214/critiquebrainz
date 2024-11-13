import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class ProfileApplicationsViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ProfileApplicationsViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": u"Tester",
        }))
        self.hacker = User(db_users.get_or_create(2, "Hacker", new_user_data={
            "display_name": u"Hacker!",
        }))
        self.application = {
            "name": "Some Application",
            "desc": "Created for some purpose",
            "website": "http://example.com/",
            "redirect_uri": "http://example.com/redirect/",
        }

    def create_dummy_application(self):
        db_oauth_client.create(user_id=self.user.id, **self.application)
        client = db_users.clients(self.user.id)[0]
        return client

    def test_index(self):
        self.temporary_login(self.user)
        response = self.client.get('/profile/applications', follow_redirects=True)
        self.assert200(response)
        self.assertIn("No applications found", str(response.data))

    def test_create(self):
        self.temporary_login(self.user)
        response = self.client.post('/profile/applications/create', data=self.application,
                                    follow_redirects=True)
        self.assert200(response)
        self.assertIn('You have created an application!', str(response.data))
        self.assertIn(self.application['name'], str(response.data))

    def test_create_invalid_redirect(self):
        """Check that an error is returned if the redirect URL isn't an http/s url"""
        self.temporary_login(self.user)
        data = {
            "name": "Another Application",
            "desc": "Created for Hacking",
            "website": "http://example.com/",
            "redirect_uri": "javascript://alert(ohno)",
        }
        response = self.client.post('/profile/applications/create', data=data,
                                    follow_redirects=True)
        self.assert200(response)
        self.assertNotIn('You have created an application!', str(response.data))
        self.assertIn('callback URL must use http or https', str(response.data))

    def test_create_invalid_website(self):
        """Check that an error is returned if the redirect URL isn't an http/s url"""
        self.temporary_login(self.user)
        data = {
            "name": "Another Application",
            "desc": "Created for Hacking",
            "website": "javascript://alert(ohno)",
            "redirect_uri": "http://example.com/redirect",
        }
        response = self.client.post('/profile/applications/create', data=data,
                                    follow_redirects=True)
        self.assert200(response)
        self.assertNotIn('You have created an application!', str(response.data))
        self.assertIn('Homepage URL must use http or https', str(response.data))

    def test_edit(self):
        app = self.create_dummy_application()

        self.application["name"] = "New Name of Application"

        self.temporary_login(self.user)
        response = self.client.post('/profile/applications/%s/edit' % app["client_id"],
                                    data=self.application, query_string=self.application,
                                    follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.application['name'], str(response.data))

    def test_delete(self):
        app = self.create_dummy_application()

        self.temporary_login(self.hacker)
        response = self.client.get('/profile/applications/%s/delete' % app["client_id"],
                                   follow_redirects=True)
        self.assert404(response, "Shouldn't be able to delete other's applications.")

        self.temporary_login(self.user)
        response = self.client.get('/profile/applications/%s/delete' % app["client_id"],
                                   follow_redirects=True)
        self.assert200(response)
        self.assertIn("You have deleted an application.", str(response.data))

    def test_token_delete(self):
        app = self.create_dummy_application()

        self.temporary_login(self.user)
        response = self.client.get('/profile/applications/%s/token/delete' % app["client_id"])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/profile/applications/')
