
Installation
============

These installation instructions are based on adding `django-classifieds` to an existing ``Django`` project.

1. Put the 'classifieds' directory somewhere on your python path.

2. Install and configure the packages in requirements.txt.

3. Add:

  'classifieds',
  'paypal.standard.ipn',
  'registration',
  'profiles',
  'django.contrib.humanize',
  'sorl.thumbnail',
  'south'

  to your `INSTALLED_APPS` setting.

4. Set your `LOGIN_URL` = '/registration/login/' and `LOGOUT_URL` = '/registration/logout/'

5. Other settings you may wish to change:

   * `LOGIN_REDIRECT_URL`

   * `ACCOUNT_ACTIVATION_DAYS`

   * `PAYPAL_RECEIVER_EMAIL`

..
        See ``extras/projects/settings.py`` for an example.
