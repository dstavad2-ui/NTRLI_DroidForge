[app]

# (str) Title of your application
title = NTRLI App

# (str) Package name
package.name = ntrli

# (str) Package domain (needed for Android)
package.domain = org.ntrli

# (str) Source code where the main.py lives
source.dir = .

# (list) File extensions to include
source.include_exts = py,kv,png,jpg,atlas

# (list) Files/dirs to exclude
#source.exclude_dirs = tests, bin

# Application version
version = 0.1

# (list) Application requirements
requirements = python3,kivy

# Supported orientation
orientation = portrait

# Android specific

# (int) Android API target
android.api = 33

# (int) Minimum Android API your APK will support
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (int) Android NDK API level
android.ndk_api = 21

# (str) Android build tools version
android.build_tools_version = 33.0.2

# (list) Android architectures to build for
android.archs = arm64-v8a,armeabi-v7a

# (bool) Skip Buildozer forcing an update of Android SDK – CI safe
android.skip_update = True

# (bool) Automatically accept Android SDK licenses (CI safe)
android.accept_sdk_license = True

# (str) Android entry point (default provided by Buildozer-p4a)
#android.entrypoint = org.kivy.android.PythonActivity

# Android permissions (optional, can add more)
android.permissions = INTERNET

[buildozer]

# (int) Log level: (0 = errors only, 1 = warnings, 2 = info, 3 = debug)
log_level = 2

# (int) Warn if buildozer run as root
warn_on_root = 1

# (str) Directory for build outputs
#build_dir = ./.buildozer

# (str) Directory for APK outputs
#bin_dir = ./bin
