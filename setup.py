import setuptools

setuptools.setup(name='sal',
                 version='1.0',
                 description='Sal',
                 long_description='Sal - Reporting for Munki',
                 py_modules=['sal.context_processors', 'sal.example_settings', 'sal.urls', 'sal.wsgi'],
                 install_requires=['django'],
                 zip_safe=False)
