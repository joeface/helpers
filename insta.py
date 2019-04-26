"""Retrieves latest photos for given Instagram accounts

Uses re, json and requests libs

Usage:
from insta import get_profile_photos

Call get_profile_photos with account name as the one string param
get_profile_photos('michaelageev')


Mikhail Ageev, 2019
michaelageev.com
"""

def get_profile_photos(account=None):
	import re
	import json
	import requests

	photos = []
	
	if not account:
		return photos
    
    # Getting HTML content of the profile page for given account
	r = requests.get('https://www.instagram.com/{0}/'.format(account))
	if r.status_code == 200:
		
        # Searches for a GRAPHQL data included
		s = re.search(r'(?:<script type="text/javascript">window._sharedData = )(.*)(?:;</script>)', r.text)
		
		if s:
			try:
				data = json.loads(s.group(1))
				user_data = data['entry_data']['ProfilePage'][0]['graphql']['user']
				photos = []
                
                # Walk through the list with photos and populate result array
				for p in user_data['edge_owner_to_timeline_media']['edges']:
					photo_url = p['node']['display_url']
					count = p['node']['edge_media_preview_like']['count']
					photos.append({'url': photo_url, 'count': count})
					
				return photos
				
			except:
				# Error occured while parsing the data
				return photos
	
	else:
		# Error occured while retrieving the data
		return photos
