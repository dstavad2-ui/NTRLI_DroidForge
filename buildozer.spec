[app]
# --- Core Identity ---
title = NTRLI_DroidForge
package.name = ntrli_droidforge
package.domain = org.ntrli

# --- Requirements & Source ---
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
# Add your specific python dependencies here
requirements = python3, kivy, requests

# --- Android Configuration (API 33 Lock) ---
android.api = 33
android.minapi = 21
android.sdk = 33
android.build_tools_version = 33.0.2

# --- NDK Stability Lock ---
android.ndk = 25b
android.ndk_api = 21

# --- Engineering Determinism (CRITICAL) ---
# This prevents Buildozer from trying to update or 
# download tools that conflict with our CI setup.
android.skip_update = True
android.accept_sdk_license = True

# --- Architecture ---
# Building for both modern and older devices
android.archs = arm64-v8a, armeabi-v7a

# --- Gradle & UI ---
android.enable_androidx = True
android.allow_backup = True
# android.presplash_color = #FFFFFF
# android.icon.filename = %(source.dir)s/icon.png
