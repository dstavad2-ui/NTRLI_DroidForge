[app]
title = NTRLI_DroidForge
package.name = ntrlidroidforge
package.domain = org.ntrli
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# --- Requirements ---
requirements = python3, kivy==2.3.0, requests, certifi

# --- Toolchain Locks ---
android.api = 33
android.minapi = 21
android.sdk = 33
android.build_tools_version = 33.0.2
android.ndk = 25b
android.ndk_api = 21

# --- Logic Locks ---
android.skip_update = True
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = master
log_level = 2
