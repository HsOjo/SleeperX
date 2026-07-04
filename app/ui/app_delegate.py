"""NSApplicationDelegate + menu target/action bridge.

Thin NSObject that forwards AppKit callbacks to the plain-Python Controller.
Kept minimal so the business/UI logic stays testable outside PyObjC.
"""
from __future__ import annotations

import objc
from AppKit import (NSObject, NSApplication,
                    NSApplicationActivationPolicyAccessory)
from Foundation import NSTimer, NSRunLoop, NSRunLoopCommonModes


class AppDelegate(NSObject):
    def initWithController_(self, controller):
        self = objc.super(AppDelegate, self).init()
        if self is None:
            return None
        self.controller = controller
        self._timer = None
        return self

    def applicationDidFinishLaunching_(self, notification):
        NSApplication.sharedApplication().setActivationPolicy_(
            NSApplicationActivationPolicyAccessory)
        self.controller.attach_statusbar(self)
        self.controller.start()
        self._timer = NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
            1.0, True, lambda timer: self.controller.tick())
        NSRunLoop.currentRunLoop().addTimer_forMode_(self._timer, NSRunLoopCommonModes)

    def applicationWillTerminate_(self, notification):
        if self._timer is not None:
            self._timer.invalidate()
            self._timer = None
        self.controller.shutdown()

    def menuAction_(self, sender):
        key = sender.representedObject()
        if key is not None:
            self.controller.on_menu(str(key))
