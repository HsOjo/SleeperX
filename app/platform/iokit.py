"""Low-level IOKit / CoreFoundation bindings via ctypes.

PyObjC's bridging of IOKit C callbacks (IOServiceInterestCallback, the IOPS
notification callback) is fragile, so the event plumbing is done with ctypes
where CFUNCTYPE gives us reliable C function pointers. CFRunLoopGetMain()
returns the process-wide main run loop, which is the very same loop AppKit /
NSRunLoop drive, so sources added here fire on the app's main loop.

NOTE (M0 gate): the clamshell interest notification must be validated on real
hardware/Hackintosh — see lid.py.
"""
from __future__ import annotations

import ctypes

_iokit = ctypes.CDLL('/System/Library/Frameworks/IOKit.framework/IOKit')
_cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')

# --- basic typedefs ---------------------------------------------------------
CFTypeRef = ctypes.c_void_p
CFStringRef = ctypes.c_void_p
CFRunLoopRef = ctypes.c_void_p
CFRunLoopSourceRef = ctypes.c_void_p
io_object_t = ctypes.c_uint32
io_service_t = ctypes.c_uint32
IONotificationPortRef = ctypes.c_void_p
kern_return_t = ctypes.c_int

kIOMainPortDefault = 0
kCFStringEncodingUTF8 = 0x08000100

# --- CoreFoundation ---------------------------------------------------------
_cf.CFStringCreateWithCString.restype = CFStringRef
_cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
_cf.CFRelease.argtypes = [CFTypeRef]
_cf.CFBooleanGetValue.restype = ctypes.c_ubyte
_cf.CFBooleanGetValue.argtypes = [CFTypeRef]
_cf.CFGetTypeID.restype = ctypes.c_ulong
_cf.CFGetTypeID.argtypes = [CFTypeRef]
_cf.CFBooleanGetTypeID.restype = ctypes.c_ulong
_cf.CFNumberGetTypeID.restype = ctypes.c_ulong
_cf.CFNumberGetValue.restype = ctypes.c_ubyte
_cf.CFNumberGetValue.argtypes = [CFTypeRef, ctypes.c_int, ctypes.c_void_p]
_cf.CFRunLoopGetMain.restype = CFRunLoopRef
_cf.CFRunLoopAddSource.argtypes = [CFRunLoopRef, CFRunLoopSourceRef, CFStringRef]
_cf.CFRunLoopRemoveSource.argtypes = [CFRunLoopRef, CFRunLoopSourceRef, CFStringRef]

kCFRunLoopDefaultMode = ctypes.c_void_p.in_dll(_cf, 'kCFRunLoopDefaultMode')
kCFRunLoopCommonModes = ctypes.c_void_p.in_dll(_cf, 'kCFRunLoopCommonModes')

kCFNumberSInt64Type = 4

# --- IOKit ------------------------------------------------------------------
_iokit.IOServiceMatching.restype = ctypes.c_void_p
_iokit.IOServiceMatching.argtypes = [ctypes.c_char_p]
_iokit.IOServiceGetMatchingService.restype = io_service_t
_iokit.IOServiceGetMatchingService.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
_iokit.IORegistryEntryCreateCFProperty.restype = CFTypeRef
_iokit.IORegistryEntryCreateCFProperty.argtypes = [io_object_t, CFStringRef, ctypes.c_void_p, ctypes.c_uint32]
_iokit.IONotificationPortCreate.restype = IONotificationPortRef
_iokit.IONotificationPortCreate.argtypes = [ctypes.c_uint32]
_iokit.IONotificationPortGetRunLoopSource.restype = CFRunLoopSourceRef
_iokit.IONotificationPortGetRunLoopSource.argtypes = [IONotificationPortRef]
_iokit.IONotificationPortDestroy.restype = None
_iokit.IONotificationPortDestroy.argtypes = [IONotificationPortRef]
_iokit.IOObjectRelease.argtypes = [io_object_t]

# IOServiceInterestCallback: void (*)(void *refcon, io_service_t, uint32_t, void *)
INTEREST_CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_void_p, io_service_t, ctypes.c_uint32, ctypes.c_void_p)
_iokit.IOServiceAddInterestNotification.restype = kern_return_t
_iokit.IOServiceAddInterestNotification.argtypes = [
    IONotificationPortRef, io_service_t, ctypes.c_char_p,
    INTEREST_CALLBACK, ctypes.c_void_p, ctypes.POINTER(io_object_t),
]

# IOPowerSources notification callback: void (*)(void *context)
IOPS_CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
_iokit.IOPSNotificationCreateRunLoopSource.restype = CFRunLoopSourceRef
_iokit.IOPSNotificationCreateRunLoopSource.argtypes = [IOPS_CALLBACK, ctypes.c_void_p]

# IOPMAssertion (prevent user-idle system sleep).
IOPMAssertionID = ctypes.c_uint32
kIOPMAssertionLevelOn = 255
kIOPMAssertionLevelOff = 0
kIOPMAssertionTypePreventUserIdleSystemSleep = 'PreventUserIdleSystemSleep'
_iokit.IOPMAssertionCreateWithName.restype = kern_return_t
_iokit.IOPMAssertionCreateWithName.argtypes = [
    CFStringRef, ctypes.c_uint32, CFStringRef, ctypes.POINTER(IOPMAssertionID)]
_iokit.IOPMAssertionRelease.restype = kern_return_t
_iokit.IOPMAssertionRelease.argtypes = [IOPMAssertionID]


def cfstr(text: str) -> CFStringRef:
    return _cf.CFStringCreateWithCString(None, text.encode('utf-8'), kCFStringEncodingUTF8)


def cf_release(ref) -> None:
    # Release raw CoreFoundation pointers obtained through ctypes (Create-rule).
    # PyObjC-managed proxy objects must NOT be passed here; let PyObjC handle
    # their lifetime to avoid double-release crashes.
    if ref:
        _cf.CFRelease(ref)


def add_source_to_main_loop(source: CFRunLoopSourceRef) -> None:
    # Use common modes so IOKit events (battery/lid) are still delivered while
    # a menu is open and the run loop is in event-tracking mode.
    _cf.CFRunLoopAddSource(_cf.CFRunLoopGetMain(), source, kCFRunLoopCommonModes)


def remove_source_from_main_loop(source: CFRunLoopSourceRef) -> None:
    _cf.CFRunLoopRemoveSource(_cf.CFRunLoopGetMain(), source, kCFRunLoopCommonModes)


def read_root_domain_bool(key: str):
    """Read a CFBoolean property from IOPMrootDomain; returns bool or None."""
    matching = _iokit.IOServiceMatching(b'IOPMrootDomain')
    if not matching:
        return None
    entry = _iokit.IOServiceGetMatchingService(kIOMainPortDefault, matching)
    # IOServiceGetMatchingService consumes the matching dictionary; do not release.
    if not entry:
        return None
    try:
        prop = _iokit.IORegistryEntryCreateCFProperty(entry, cfstr(key), None, 0)
        if not prop:
            return None
        try:
            if _cf.CFGetTypeID(prop) == _cf.CFBooleanGetTypeID():
                return bool(_cf.CFBooleanGetValue(prop))
            return None
        finally:
            cf_release(prop)
    finally:
        _iokit.IOObjectRelease(entry)


# Re-export the ctypes handles for callers that need them directly.
iokit = _iokit
cf = _cf
