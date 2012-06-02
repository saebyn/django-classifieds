
Installation
============

1. Put the 'classifieds' directory somewhere on your python path.

2. Install and configure the packages in requirements.txt.

3. Add:

  'classifieds',
  'paypal.standard.ipn',
  'registration',
  'profiles',
  'django.contrib.humanize',
  'sorl.thumbnail'

  and optionally 'south'

  to your `INSTALLED_APPS`.

4. Set your LOGIN_URL = '/registration/login/' and LOGOUT_URL = '/registration/logout/'
