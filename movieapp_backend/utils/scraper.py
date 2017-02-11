from googleapiclient.discovery import build
from movieapp_backend.settings import API_KEY, ENGINE_CX

def get_image(title):
  # Build a service object for interacting with the API. Visit
  # the Google APIs Console <http://code.google.com/apis/console>
  # to get an API key for your own application.
  service = build("customsearch", "v1",
            developerKey=API_KEY)

  res = service.cse().list(
      q=title+' movie',
      cx=ENGINE_CX,
      searchType='image',
      num=1
    ).execute()

  try:
    return res['items'][0]['link']
  except:
    return None
