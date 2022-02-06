from distutils.core import setup

setup(
    name='Lights Controller',
    version='0.1',
    packages=['lights',],
    install_requires=['numpy==1.22.0', 'pandas==1.3.5', 'pigpio==1.78', 'PyYAML==6.0',
                      'python-dateutil==2.8.2', 'schedule==1.1.0', 'pytz==2021.3', 'PyYAML==6.0',
                      'schedule==1.1.0', 'six==1.16.0', 'rpi-ws281x==4.3.1'],
    description='Light controller for LED strip',
    extras_require={
        'google': ['requests==2.27.1', 'google-api-core==2.4.0', 'google-api-python-client==2.36.0',
                   'google-auth==2.6.0', 'google-auth-httplib2==0.1.0', 'google-auth-oauthlib==0.4.6',
                   'googleapis-common-protos==1.54.0'],
        'web': ['fastapi==0.73.0', 'uvicorn[standard]==0.17.4']
    },

    author='Alejandro Sanchez',
    author_email='asramirez@gmail.com',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
    scripts=['scripts/run_lights_controller.py',]
)
