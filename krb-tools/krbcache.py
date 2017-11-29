#!/bin/env python

import subprocess, os, datetime

class KrbCache(object) :
    
    def __init__(self, principal = None, ccname = None, mintimeleft = 5, aklog = False) :
        if principal :
            self.kinitargs = ['kinit', principal]
        else :
            self.kinitargs = ['kinit']

        if principal and not ccname :
            ccname = '/tmp/krb5cc_' + str(os.getuid()) + '_' + principal
        self.ccname = ccname
        if ccname :
            self.env = self._env
        else :
            self.env = lambda : os.environ
            
        self.mintimeleft = mintimeleft * 60**2
        if aklog :
            self.kinit = self._kinit_aklog
        else :
            self.kinit = self._kinit

    def _env(self) :
        env = dict(os.environ)
        env['KRB5CCNAME'] = self.ccname
        return env

    def popen(self, **kwargs) :
        return subprocess.Popen(env = self.env(), **kwargs)

    def call(self, **kwargs) :
        proc = self.popen(**kwargs)
        stdout, stderr = proc.communicate()
        return proc.poll(), stdout, stderr
    
    def _kinit(self) :
        return self.call(args = self.kinitargs)

    def aklog(self, **kwargs) :
        return self.call(args = ['aklog'], **kwargs)

    def _kinit_aklog(self) :
        exitcode, stdout, stderr = self._kinit()
        if exitcode != 0 :
            return exitcode, stdout, stderr
        return self.aklog()

    def klist(self, **kwargs) :
        return self.call(args = ['klist'], **kwargs)

    def kdestroy(self, **kwargs) :
        return self.call(args = ['kdestroy'], **kwargs)
    
    def _time(self, istart, iend) :
        exitcode, stdout, stderr = self.klist(stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        if exitcode != 0 :
            if stderr :
                raise Exception(stderr)
            else :
                raise Exception('Call to klist failed! Exit code: ' + str(exitcode))
        lastline = filter(None, stdout.split('\n'))[-1].split()
        time = datetime.datetime.strptime(' '.join(lastline[istart:iend]), '%b %d %H:%M:%S %Y')
        return time
    
    def expires(self) :
        return self._time(4, 8)

    def issued(self) :
        return self._time(0, 4)

    def timeleft(self) :
        try :
            expires = self.expires()
        except :
            return datetime.timedelta(0)
        now = datetime.datetime.today()
        return max(datetime.timedelta(0), expires - now)

    def check_kinit(self) :
        if self.timeleft().total_seconds() < self.mintimeleft :
            exitcode, stdout, stderr = self.kinit()
            if 0 != exitcode :
                if stderr :
                    raise Exception(stderr)
                else :
                    raise Exception('Call to kinit failed! Exit code: ' + str(exitcode))
        
    def check_call(self, **kwargs) :
        self.check_kinit()
        return self.call(**kwargs)

    def check_popen(self, **kwargs) :
        self.check_kinit()
        return self.popen(**kwargs)

if __name__ == '__main__' :
    cache = KrbCache('malexand')
    cache.kdestroy()
    #cache.klist()
    #cache.kinit()
    cache.check_call(args = ['ssh', 'lxplus039'])
    print cache.timeleft()
    print cache.expires()
