#from odoo.addons.website.tools import get_video_embed_code
from odoo.addons.web_editor.tools import get_video_embed_code#16
from odoo import api, fields, models, tools
import odoo
import re
import werkzeug

#def get_video_embed_code_custom(video_url):#16
#    
#    if not video_url:
#        return False

#    validURLRegex = r'^(http:\/\/|https:\/\/|\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'

#    ytRegex = r'^(?:(?:https?:)?\/\/)?(?:www\.)?(?:youtu\.be\/|youtube(-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((?:\w|-){11})(?:\S+)?$'
#    vimeoRegex = r'\/\/(player.)?vimeo.com\/([a-z]*\/)*([0-9]{6,11})[?]?.*'
#    dmRegex = r'.+dailymotion.com\/(video|hub|embed)\/([^_]+)[^#]*(#video=([^_&]+))?'
#    igRegex = r'(.*)instagram.com\/p\/(.[a-zA-Z0-9]*)'
#    ykuRegex = r'(.*).youku\.com\/(v_show\/id_|embed\/)(.+)'

#    if not re.search(validURLRegex, video_url):
#        return False
#    else:
#        embedUrl = False
#        ytMatch = re.search(ytRegex, video_url)
#        vimeoMatch = re.search(vimeoRegex, video_url)
#        dmMatch = re.search(dmRegex, video_url)
#        igMatch = re.search(igRegex, video_url)
#        ykuMatch = re.search(ykuRegex, video_url)

#        if ytMatch and len(ytMatch.groups()[1]) == 11:
#            embedUrl = '//www.youtube%s.com/embed/%s?autoplay=1&mute=1&rel=1&loop=1&controls=1&fs=0&modestbranding=1' % (ytMatch.groups()[0] or '', ytMatch.groups()[1])
#        elif vimeoMatch:
#            embedUrl = '//player.vimeo.com/video/%s?autoplay=1&muted=1' % (vimeoMatch.groups()[2])
#        elif dmMatch:
#            embedUrl = '//www.dailymotion.com/embed/video/%s?autoplay=1&mute=1&controls=1&ui-logo=1&sharing-enable=1' % (dmMatch.groups()[1])
#        elif igMatch:
#            embedUrl = '//www.instagram.com/p/%s/embed/' % (igMatch.groups()[1])
#        elif ykuMatch:
#            ykuLink = ykuMatch.groups()[2]
#            if '.html?' in ykuLink:
#                ykuLink = ykuLink.split('.html?')[0]
#            embedUrl = '//player.youku.com/embed/%s' % (ykuLink)
#        else:
#            embedUrl = video_url
#        return '<iframe class="embed-responsive-item" src="%s" allowFullScreen="true" allow="autoplay" frameborder="0"></iframe>' % embedUrl

class Website(models.Model):
    _inherit = "website"


    def custom_embded_video(self,video_url):#16
#        res = get_video_embed_code_custom(video_url)
        res = get_video_embed_code(video_url)
        return res
