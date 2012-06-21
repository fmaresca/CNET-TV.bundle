ROOT_URL        = "http://cnettv.cnet.com/"
SEARCH_API_URL  = "http://api.cnet.com/restApi/v1.0/videoSearch?%s=%s"
CNET_PARAMS     = "&orderBy=productionDate~desc,createDate~desc&limit=20&iod=images,videoMedia,relatedLink,breadcrumb,relatedAssets,broadcast%2Clowcache&partTag=cntv&showBroadcast=true"
CNET_NAMESPACE  = {'l':'http://api.cnet.com/rest/v1.0/ns'}
PARAM_NAME_MAP  = {'videoId':'videoIds', 'node':'categoryIds', 'videoProfileIds':'franchiseIds', 'videoProfileId':'franchiseIds'}

RE_ONCLICK_ITEMS = Regex("'[^']+'")
RE_TODAYS_VIDEO = Regex(r'[0-9,]+[0-9]+')

####################################################################################################
def Main():

    oc = ObjectContainer(content = ContainerContent.Secondary)
    el = HTML.ElementFromURL(ROOT_URL)
    videoId = TodaysVideoId(el)
    oc.add(DirectoryObject(key=Callback(Videos, title="Today", key_param='videoIds', params=videoId), title='Today on CNET'))
  
    for item in el.xpath('//li[@class="expandable"]'):
        title = item.xpath('./a/text()')[0].strip()
        subMenus = []

        for subItem in item.xpath('.//nav/ul/li/a'):
            try:
                onClickItems = [p.strip("'") for p in RE_ONCLICK_ITEMS.findall(subItem.get('onclick'))]
                onClickItems[0] = onClickItems[0].replace(u'\x92',"'")
                subMenus += [onClickItems]
            except:
                pass

        if len(subMenus) > 0:
            oc.add(DirectoryObject(key=Callback(Menu, subMenus=subMenus), title=title))

    return oc

####################################################################################################
@route("menu", subMenus = list)
def Menu(subMenus):

    oc = ObjectContainer(content = ContainerContent.Secondary)

    for subMenu in subMenus:
        try:
            title = unicode(subMenu[0])
            key_param = PARAM_NAME_MAP[subMenu[1]]
            params = subMenu[2]
            oc.add(DirectoryObject(key=Callback(Videos, title=title, key_param=key_param, params=params), title=title))
        except:
            pass

    return oc

####################################################################################################
@route("videos")
def Videos(title, key_param, params):

    oc = ObjectContainer(title2 = title, content = ContainerContent.GenericVideos)
    searchUrl = SEARCH_API_URL % (key_param, params) + CNET_PARAMS

    for video in XML.ElementFromURL(searchUrl).xpath('//l:Videos/l:Video', namespaces=CNET_NAMESPACE):
        # Only process media items that have video
        if len(video.xpath('./l:VideoMedias', namespaces=CNET_NAMESPACE)) > 0:
            thumbs = []
            media_url = video.xpath('./l:CnetTvURL', namespaces=CNET_NAMESPACE)[0].text
            title = video.xpath('./l:Title', namespaces=CNET_NAMESPACE)[0].text
            summary = video.xpath('./l:Description', namespaces=CNET_NAMESPACE)[0].text
            images = video.xpath('./l:Images/l:Image', namespaces=CNET_NAMESPACE)
            thumbs = SortImages(images)
            duration = int(video.xpath('./l:LengthSecs', namespaces=CNET_NAMESPACE)[0].text)*1000
            subtitle = Datetime.ParseDate(video.xpath('./l:CreateDate', namespaces=CNET_NAMESPACE)[0].text).strftime('%a %b %d, %Y')
            oc.add(VideoClipObject(url=media_url, title=title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumbs, fallback="icon-default.png")))

    return oc

####################################################################################################
def TodaysVideoId(el):

    for script in el.xpath('//script'):
        if script.text != None:
            start = script.text.find('todaysPlaylist')
            if start != -1:
                matches = RE_TODAYS_VIDEO.findall(script.text)
                if len(matches) > 0:
                    videoId = matches[0]
                    return videoId

    return None

####################################################################################################
def SortImages(images=[]):

  thumbs = []
  for image in images:
      height = image.get('height')
      url = image.xpath('./l:ImageURL', namespaces=CNET_NAMESPACE)[0].text
      thumbs.append({'height':height, 'url':url})

  sorted_thumbs = sorted(thumbs, key=lambda thumb : int(thumb['height']), reverse=True)
  thumb_list = []
  for thumb in sorted_thumbs:
      thumb_list.append(thumb['url'])

  return thumb_list
