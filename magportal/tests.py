from django.test import TestCase

# Create your tests here.
# "python manage.py test magportal.tests" to run the tests.
# will be adding more tests as we go

import os
import re
import importlib
import warnings
import inspect
import tempfile

from django.urls import reverse, resolve
from django.test import TestCase
from django.conf import settings
import magportal.models
from magportal import forms, views
from django.db import models
from django.contrib.auth.models import User
from magportal.models import Magazine, Category
from populate_mags import populate
from django.forms import fields as django_fields

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

class Tests(TestCase):
    
    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.templates_dir = os.path.join(self.project_base_dir, 'template')
        self.magportal_templates_dir = os.path.join(self.templates_dir, 'magportal')
        
    def test_templates_directory_exists(self):
        """
        Does the template/ directory exist?
        """
        directory_exists = os.path.isdir(self.templates_dir)
        self.assertTrue(directory_exists, f"{FAILURE_HEADER}Your project's templates directory does not exist.{FAILURE_FOOTER}")

    def test_magportal_templates_directory_exists(self):
        """
        Does the template/magportal/ directory exist?
        """
        directory_exists = os.path.isdir(self.magportal_templates_dir)
        self.assertTrue(directory_exists, f"{FAILURE_HEADER}The magportal templates directory does not exist.{FAILURE_FOOTER}")

    def test_template_dir_setting(self):
        """
        Does the TEMPLATE_DIR setting exist, and does it point to the right directory?
        """
        variable_exists = 'TEMPLATE_DIR' in dir(settings)
        self.assertTrue(variable_exists, f"{FAILURE_HEADER}Your settings.py module does not have the variable TEMPLATE_DIR defined!{FAILURE_FOOTER}")

        template_dir_value = os.path.normpath(settings.TEMPLATE_DIR)
        template_dir_computed = os.path.normpath(self.templates_dir)
        self.assertEqual(template_dir_value, template_dir_computed, f"{FAILURE_HEADER}Your TEMPLATE_DIR setting does not point to the expected path. Check your configuration, and try again.{FAILURE_FOOTER}")

    def test_template_lookup_path(self):
        """
        Does the TEMPLATE_DIR value appear within the lookup paths for templates?
        """
        lookup_list = settings.TEMPLATES[0]['DIRS']
        found_path = False

        for entry in lookup_list:
            entry_normalised = os.path.normpath(entry)

            if entry_normalised == os.path.normpath(settings.TEMPLATE_DIR):
                found_path = True

        self.assertTrue(found_path, f"{FAILURE_HEADER}Your project's templates directory is not listed in the TEMPLATES>DIRS lookup list. Check your settings.py module.{FAILURE_FOOTER}")

    def test_templates_exist(self):
        """
        Do templates exist?
        """
        base_path = os.path.join(self.magportal_templates_dir, 'base.html')
        cancel_path = os.path.join(self.magportal_templates_dir, 'cancel.html')
        magazines_path = os.path.join(self.magportal_templates_dir, 'magazines.html')
        contact_path = os.path.join(self.magportal_templates_dir, 'contact.html')
        home_path = os.path.join(self.magportal_templates_dir, 'home.html')
        membership_path = os.path.join(self.magportal_templates_dir, 'membership.html')
        profile_path = os.path.join(self.magportal_templates_dir, 'view_profile.html')
        edit_profile_path_path = os.path.join(self.magportal_templates_dir, 'edit_profile.html')
        discount_code_path = os.path.join(self.magportal_templates_dir, 'discountcode.html')
  

        self.assertTrue(os.path.isfile(base_path), f"{FAILURE_HEADER}Your base.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(cancel_path), f"{FAILURE_HEADER}Your cancel.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(magazines_path), f"{FAILURE_HEADER}Your magazines.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(contact_path), f"{FAILURE_HEADER}Your contact.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(home_path), f"{FAILURE_HEADER}Your home.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(profile_path), f"{FAILURE_HEADER}Your view_profile.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(discount_code_path), f"{FAILURE_HEADER}Your discountcode.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(membership_path), f"{FAILURE_HEADER}Your membership.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")
        self.assertTrue(os.path.isfile(edit_profile_path_path), f"{FAILURE_HEADER}Your edit_profile.html template does not exist, or is in the wrong location.{FAILURE_FOOTER}")     
        
        
        
    def does_gitignore_include_database(self, path):
        """
        Takes the path to a .gitignore file, and checks to see whether the db.sqlite3 database is present in that file.
        """
        f = open(path, 'r')

        for line in f:
            line = line.strip()

            if line.startswith('db.sqlite3'):
                return True

        f.close()
        return False

    def test_databases_variable_exists(self):
        """
        Does the DATABASES settings variable exist, and does it have a default configuration?
        """
        self.assertTrue(settings.DATABASES, f"{FAILURE_HEADER}Your project's settings module does not have a DATABASES variable, which is required. Check the start of Chapter 5.{FAILURE_FOOTER}")
        self.assertTrue('default' in settings.DATABASES, f"{FAILURE_HEADER}You do not have a 'default' database configuration in your project's DATABASES configuration variable. Check the start of Chapter 5.{FAILURE_FOOTER}")

    def test_gitignore_for_database(self):
        """
        If you are using a Git repository and have set up a .gitignore, checks to see whether the database is present in that file.
        """
        git_base_dir = os.popen('git rev-parse --show-toplevel').read().strip()

        if git_base_dir.startswith('fatal'):
            warnings.warn("You don't appear to be using a Git repository for your codebase. Although not strictly required, it's *highly recommended*. Skipping this test.")
        else:
            gitignore_path = os.path.join(git_base_dir, '.gitignore')

            if os.path.exists(gitignore_path):
                self.assertTrue(self.does_gitignore_include_database(gitignore_path), f"{FAILURE_HEADER}Your .gitignore file does not include 'db.sqlite3' -- you should exclude the database binary file from all commits to your Git repository.{FAILURE_FOOTER}")
            else:
                warnings.warn("You don't appear to have a .gitignore file in place in your repository. We ask that you consider this! Read the Don't git push your Database paragraph in Chapter 5.")

    def views_use_correct_templates(self):
        
        """
        Do views use templates? Are they the correct ones?
        """
        
        self.browse_magazines = self.client.get(reverse('magportal:browse_magazines'))
        self.contact = self.client.get(reverse('magportal:contact'))
        self.browse_category = self.client.get(reverse('magportal:browse_category'))
        self.view_profile = self.client.get(reverse('magportal:view_profile'))
        self.register = self.client.get(reverse('magportal:register'))
        self.edit_profile = self.client.get(reverse('magportal:edit_profile'))
        self.favourite = self.client.get(reverse('magportal:favourite'))

        
        self.assertTemplateUsed(self.browse_magazines, 'magportal/magazines.html', f"{FAILURE_HEADER}Your browse_magazines() view does not use the expected magportal/magazines.html template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.contact, 'magportal/contact.html', f"{FAILURE_HEADER}Your contact() view does not use the expected magportal/contact.html template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.browse_category, 'magportal/magazines.html', f"{FAILURE_HEADER}Your browse_category() view does not use the expected magportal/magazines.html template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.view_profile, 'magportal/view_profile.html', f"{FAILURE_HEADER}Your view_profile() view does not use the expected magportal/browse.html template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.edit_profile, 'magportal/edit_profile.html', f"{FAILURE_HEADER}Your edit_profile view does not use the expected magportal/edit_profile.html template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.register, 'magportal/register.html', f"{FAILURE_HEADER}Your register() view does not use the expected magportal/register.htmll template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.user_login, 'magportal/login.html', f"{FAILURE_HEADER}Your user_login() view does not use the expected magportal/login.html template.{FAILURE_FOOTER}")
        self.assertTemplateUsed(self.favourite, 'magportal/magazines.html', f"{FAILURE_HEADER}Your favourite() view does not use the expected magportal/magazines.html template.{FAILURE_FOOTER}")
       
    def test_installed_apps(self):
        """
        Checks whether the 'django.contrib.auth' app has been included in INSTALLED_APPS.
        """
        self.assertTrue('django.contrib.auth' in settings.INSTALLED_APPS)
        
    def test_userprofile_class(self):
        """
        Does the UserProfile class exist in magportal.models? If so, are all the required attributes present?
        Assertion fails if we can't assign values to all the fields required (i.e. one or more missing).
        """
        self.assertTrue('UserProfile' in dir(magportal.models))

        user_profile = magportal.models.UserProfile()

        # Now check that all the required attributes are present.
        # We do this by building up a UserProfile instance, and saving it.
        expected_attributes = {
            'UserID': 123,
            'Slug': 'whatever',
            'UserAccount': create_user_object(),
        }

        expected_types = {
            'UserID': models.AutoField,
            'Slug': models.SlugField,
            'UserAccount': models.OneToOneField,
        }

        found_count = 0

        for attr in user_profile._meta.fields:
            attr_name = attr.name
            

            for expected_attr_name in expected_attributes.keys():
                if expected_attr_name == attr_name:
                    found_count += 1

                    self.assertEqual(type(attr), expected_types[attr_name], f"{FAILURE_HEADER}The type of attribute for '{attr_name}' was '{type(attr)}'; we expected '{expected_types[attr_name]}'. Check your definition of the UserProfile model.{FAILURE_FOOTER}")
                    setattr(user_profile, attr_name, expected_attributes[attr_name])

        self.assertEqual(found_count, len(expected_attributes.keys()), f"{FAILURE_HEADER}In the UserProfile model, we found {found_count} attributes, but were expecting {len(expected_attributes.keys())}. Check your implementation and try again.{FAILURE_FOOTER}")
        user_profile.save()
        
    def test_user_form(self):
        """
        Tests whether UserForm is in the correct place, and whether the correct fields have been specified for it.
        """
        self.assertTrue('UserForm' in dir(forms), f"{FAILURE_HEADER}We couldn't find the UserForm class in magportal's forms.py module. Did you create it in the right place?{FAILURE_FOOTER}")

        user_form = forms.UserForm()
        self.assertEqual(type(user_form.__dict__['instance']), User, f"{FAILURE_HEADER}Your UserForm does not match up to the User model. Check your Meta definition of UserForm and try again.{FAILURE_FOOTER}")

        fields = user_form.fields

        expected_fields = {
            'username': django_fields.CharField,
            'password': django_fields.CharField,
        }

        for expected_field_name in expected_fields:
            expected_field = expected_fields[expected_field_name]

            self.assertTrue(expected_field_name in fields.keys(), f"{FAILURE_HEADER}The field {expected_field_name} was not found in the UserForm form. Check you have complied with the specification, and try again.{FAILURE_FOOTER}")
            self.assertEqual(expected_field, type(fields[expected_field_name]), f"{FAILURE_HEADER}The field {expected_field_name} in UserForm was not of the correct type. Expected {expected_field}; got {type(fields[expected_field_name])}.{FAILURE_FOOTER}")

    
    def test_login_functionality(self):
        
        #Tests the login functionality. A user should be able to log in, and should be redirected to the magportal homepage.
        
        user_object = create_user_object()

        response = self.client.post(reverse('magportal:login'), {'username': 'testuser', 'password': 'testabc123'})

        try:
            self.assertEqual(user_object.id, int(self.client.session['_auth_user_id']), f"{FAILURE_HEADER}We attempted to log a user in with an ID of {user_object.id}, but instead logged a user in with an ID of {self.client.session['_auth_user_id']}. Please check your login() view.{FAILURE_FOOTER}")
        except KeyError:
            self.assertTrue(False, f"{FAILURE_HEADER}When attempting to log in with your login() view, it didn't seem to log the user in. Please check your login() view implementation, and try again.{FAILURE_FOOTER}")

        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}Testing your login functionality, logging in was successful. However, we expected a redirect; we got a status code of {response.status_code} instead. Check your login() view implementation.{FAILURE_FOOTER}")
        self.assertEqual(response.url, reverse('magportal:home'), f"{FAILURE_HEADER}We were not redirected to the magportal homepage after logging in. Please check your login() view implementation, and try again.{FAILURE_FOOTER}")

    #activate test when index view exists/when login redirects to something else than index
    
    def test_bad_request(self):
        """
        Tries to access the membership view when not logged in.
        This should redirect the user to the magazines page.
        """
        response = self.client.get(reverse('magportal:membership'))

        self.assertEqual(response.status_code, 302, f"{FAILURE_HEADER}We tried to access a restricted view when not logged in. We expected to be redirected, but were not. Check your restricted() view.{FAILURE_FOOTER}")
        
    def test_middleware_present(self):
        """
        Tests to see if the SessionMiddleware is present in the project configuration.
        """
        self.assertTrue('django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE)

    def test_session_app_present(self):
        """
        Tests to see if the sessions app is present.
        """
        self.assertTrue('django.contrib.sessions' in settings.INSTALLED_APPS)

def create_user_object():
    """
    Helper function to create a User object.
    """
    user = User.objects.get_or_create(username='testuser',
                                      first_name='Test',
                                      last_name='User',
                                      email='test@test.com')[0]
    user.set_password('testabc123')
    user.save()

    return user 

class LoginTests(TestCase):
    
    def test_logged_in_links(self):
        
        #Checks for links that should only be displayed when the user is logged in.
        
        user_object = create_user_object()
        self.client.login(username='testuser', password='testabc123')
        content = self.client.get(reverse('magportal:home')).content.decode()

        # These should not be present.
        self.assertTrue('href="/login/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/register/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")

    def test_logged_out_links(self):
        
        #Checks for links that should only be displayed when the user is not logged in.
        
        content = self.client.get(reverse('magportal:browse_magazines')).content.decode()
        
        # These should not be present.
        self.assertTrue('href="/codes/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
        self.assertTrue('href="/edit_profile/"' not in content, f"{FAILURE_HEADER}Please check the links in your base.html have been updated correctly to change when users log in and out.{FAILURE_FOOTER}")
             

class ViewTests(TestCase):
    
    def setUp(self):
        self.project_base_dir = os.getcwd()
        self.templates_dir = os.path.join(self.project_base_dir, 'template')
        self.magportal_templates_dir = os.path.join(self.templates_dir, 'magportal')
        
    def test_views(self):

        """
        Ensures views work as intended...
        """
        #popular/new workouts/exercises
        
        browse_magazines = self.client.get(reverse('magportal:browse_magazines'))
       
        BM_content = browse_magazines.content.decode()
        
        magazine_list = Magazine.objects.all()
          
        print(BM_content)
        self.assertTrue('results' not in BM_content, f"{FAILURE_HEADER}The browse_magazines view should use 'results' in its context dictionary.{FAILURE_FOOTER}")
        self.assertTrue('cats' not in BM_content, f"{FAILURE_HEADER}The browse_magazines view should use 'cats' in its context dictionary.{FAILURE_FOOTER}")
        
        self.assertEqual(list(magazine_list), list(browse_magazines.context['results']), f"{FAILURE_HEADER}Your browse_magazines() view does not pass the magazine list into its context dictionary{FAILURE_FOOTER}")
        
        #register
        
        register = self.client.get(reverse('magportal:register'))
        register_content = register.content.decode()
        
        self.assertTrue('user_form' not in register_content, f"{FAILURE_HEADER}The register() view context dictionary should have a 'user_form' variable.{FAILURE_FOOTER}")
        
        
   