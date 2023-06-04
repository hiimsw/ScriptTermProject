from distutils.core import setup

setup(name="main",
      version='1.0',
      py_modules=['core', 'course_weather_loader', 'document_creator', 'map_loader', 'teller'],

      packages=['assets', 'data', 'api_keys'],
      package_data={
          'assets': ['*.png'],
          'data': ['map_base_html.txt', 'token.json', 'google_oauth_client.json', 'course.xml'],
          'api_keys': ['dummy']
      }
      )
