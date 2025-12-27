[app]
# (Title and package names as per your project)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.build_tools_version = 33.0.2
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# CRITICAL: Prevent Buildozer from overriding our manual SDK setup
android.skip_update = True
android.accept_sdk_license = True
