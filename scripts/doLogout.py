#!/usr/bin/python
""" Python Pam Example:
if __name__ == "__main__":
    import readline, getpass

    def input_with_prefill(prompt, text):
        def hook():
            readline.insert_text(text)
            readline.redisplay()
        readline.set_pre_input_hook(hook)

        if sys.version_info >= (3,):
            result = input(prompt)
        else:
            result = raw_input(prompt)

        readline.set_pre_input_hook()
        return result


    username = input_with_prefill('Username: ', getpass.getuser())

    # enter a valid username and an invalid/valid password, to verify both failure and success
    pam.authenticate(username, getpass.getpass())
    print('{} {}'.format(pam.code, pam.reason))
"""

from conf import config

import cgi
import pam
import pwd

def main (environ):
    """ Login Handler
    """

    session=environ['beaker.session']

    result=[]

    params=cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ);

    # Destroy session
    session.invalidate()
    result.append('{"data": {"status": "Logged out"}}')

    # Cleanup
    # return the results
    return result[0]

if __name__ == "__main__":
    import os
    for x in main(os.environ):
        print x,
