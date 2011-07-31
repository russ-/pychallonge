from distutils.core import setup
import challonge


setup(name = "pychallonge",
      author = "russ-",
      author_email = "russminus@gmail.com",
      url = "https://github.com/russ-/pychallonge",
      download_url = "https://github.com/russ-/pychallonge/tarball/v1.0",
      version = challonge.__version__,
      packages = [
          'challonge',
      ],
      requires = [
          'dateutil (<2.0)',
      ],
      classifiers = [
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
      ],
)
