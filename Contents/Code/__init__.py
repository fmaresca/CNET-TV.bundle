COLLECTION_FEED = 'https://feed.cnet.com/feed/river?version=3_0&contentTypes=content_video&collection=%s&locale=us&start=0&edition=us&release=3.8.2&d=iPad4,4&limit=30&version=3_3'
COLLECTIONS = [
	{'title': 'New Releases', 'collection_id': None},
	{'title': 'Apple Byte', 'collection_id': 'b1a9dea1-31dc-4a54-88f7-cd7d6cde4bae'},
	{'title': 'Carfection', 'collection_id': 'b43987f2-16f6-4f51-9156-871c2def5110'},
	{'title': 'CNET Top 5', 'collection_id': '62f3b410-203f-49d9-b99b-fd2c2c2da1a2'},
	{'title': 'CNET Update', 'collection_id': '8cd2040c-3418-4f94-8b69-f04447141857'},
	{'title': 'Googlicious', 'collection_id': '4416863f-854f-45bc-a9c2-d6c1ca732bdf'},
	{'title': 'How To', 'collection_id': '043b8a15-f01d-441a-8401-7db7466c3747'},
	{'title': 'Netpicks', 'collection_id': 'eee6e8de-9fdf-4c2c-9979-79a08531a1c4'},
	{'title': 'Next Big Thing', 'collection_id': '978ae22f-1c7a-4fe9-9d8f-c2cff67bbe32'},
	{'title': 'News', 'collection_id': '040fa0bc-bf08-43dc-ac3d-ee7869a9fc85'},
	{'title': 'On Cars', 'collection_id': '51f1fed7-3716-4593-8096-eb8865d0f2ce'},
	{'title': 'Prizefight', 'collection_id': 'd53a83ea-bdb0-48a4-a88d-f23a5502f7d0'}
]

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

####################################################################################################
def Start():

    ObjectContainer.title1 = 'CNET'
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'CNET/20161207.3.8.2.60 CFNetwork/808.1.4 Darwin/16.1.0'

####################################################################################################
@handler('/video/cnettv', 'CNET', thumb=ICON, art=ART)
def MainMenu():

    oc = ObjectContainer()

    for collection in COLLECTIONS:

        oc.add(DirectoryObject(
            key = Callback(Collection, title=collection['title'], collection_id=collection['collection_id']),
            title = collection['title']
        ))

    return oc

####################################################################################################
@route('/video/cnettv/collection')
def Collection(title, collection_id):

    oc = ObjectContainer(title2=title)

    if collection_id:
        url = COLLECTION_FEED % (collection_id)
    else:
        url = COLLECTION_FEED.replace('&collection=%s', '')

    json_obj = JSON.ObjectFromURL(url)

    for video in json_obj['river']['items']['item']:

        if video['assetId'] == '' or not video['permalink'].startswith('https://'):
            continue

        oc.add(VideoClipObject(
            url = video['permalink'],
            title = video['headline'],
            summary = video['description'],
            originally_available_at = Datetime.ParseDate(video['timestamp']).date(),
            thumb = Resource.ContentsOfURLWithFallback(url=video['defaultPhoneReviewGalleryImageUrl'])
        ))

    return oc
