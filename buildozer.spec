[app]
title = NTRLI DroidForge
package.name = droidforge
package.domain = org.ntrli

source.dir = .
source.include_exts = py,kv,png,jpg,json,txt

version = 0.1.0

requirements =
    python3,
    kivy,
    kivymd

orientation = portrait

fullscreen = 0

icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# -----------------------------
# CRITICAL: DO NOT USE 36.x
# -----------------------------


android.permissions =
    INTERNET

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True

android.gradle_dependencies =

android.enable_androidx = True



android.accept_sdk_license = True

android.private_storage = True

android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a
android.skip_update = True

android.logcat_filters = *:S python:D

android.debuggable = True
