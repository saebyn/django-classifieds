# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ImageFormat'
        db.create_table('classifieds_imageformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('classifieds', ['ImageFormat'])

        # Adding model 'Category'
        db.create_table('classifieds_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('template_prefix', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('enable_contact_form_upload', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contact_form_upload_max_size', self.gf('django.db.models.fields.IntegerField')(default=1048576)),
            ('contact_form_upload_file_extensions', self.gf('django.db.models.fields.CharField')(default='txt,doc,odf,pdf', max_length=200)),
            ('images_max_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('images_max_width', self.gf('django.db.models.fields.IntegerField')(default=1024)),
            ('images_max_height', self.gf('django.db.models.fields.IntegerField')(default=1024)),
            ('images_max_size', self.gf('django.db.models.fields.IntegerField')(default=1048576)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('sortby_fields', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('sort_order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('classifieds', ['Category'])

        # Adding M2M table for field images_allowed_formats on 'Category'
        db.create_table('classifieds_category_images_allowed_formats', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm['classifieds.category'], null=False)),
            ('imageformat', models.ForeignKey(orm['classifieds.imageformat'], null=False))
        ))
        db.create_unique('classifieds_category_images_allowed_formats', ['category_id', 'imageformat_id'])

        # Adding model 'Subcategory'
        db.create_table('classifieds_subcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Category'])),
        ))
        db.send_create_signal('classifieds', ['Subcategory'])

        # Adding model 'Field'
        db.create_table('classifieds_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Category'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('field_type', self.gf('django.db.models.fields.IntegerField')()),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('max_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('enable_counter', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_wysiwyg', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('options', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('classifieds', ['Field'])

        # Adding model 'Ad'
        db.create_table('classifieds_ad', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Category'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expires_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('classifieds', ['Ad'])

        # Adding model 'AdImage'
        db.create_table('classifieds_adimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Ad'])),
            ('full_photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('thumb_photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('classifieds', ['AdImage'])

        # Adding model 'FieldValue'
        db.create_table('classifieds_fieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Field'])),
            ('ad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Ad'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('classifieds', ['FieldValue'])

        # Adding model 'Pricing'
        db.create_table('classifieds_pricing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
        ))
        db.send_create_signal('classifieds', ['Pricing'])

        # Adding model 'PricingOptions'
        db.create_table('classifieds_pricingoptions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
        ))
        db.send_create_signal('classifieds', ['PricingOptions'])

        # Adding model 'ZipCode'
        db.create_table('classifieds_zipcode', (
            ('zipcode', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('classifieds', ['ZipCode'])

        # Adding model 'SiteSetting'
        db.create_table('classifieds_sitesetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('classifieds', ['SiteSetting'])

        # Adding model 'Payment'
        db.create_table('classifieds_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Ad'])),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=9, decimal_places=2)),
            ('pricing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classifieds.Pricing'])),
        ))
        db.send_create_signal('classifieds', ['Payment'])

        # Adding M2M table for field options on 'Payment'
        db.create_table('classifieds_payment_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('payment', models.ForeignKey(orm['classifieds.payment'], null=False)),
            ('pricingoptions', models.ForeignKey(orm['classifieds.pricingoptions'], null=False))
        ))
        db.create_unique('classifieds_payment_options', ['payment_id', 'pricingoptions_id'])

        # Adding model 'UserProfile'
        db.create_table('classifieds_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('receives_new_posting_notices', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('receives_newsletter', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(default='', max_length=20, blank=True)),
        ))
        db.send_create_signal('classifieds', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'ImageFormat'
        db.delete_table('classifieds_imageformat')

        # Deleting model 'Category'
        db.delete_table('classifieds_category')

        # Removing M2M table for field images_allowed_formats on 'Category'
        db.delete_table('classifieds_category_images_allowed_formats')

        # Deleting model 'Subcategory'
        db.delete_table('classifieds_subcategory')

        # Deleting model 'Field'
        db.delete_table('classifieds_field')

        # Deleting model 'Ad'
        db.delete_table('classifieds_ad')

        # Deleting model 'AdImage'
        db.delete_table('classifieds_adimage')

        # Deleting model 'FieldValue'
        db.delete_table('classifieds_fieldvalue')

        # Deleting model 'Pricing'
        db.delete_table('classifieds_pricing')

        # Deleting model 'PricingOptions'
        db.delete_table('classifieds_pricingoptions')

        # Deleting model 'ZipCode'
        db.delete_table('classifieds_zipcode')

        # Deleting model 'SiteSetting'
        db.delete_table('classifieds_sitesetting')

        # Deleting model 'Payment'
        db.delete_table('classifieds_payment')

        # Removing M2M table for field options on 'Payment'
        db.delete_table('classifieds_payment_options')

        # Deleting model 'UserProfile'
        db.delete_table('classifieds_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'classifieds.ad': {
            'Meta': {'object_name': 'Ad'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Category']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires_on': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'classifieds.adimage': {
            'Meta': {'object_name': 'AdImage'},
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Ad']"}),
            'full_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thumb_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        'classifieds.category': {
            'Meta': {'object_name': 'Category'},
            'contact_form_upload_file_extensions': ('django.db.models.fields.CharField', [], {'default': "'txt,doc,odf,pdf'", 'max_length': '200'}),
            'contact_form_upload_max_size': ('django.db.models.fields.IntegerField', [], {'default': '1048576'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'enable_contact_form_upload': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images_allowed_formats': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['classifieds.ImageFormat']", 'symmetrical': 'False', 'blank': 'True'}),
            'images_max_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'images_max_height': ('django.db.models.fields.IntegerField', [], {'default': '1024'}),
            'images_max_size': ('django.db.models.fields.IntegerField', [], {'default': '1048576'}),
            'images_max_width': ('django.db.models.fields.IntegerField', [], {'default': '1024'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'sort_order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'sortby_fields': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'template_prefix': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'classifieds.field': {
            'Meta': {'object_name': 'Field'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Category']", 'null': 'True', 'blank': 'True'}),
            'enable_counter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_wysiwyg': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field_type': ('django.db.models.fields.IntegerField', [], {}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'max_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'options': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'classifieds.fieldvalue': {
            'Meta': {'object_name': 'FieldValue'},
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Ad']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'classifieds.imageformat': {
            'Meta': {'object_name': 'ImageFormat'},
            'format': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'classifieds.payment': {
            'Meta': {'object_name': 'Payment'},
            'ad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Ad']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['classifieds.PricingOptions']", 'symmetrical': 'False'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paid_on': ('django.db.models.fields.DateTimeField', [], {}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Pricing']"})
        },
        'classifieds.pricing': {
            'Meta': {'ordering': "['price']", 'object_name': 'Pricing'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        'classifieds.pricingoptions': {
            'Meta': {'ordering': "['price']", 'object_name': 'PricingOptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.IntegerField', [], {}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '9', 'decimal_places': '2'})
        },
        'classifieds.sitesetting': {
            'Meta': {'object_name': 'SiteSetting'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'classifieds.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classifieds.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'classifieds.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'receives_new_posting_notices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receives_newsletter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'classifieds.zipcode': {
            'Meta': {'object_name': 'ZipCode'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'zipcode': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['classifieds']
