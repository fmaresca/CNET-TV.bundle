import datetime, re

PLUGIN_PREFIX   = "/video/cnettv"
ROOT_URL        = "http://cnettv.cnet.com/"
SEARCH_API_URL  = "http://api.cnet.com/restApi/v1.0/videoSearch?%s=%s"
CNET_PARMS      = "&orderBy=productionDate~desc,createDate~desc&limit=20&iod=images,videoMedia,relatedLink,breadcrumb,relatedAssets,broadcast%2Clowcache&partTag=cntv&showBroadcast=true"
CNET_NAMESPACE  = {'l':'http://api.cnet.com/rest/v1.0/ns'}
PARAM_NAME_MAP  = {'videoId':'videoIds', 'node':'categoryIds', 'videoProfileIds':'franchiseIds', 'videoProfileId':'franchiseIds'}

RE_ONCLICK_ITEMS = Regex("'[^']+'")

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "CNET TV", "icon-default.png", "art-default.jpg")
    ObjectContainer.title1 ="CNET TV"
    ObjectContainer.art = R('art-default.jpg')
    DirectoryObject.thumb=R("icon-default.png")

#####################################  
def MainMenu():
    oc = ObjectContainer()
    videoId = TodaysVideoId()
    oc.add(DirectoryObject(key=Callback(Videos, title="Today", key_param='videoIds', params=videoId), title='Today on CNET'))
  
    for item in HTML.ElementFromURL(ROOT_URL).xpath('//li[@class="expandable"]'):
        title = item.xpath('./a/text()')[0].strip()
        subMenus = []
        for subItem in item.xpath('.//nav/ul/li/a'):
            try:
                onClickItems = [p.strip("'") for p in RE_ONLCICK_ITEMS.findall(subItem.get('onclick'))]
                onClickItems[0] = onClickItems[0].replace(u'\x92',"'")
                subMenus += [onClickItems]
            except:
                pass

            if len(subMenus) > 0:
                oc.add(DirectoryObject(key=Callback(Menu, subMenus=subMenus), title=title))

  return oc

#####################################
def Menu(subMenus):
    oc = ObjectContainer()

    for subMenu in subMenus:
        try:
            title = unicode(subMenu[0])
            key_param = PARAM_NAME_MAP[subMenu[1]]
            params = subMenu[2]
            oc.add(DirectoryObject(key=Callback(Videos, title=title, key_param=key_param, params=params), title=title))
        except:
            pass

  return oc

#####################################
def Videos(title, key_param, params):
    oc = ObjectContainer(title2=title)
    searchUrl = SEARCH_API_URL % (key_param, params) + CNET_PARMS

    for video in XML.ElementFromURL(searchUrl).xpath('//l:Videos/l:Video', namespaces=CNET_NAMESPACE):
        # Only process media items that have video
        if len(video.xpath('./l:VideoMedias', namespaces=CNET_NAMESPACE)) > 0:
            media_url = video.xpath('./l:CnetTvURL', namespaces=CNET_NAMESPACE)[0].text
            title = video.xpath('./l:Title', namespaces=CNET_NAMESPACE)[0].text
            summary = video.xpath('./l:Description', namespaces=CNET_NAMESPACE)[0].text
            images = video.xpath('./l:Images/l:Image', namespaces=CNET_NAMESPACE)
            duration = int(video.xpath('./l:LengthSecs', namespaces=CNET_NAMESPACE)[0].text)*1000
            subtitle = Datetime.ParseDate(video.xpath('./l:CreateDate', namespaces=CNET_NAMESPACE)[0].text).strftime('%a %b %d, %Y')
            oc.add(VideoClipObject(url=media_url, title=title, summary=summary, thumb=Callback(pickThumb, images), tagline=subtitle)

    return oc

#####################################
def TodaysVideoId():
  for script in HTML.ElementFromURL(ROOT_URL).xpath('//script'):
    if script.text != None:
      start = script.text.find('todaysPlaylist')
      if start != -1:
        matches = re.findall(r'[0-9,]+[0-9]+', script.text)
        if len(matches) > 0:
          videoId = matches[0]
          return videoId

  return None

###################################   
def pickVideo(videos):
  pickedBitrate = 0
  pickedURL = None
  for video in videos:
    bitrate = int(video.xpath('./l:BitRate', namespaces=CNET_NAMESPACE)[0].text)
    if bitrate > pickedBitrate:
      url = video.xpath('./l:DeliveryUrl', namespaces=CNET_NAMESPACE)[0].text
      if '.mp4' in url:
        pickedBitrate = bitrate
        pickedURL = url
      else:
        pass
  return pickedURL

#######################################
def pickThumb(images):
  pickedHeight = 0
  pickedThumb = None
  for image in images:
    height = int(image.get("height"))
    if height > pickedHeight:
      pickedThumb = image.xpath('./l:ImageURL', namespaces=CNET_NAMESPACE)[0].text
      pickedHeight = height

  return pickedThumb
