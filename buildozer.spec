# buildozer.spec

[app]

title = DroidForge
package.name = droidforge
package.domain = org.ntrli

source.dir = .
source.include_exts = py,png,jpg,kv,json

version = 0.1

requirements = python3,kivy

orientation = portrait

fullscreen = 1

android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2

android.sdk_path = ${ANDROID_SDK_ROOT}
android.ndk_path = ${ANDROID_SDK_ROOT}/ndk/25.1.8937393
android.accept_sdk_license = True

android.archs = arm64-v8a

android.permissions = INTERNET

[buildozer]

log_level = 2
warn_on_root = 1
