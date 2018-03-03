# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='openpharma',
      version='0.1',
      description="Parse results from trusted sources of informations about open \
          chemist's shops and sort by distance from your position.",
      url='https://github.com/manuelep/openpharma',
      author='Manuele Pesenti',
      author_email='manuele@inventati.org',
      license='MIT',
      packages=['openpharma'],
      install_requires = ['geocoder>=1.37.0','lxml', 'geopy', 'geojson'],
      entry_points = {
        'console_scripts': ['openpharma-nearest=openpharma.bin.command_line:main'],
      },
      zip_safe=False)
