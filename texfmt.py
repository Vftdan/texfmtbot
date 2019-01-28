import json as _json

class _stack:
    __slots__ = ('_data',)
    def __init__(self, src=[]):
        self._data = list(src)
    def __len__(self):
        return len(self._data)
    def __iter__(self):
        return iter(self._data)
    def push(self, val):
        self._data += [val]
    def peek(self, ind=0):
        return self._data[-1 - ind]
    def pop(self):
        d = self._data
        d, v = d[:-1], d[-1]
        self._data = d
        return v

class TexException(BaseException):
    pass

texchars = _json.load(open('texchars.json'))

def _eschtmlchar(c):
    if c == '&':
        return '&amp;'
    if c == '<':
        return '&lt;'
    if c == '>':
        return '&gt;'
    if c == '"':
        return '&quot;'
    return c

def _eschtml(txt):
    return ''.join(map(_eschtmlchar, txt))

def _tagsopen(*tags):
    return ''.join(map(lambda tn: '<{0}>'.format(tn), tags))

def _tagsclose(*tags):
    return ''.join(map(lambda tn: '</{0}>'.format(tn), tags))

def _isalpha(c):
    return 'A' <= c <= 'Z' or 'a' <= c <= 'z'

def tex2html(src, nocombine=False):
    flag_it = False
    flag_bf = False
    flag_tt = False
    res = _stack()
    states = _stack()
    handler = res.push
    mode_cmd = False
    mode_acmd = False
    acmd = ''
    def allopen():
        t = []
        if flag_it:
            t += ['i']
        if flag_bf:
            t += ['b']
        if flag_tt:
            t += ['pre']
        res.push(_tagsopen(*t))
    def allclose():
        t = []
        if flag_tt:
            t += ['pre']
        if flag_bf:
            t += ['b']
        if flag_it:
            t += ['i']
        res.push(_tagsclose(*t))
    def hrefhandler(href):
        nonlocal handler
        if '<' in href:
            raise TexException('Formating in url is not allowed')
        allopen()
        popstate()
        allclose()
        def newhandler(txt):
            #allclose()
            runhandler('<a href="{0}">{1}</a>'.format(href, txt))
            if nocombine:
                allopen()
                popstate()
                allclose()
        if nocombine:
            allopen()
            pushstate()
            runmacro('rm')
            allclose()
        handler = newhandler
    def runmacro(m):
        nonlocal handler, flag_it, flag_bf, flag_tt
        if m == 'it' or m == 'sl':
            allclose()
            flag_it = True
            if nocombine:
                flag_bf = False
                flag_tt = False
            allopen()
            return
        if m == 'bf':
            allclose()
            flag_bf = True
            if nocombine:
                flag_it = False
                flag_tt = False
            allopen()
            return
        if m == 'tt':
            allclose()
            flag_tt = True
            if nocombine:
                flag_it = False
                flag_bf = False
            allopen()
            return
        if m == 'rm':
            allclose()
            flag_it = False
            flag_bf = False
            flag_tt = False
            allopen()
            return
        if m == 'href':
            pushstate()
            runmacro('rm')
            handler = hrefhandler
            return
        if m in texchars:
            res.push(_eschtml(texchars[m]))
            return
        raise TexException('Unknown macro: {0}'.format(m))
    def runhandler(s):
        nonlocal handler
        h, handler = handler, res.push
        h(s)
    def pushstate():
        nonlocal res, handler
        allclose()
        states.push((res, handler, flag_it, flag_bf, flag_tt))
        res = _stack()
        handler = res.push
        allopen()
    def popstate():
        nonlocal res, handler, flag_it, flag_bf, flag_tt
        if len(states) == 0:
            raise TexException('Unexpected "}"')
        handler('')
        allclose()
        state = states.pop()
        flag_it, flag_bf, flag_tt = state[2:]
        s = ''.join(res)
        handler = state[1]
        res = state[0]
        runhandler(s)
        allopen()
    for c in src:
        if mode_cmd:
            if _isalpha(c):
                acmd = c
                mode_cmd = False
                mode_acmd = True
                continue
            mode_cmd = False
            runmacro(c)
            continue
        if mode_acmd:
            if _isalpha(c):
                acmd += c
                continue
            mode_acmd = False
            a, acmd = acmd, ''
            runmacro(a)
            if c in ' \n\t':
                continue
        if c == '{':
            pushstate()
            continue
        if c == '}':
            popstate()
            continue
        if c == '\\':
            mode_cmd = True
            continue
        runhandler(_eschtml(c))
    while len(states):
        popstate()
    allclose()
    return ''.join(res)
