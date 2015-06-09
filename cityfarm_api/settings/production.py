DEBUG = False

SECRET_FILE = os.path.join(BASE_DIR, 'secret.txt')
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        import random
        SECRET_KEY = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        secret = file(SECRET_FILE, 'w')
        secret.write(SECRET_KEY)
        secret.close()
    except IOError:
        raise Exception("Failed to write secret key to secret file at %s" %
                SECRET_FILE)

ALLOWED_HOSTS = [
    ".media.mit.edu",
    ".media.mit.edu.",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CONN_MAX_AGE = None

ADMINS = (("Douglas Chambers", "leonchambers@mit.edu"),)

