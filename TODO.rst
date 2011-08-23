
* Verify all functionality works with Django 1.3 (see unit testing below)

* Unit testing

  - Views

    1. Ad management

    2. Ad browsing

    3. Checkout / Payment processing

  - Utilities

* Rework how app settings are done.

* Contact form

* Use queueing solution for backend image processing / thumbnail generation.

* Field type model to replace utils.fields_for_ad
  
  - model method that returns the correct form field object

  - initial_data fixture provides useful fieldtypes

* Debug image uploading / replacement during ad posting / edit process.

* Refactor view code

  - Ad editing in create and manage modules should be unified

* Improve i18n support

  - Add support for translations in templates, where not already present

  - Audit code for translatable strings to marked for gettext support

* Refactor the custom category fields system

* Documentation

  - Give a better explanation of the project's structure

* Finish refurbising the base theme

* Replace django-paypal with support for multiple payment gateways (django-bursar?)
