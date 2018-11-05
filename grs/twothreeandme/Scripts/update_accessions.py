# from crsapi import settings
import sys

# from twothreeandme import ttm_functions


try:
    arg = sys.argv[1]

    # message = ttm_functions.update_accessions(arg)
    message = 'test'
except Exception as e:
    e_message = e.message if e.message else ','.join(map(str, e.args))
    message = 'Update Accession Error -   %s' % e_message

print message
