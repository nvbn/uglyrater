import httplib
import re
import vkontakte
import sys
sys.path.append('../../uglyweb/')
from uglyweb import settings

vk = vkontakte.API(settings.VK_ID, settings.VK_SECRET)


class ProfileNotFound(Exception):
    def __init__(self, name):
        self.name = name
        super(ProfileNotFound, self).__init__()

    def __repr__(self):
        return 'Profile with data: %s not found!' % self.name


def get_profile(name):
    """Get profile from VK api"""
    try:
        return vk.getProfiles(uids=name,
            fields='uid, first_name, last_name, photo'
        )[0]
    except IndexError:
        raise ProfileNotFound(name)


def check_url(addr, name):
    """Check url exist"""
    conn = httplib.HTTPConnection(addr)
    conn.request('GET', name)
    response = conn.getresponse()
    return response.status == 200


def get_name_from_url(url):
    """Get fb or vk name from url"""
    vk = re.search(r'([^v]*)(vk\.com|vkontakte\.ru)\/([^\/]*)(.*)', url)
    if vk:
        vk_name = vk.group(3)
        if vk_name and check_url('vk.com', vk_name):
            return vk_name
    raise ProfileNotFound(url)
