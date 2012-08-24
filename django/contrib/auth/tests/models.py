from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import (Group, User,
    SiteProfileNotAvailable, UserManager)


class ProfileTestCase(TestCase):

    def setUp(self):
        """Backs up the AUTH_PROFILE_MODULE"""
        self.user = User.objects.create(username='testclient') 

    @override_settings(AUTH_PROFILE_MODULE='')    
    def test_site_profile_not_available(self):
        # calling get_profile without AUTH_PROFILE_MODULE set
        self.assertRaises(SiteProfileNotAvailable, self.user.get_profile)

    @override_settings(AUTH_PROFILE_MODULE='foobar')
    def test_site_profile_bad_syntax(self):
        # Bad syntax in AUTH_PROFILE_MODULE:
        self.assertRaises(SiteProfileNotAvailable, self.user.get_profile)

    @override_settings(AUTH_PROFILE_MODULE='foo.bar')
    def test_site_profile_missing_module(self):
        # module that doesn't exist
        self.assertRaises(SiteProfileNotAvailable, self.user.get_profile)

ProfileTestCase = override_settings(USE_TZ=False)(ProfileTestCase)


class NaturalKeysTestCase(TestCase):
    fixtures = ['authtestdata.json']

    def test_user_natural_key(self):
        staff_user = User.objects.get(username='staff')
        self.assertEquals(User.objects.get_by_natural_key('staff'), staff_user)
        self.assertEquals(staff_user.natural_key(), ('staff',))

    def test_group_natural_key(self):
        users_group = Group.objects.create(name='users')
        self.assertEquals(Group.objects.get_by_natural_key('users'), users_group)

NaturalKeysTestCase = override_settings(USE_TZ=False)(NaturalKeysTestCase)


class LoadDataWithoutNaturalKeysTestCase(TestCase):
    fixtures = ['regular.json']

    def test_user_is_created_and_added_to_group(self):
        user = User.objects.get(username='my_username')
        group = Group.objects.get(name='my_group')
        self.assertEquals(group, user.groups.get())

LoadDataWithoutNaturalKeysTestCase = override_settings(USE_TZ=False)(LoadDataWithoutNaturalKeysTestCase)


class LoadDataWithNaturalKeysTestCase(TestCase):
    fixtures = ['natural.json']

    def test_user_is_created_and_added_to_group(self):
        user = User.objects.get(username='my_username')
        group = Group.objects.get(name='my_group')
        self.assertEquals(group, user.groups.get())

LoadDataWithNaturalKeysTestCase = override_settings(USE_TZ=False)(LoadDataWithNaturalKeysTestCase)


class UserManagerTestCase(TestCase):

    def test_create_user(self):
        email_lowercase = 'normal@normal.com'
        user = User.objects.create_user('user', email_lowercase)
        self.assertEquals(user.email, email_lowercase)
        self.assertEquals(user.username, 'user')
        self.assertEquals(user.password, '!')

    def test_create_user_email_domain_normalize_rfc3696(self):
        # According to  http://tools.ietf.org/html/rfc3696#section-3
        # the "@" symbol can be part of the local part of an email address
        returned = UserManager.normalize_email(r'Abc\@DEF@EXAMPLE.com')
        self.assertEquals(returned, r'Abc\@DEF@example.com')

    def test_create_user_email_domain_normalize(self):
        returned = UserManager.normalize_email('normal@DOMAIN.COM')
        self.assertEquals(returned, 'normal@domain.com')

    def test_create_user_email_domain_normalize_with_whitespace(self):
        returned = UserManager.normalize_email('email\ with_whitespace@D.COM')
        self.assertEquals(returned, 'email\ with_whitespace@d.com')

    def test_empty_username(self):
        self.assertRaisesMessage(ValueError,
                                 'The given username must be set',
                                  User.objects.create_user, username='')
