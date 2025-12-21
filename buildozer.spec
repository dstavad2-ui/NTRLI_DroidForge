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

entrypoint = main.py


[buildozer]

log_level = 2
warn_on_root = 1


[app:android]

# ===== FORCE BUILDOZER TO USE CI SDK (CRITICAL FIX) =====
android.sdk_path = /home/runner/work/_temp/android-sdk
android.ndk_path = /home/runner/work/_temp/android-sdk/ndk/25.1.8937393

android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2
android.ndk = 25b

android.arch = arm64-v8a, armeabi-v7a

android.permissions = INTERNET

android.accept_sdk_license = True
android.skip_update = True
android.enable_androidx = True
android.debug = True
