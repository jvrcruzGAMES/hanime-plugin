import posixpath
import urllib.parse


def _normalize_url(url):
    try:
        parsed = urllib.parse.urlsplit(url)
        hostname = parsed.hostname
        if not parsed.scheme or (parsed.scheme in ('http', 'https') and not hostname):
            raise ValueError
        hostname = hostname.encode('idna').decode('ascii').lower() if hostname else ''
        host = f'[{hostname}]' if ':' in hostname and not hostname.startswith('[') else hostname
        if parsed.port is not None:
            host += f':{parsed.port}'
        userinfo = ''
        if parsed.username is not None:
            userinfo = urllib.parse.quote(parsed.username, safe='%')
            if parsed.password is not None:
                userinfo += ':' + urllib.parse.quote(parsed.password, safe='%')
            userinfo += '@'
        path = parsed.path.replace('\\', '/')
        trailing_slash = path.endswith(('/', '/.', '/..'))
        path = posixpath.normpath(path) if path else ('/' if host else '')
        if path == '.':
            path = ''
        if host and not path.startswith('/'):
            path = '/' + path
        if trailing_slash and not path.endswith('/'):
            path += '/'
        path = urllib.parse.quote(urllib.parse.unquote(path), safe="/%:@!$&'()*+,;=-._~")
        return urllib.parse.urlunsplit((parsed.scheme.lower(), userinfo + host, path, parsed.query, parsed.fragment))
    except (AttributeError, TypeError, UnicodeError, ValueError):
        raise ValueError('Invalid URL') from None


def join_url(base_url, url):
    try:
        if not isinstance(base_url, str) or not isinstance(url, str):
            raise ValueError
        return _normalize_url(urllib.parse.urljoin(_normalize_url(base_url), url.replace('\\', '/')))
    except (TypeError, ValueError):
        raise ValueError('Invalid URL') from None


class URL:
    def __init__(self, url):
        self._href = _normalize_url(url)

    @property
    def href(self):
        return self._href

    @property
    def hostname(self):
        return urllib.parse.urlsplit(self._href).hostname or ''

    @property
    def pathname(self):
        return urllib.parse.urlsplit(self._href).path

    @pathname.setter
    def pathname(self, value):
        if not isinstance(value, str):
            raise ValueError('Invalid value for pathname')
        parsed = urllib.parse.urlsplit(self._href)
        self._href = _normalize_url(urllib.parse.urlunsplit(parsed._replace(path=value)))
