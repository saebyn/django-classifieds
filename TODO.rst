
* Make the app a proper python package (setup.py, fix install instructions, add to pypi)

* Implement the image upload field type (GH issue #2)

* Skip payment step when a free pricing option is chosen

* Try http://mvpdev.github.com/django-eav/

* Try django-filters for search functionality

  - Fork the project to support EAV fields

* Rework how app settings are done.

* Contact form

* Debug image uploading / replacement during ad posting / edit process. (verify that sorl is working correctly)

* Use queueing solution for backend image processing / thumbnail generation. ??

* Field type model to replace utils.fields_for_ad
  
  - model method that returns the correct form field object

  - initial_data fixture provides useful fieldtypes

* Refactor view code

  - Ad editing in create and manage modules should be unified

* Improve i18n support

  - Add support for translations in templates, where not already present

  - Audit code for translatable strings to marked for gettext support

* Documentation

  - Give a better explanation of the project's structure

* Finish refurbising the base theme

* Replace django-paypal with support for multiple payment gateways (django-bursar?)
