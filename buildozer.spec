[app]

title = NTRLI DroidForge
package.name = ntrlidroidforge
package.domain = org.ntrli

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,json,yaml,ini

version = 0.1

requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,requests,pyyaml,certifi,charset-normalizer,idna,urllib3,chardet,filetype,six

orientation = portrait
fullscreen = 1

icon.filename = %(source.dir)s/icon.png

entrypoint = main.py


[buildozer]

log_level = 2
warn_on_root = 1


[app:android]

# CRITICAL FIX — android.api (NOT android.sdk)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a, armeabi-v7a

android.permissions = INTERNET

android.allow_backup = True

android.gradle_dependencies = \
    androidx.appcompat:appcompat:1.6.1

android.enable_androidx = True

android.accept_sdk_license = True

android.debug = True
