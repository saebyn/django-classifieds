
from django.conf import settings

def setting(name, default):
   return getattr(settings, 'CLASSIFIEDS_' + name, default)
 

NOTICE_ENABLED = setting('NOTICE_ENABLED', False)

# (in number of days)
NOTICE_POSTING_NEW = setting('NOTICE_POSTING_NEW', 1)
NOTICE_POSTING_EXPIRES = setting('NOTICE_POSTING_EXPIRES', 1)

FROM_EMAIL = setting('FROM_EMAIL', 'john@pledge4code.com')

ADS_PER_PAGE = setting('ADS_PER_PAGE', 5)

FORBIDDEN_WORDS = setting('FORBIDDEN_WORDS', [])
