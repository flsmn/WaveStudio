"""Keep user-requested computation scheduled on macOS; allow idle system sleep."""
import ctypes
import ctypes.util
import logging
import sys


class DarwinActivity:
    # Foundation/NSProcessInfo.h: UserInitiated & ~IdleSystemSleepDisabled.
    OPTIONS = 0x00FFFFFF & ~(1 << 20)

    def __init__(self):
        self.foundation=ctypes.CDLL('/System/Library/Frameworks/Foundation.framework/Foundation')
        self.objc=ctypes.CDLL(ctypes.util.find_library('objc'))
        self.objc.objc_getClass.argtypes=[ctypes.c_char_p];self.objc.objc_getClass.restype=ctypes.c_void_p
        self.objc.sel_registerName.argtypes=[ctypes.c_char_p];self.objc.sel_registerName.restype=ctypes.c_void_p
        self.objc.objc_retain.argtypes=[ctypes.c_void_p];self.objc.objc_retain.restype=ctypes.c_void_p
        self.objc.objc_release.argtypes=[ctypes.c_void_p];self.objc.objc_release.restype=None
        address=ctypes.cast(self.objc.objc_msgSend,ctypes.c_void_p).value
        self.send=ctypes.CFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p)(address)
        self.send_string=ctypes.CFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_char_p)(address)
        self.send_begin=ctypes.CFUNCTYPE(ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint64,ctypes.c_void_p)(address)
        self.send_end=ctypes.CFUNCTYPE(None,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p)(address)
        self.send_integer=ctypes.CFUNCTYPE(ctypes.c_long,ctypes.c_void_p,ctypes.c_void_p)(address)

    def power_state(self):
        process=self.call(self.objc.objc_getClass(b'NSProcessInfo'),'processInfo')
        return {'thermal_state':self.send_integer(process,self.selector('thermalState')),'low_power_mode':bool(self.send_integer(process,self.selector('isLowPowerModeEnabled')))}

    def selector(self,name):return self.objc.sel_registerName(name.encode())
    def call(self,obj,name):return self.send(obj,self.selector(name))
    def pool(self):return self.call(self.call(self.objc.objc_getClass(b'NSAutoreleasePool'),'alloc'),'init')

    def begin(self):
        pool=self.pool();reason=None
        try:
            process=self.call(self.objc.objc_getClass(b'NSProcessInfo'),'processInfo')
            reason=self.send_string(self.call(self.objc.objc_getClass(b'NSString'),'alloc'),self.selector('initWithUTF8String:'),b'Wave Studio user-requested simulation')
            token=self.send_begin(process,self.selector('beginActivityWithOptions:reason:'),self.OPTIONS,reason)
            if not token:raise RuntimeError('NSProcessInfo did not return an activity token.')
            return self.objc.objc_retain(token)
        finally:
            if reason:self.objc.objc_release(reason)
            self.call(pool,'drain')

    def end(self,token):
        pool=self.pool()
        try:
            process=self.call(self.objc.objc_getClass(b'NSProcessInfo'),'processInfo')
            self.send_end(process,self.selector('endActivity:'),token)
        finally:
            self.objc.objc_release(token);self.call(pool,'drain')


class RunActivity:
    """Lazy native integration; no-op on other platforms or unavailable APIs."""
    def __init__(self,backend_factory=DarwinActivity,platform=None):
        self.supported=(sys.platform if platform is None else platform)=='darwin'
        self._factory=backend_factory;self._backend=None;self._token=None;self.failed=False
        self.begins=0;self.ends=0

    @property
    def active(self):return self._token is not None

    def begin(self):
        if self.active or not self.supported or self.failed:return
        try:
            if self._backend is None:self._backend=self._factory()
            self._token=self._backend.begin();self.begins+=1
        except Exception:
            self.failed=True;logging.getLogger(__name__).warning('macOS run activity unavailable',exc_info=True)

    def end(self):
        if not self.active:return
        token,self._token=self._token,None
        try:self._backend.end(token)
        except Exception:logging.getLogger(__name__).warning('Could not end macOS run activity',exc_info=True)
        finally:self.ends+=1
