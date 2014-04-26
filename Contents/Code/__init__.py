ROOT_URL        = "http://www.cnet.com"
VID_URL        = "http://www.cnet.com/videos/"
RE_VIDEO_DATA = Regex('"slug":"(.+?)","vanityUrl"')
VIDEO_META        = "http://www.cnet.com/videos/video-meta-xhr/%s/"
# Below is the ilist of shows that have a video player at the top
VIDSHOW_LIST        = ['CNET On Cars', 'The 404', 'XCar', 'Googlicious', 'Next Big Thing', 'The Fix']

####################################################################################################
def Start():

    ObjectContainer.title1 = "CNET TV"
    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
# This uses the EXPLORE CNET VIDEO side menu on the main video page
@handler('/video/cnettv', 'CNET TV')
def MainMenu():

    oc = ObjectContainer()
    
    for item in HTML.ElementFromURL(VID_URL).xpath('//div[@id="videonav"]/ul/li'):
        url = item.xpath('./a/@href')[0]
        url = url.replace('#', '')
        title = item.xpath('./a/text()')[0].strip()

        # Featured and New Releases link both come back to the main page, so we could get rid of one
        if 'Featured' in title or 'New Releases' in title:
            oc.add(DirectoryObject(key=Callback(Videos, title=title, url=VID_URL), title=title))
        elif 'Shows' in title:
            # Send it to a function that gives us a better display of shows with images
            oc.add(DirectoryObject(key=Callback(ShowMenu, title=title), title=title))
        else:
            oc.add(DirectoryObject(key=Callback(Menu, title=title, url=url), title=title))

    return oc

####################################################################################################
# This creates submenus for Products and HowTo menu items
@route('/video/cnettv/menu')
def Menu(title, url):

    oc = ObjectContainer()

    for item in HTML.ElementFromURL(VID_URL).xpath('//ul[@id="%s"]/li/a' %url):
        url = ROOT_URL + item.xpath('./@href')[0]
        title = item.xpath('.//text()')[0].strip()
        oc.add(DirectoryObject(key=Callback(Videos, title=title, url=url), title=title))

    return oc

####################################################################################################
# This creates the show menu using the carousel at the bottom of the main page to include thumbs
@route('/video/cnettv/showmenu')
def ShowMenu(title):

    oc = ObjectContainer(title2=title)

    for item in HTML.ElementFromURL(VID_URL).xpath('//div[@section="carousel"]//ul/li/a'):
        url = ROOT_URL + item.xpath('./@href')[0]
        title = item.xpath('.//div[@class="content"]/h3//text()')[0].strip()
        thumb = item.xpath('.//img/@src')[0]
        try: desc = item.xpath('.//p//text()')[0].strip()
        except: desc = ''
        oc.add(DirectoryObject(key=Callback(Videos, title=title, url=url), title=title, summary=desc, thumb=thumb))

    return oc

####################################################################################################
# This function creates videos for all the different types of videos available.
# Whether that be a top video player json, individual video json, or html. Many pages use more than one of these methods
@route('/video/cnettv/videos')
def Videos(url, title):

    oc = ObjectContainer(title2=title)
    html = HTML.ElementFromURL(url)
    
    # This picks up the json for the video players at the top of some show pages
    try: json_data = html.xpath('//div[@class="cnetVideoPlayer"]/@data-cnet-video-options')[0]
    except: json_data = None
    if json_data:
        player_json = JSON.ObjectFromString(json_data)
        player_list = player_json['videos']
        # The video player on the front page is picked up here but only list one in video none in videos
        if player_list:
            for item in player_list:
                title = item['headline']
                url = item['slug']
                url = VID_URL + url
                desc = item['dek']
                duration = item['duration']
                id = item['mpxId']
                thumb = item['image']['path']
                oc.add(VideoClipObject(url=url, title=title, duration=duration, summary=desc, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

    #This picks up videos that have individual json data including those in shows and the player on the front page
    for video in html.xpath('//*[@data-video]'):
        thumb = video.xpath('.//img/@src')[0]
        video_data = video.xpath('./@data-video')[0]
        video_json = JSON.ObjectFromString(video_data)
        # The json for video player on the first page does not include half the info and does not nestle it in a 'video' 
        # So you have to break this into a try/except to get all the parts 
        try:
            title = video_json['video']['headline']
            url = video_json['video']['slug']
            url = VID_URL + url
            desc = video_json['video']['dek']
            duration = video_json['video']['duration']
        except:
            mpx_id= video_json['mpxId']
            # The front video player does not provide a url for the video just the actual video file, so
            # here we use the mpxId to get the html code used in the page to pull the title, desc, and url from the share link code
            (title, url, desc) = VideoMeta(mpx_id)
            duration = video_json['duration']
        oc.add(VideoClipObject(url=url, title=title, duration=duration, summary=desc, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))
        
    # This picks up other videos that do not have json data    
    for video in html.xpath('//li/a[@class="imageLinkWrapper"]'):
        url = ROOT_URL + video.xpath('./@href')[0]
        title = video.xpath('.//div[@class="headline"]//text()')[0]
        thumb = video.xpath('.//img/@src')[0]
        duration = Datetime.MillisecondsFromString(video.xpath('.//span[@class="assetDuration"]//text()')[0])
        date = Datetime.ParseDate(video.xpath('.//span[@class="assetDate"]//text()')[0].strip())
        oc.add(VideoClipObject(url=url, title=title, duration=duration, originally_available_at = date, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

    return oc

#####################################################################################################
# This gets the title, url and description from the share video info that is produced on the page using the VIDEO_META url for each video
@route('/video/cnettv/videometa')
def VideoMeta(mpx_id):

    url = VIDEO_META %mpx_id
    share_data = HTML.ElementFromURL(url).xpath('//ul/@data-sharebar-options')[0]
    video_json = JSON.ObjectFromString(share_data)
    # The video player on the front page uses video while all the players for shows use videos
    title = video_json['title']
    url = video_json['url']
    desc = video_json['description']
    
    return title, url, desc
