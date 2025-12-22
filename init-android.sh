#!/bin/bash

# NTRLI DroidForge - Android Project Initialization Script
# This creates a complete Android project structure from scratch

set -e

PROJECT_NAME="NTRLI_DroidForge"
PACKAGE_NAME="com.ntrli.droidforge"
MIN_SDK=24
TARGET_SDK=34
COMPILE_SDK=34

echo "🚀 Initializing NTRLI DroidForge Android Project..."
echo ""

# Create project structure
echo "📁 Creating project structure..."
mkdir -p app/src/main/java/com/ntrli/droidforge
mkdir -p app/src/main/res/layout
mkdir -p app/src/main/res/values
mkdir -p app/src/main/res/drawable
mkdir -p app/src/main/res/mipmap-hdpi
mkdir -p app/src/main/res/mipmap-mdpi
mkdir -p app/src/main/res/mipmap-xhdpi
mkdir -p app/src/main/res/mipmap-xxhdpi
mkdir -p app/src/main/res/mipmap-xxxhdpi
mkdir -p gradle/wrapper

# Create settings.gradle.kts
echo "📝 Creating settings.gradle.kts..."
cat > settings.gradle.kts << 'EOF'
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "NTRLI_DroidForge"
include(":app")
EOF

# Create root build.gradle.kts
echo "📝 Creating build.gradle.kts..."
cat > build.gradle.kts << 'EOF'
plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "2.0.0" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}
EOF

# Create app/build.gradle.kts
echo "📝 Creating app/build.gradle.kts..."
cat > app/build.gradle.kts << EOF
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "$PACKAGE_NAME"
    compileSdk = $COMPILE_SDK

    defaultConfig {
        applicationId = "$PACKAGE_NAME"
        minSdk = $MIN_SDK
        targetSdk = $TARGET_SDK
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
}
EOF

# Create proguard-rules.pro
cat > app/proguard-rules.pro << 'EOF'
# Add project specific ProGuard rules here.
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
EOF

# Create AndroidManifest.xml
echo "📝 Creating AndroidManifest.xml..."
cat > app/src/main/AndroidManifest.xml << EOF
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.NTRLIDroidForge"
        tools:targetApi="31">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.NTRLIDroidForge">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
EOF

# Create MainActivity.kt
echo "📝 Creating MainActivity.kt..."
cat > app/src/main/java/com/ntrli/droidforge/MainActivity.kt << 'EOF'
package com.ntrli.droidforge

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.TextView

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        val textView = findViewById<TextView>(R.id.textView)
        textView.text = "🌿 NTRLI DroidForge\n\nBuilt with precision.\nNo compromises."
    }
}
EOF

# Create activity_main.xml
echo "📝 Creating activity_main.xml..."
cat > app/src/main/res/layout/activity_main.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#E8F5E9"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="NTRLI DroidForge"
        android:textSize="24sp"
        android:textColor="#1B5E20"
        android:textStyle="bold"
        android:gravity="center"
        android:padding="32dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
EOF

# Create strings.xml
echo "📝 Creating strings.xml..."
cat > app/src/main/res/values/strings.xml << 'EOF'
<resources>
    <string name="app_name">NTRLI DroidForge</string>
</resources>
EOF

# Create colors.xml
cat > app/src/main/res/values/colors.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary">#4CAF50</color>
    <color name="primary_dark">#388E3C</color>
    <color name="accent">#8BC34A</color>
    <color name="background">#E8F5E9</color>
    <color name="text">#1B5E20</color>
    <color name="white">#FFFFFF</color>
    <color name="black">#000000</color>
</resources>
EOF

# Create themes.xml
cat > app/src/main/res/values/themes.xml << 'EOF'
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.NTRLIDroidForge" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <item name="colorPrimary">@color/primary</item>
        <item name="colorPrimaryDark">@color/primary_dark</item>
        <item name="colorAccent">@color/accent</item>
        <item name="android:statusBarColor">@color/primary_dark</item>
    </style>
</resources>
EOF

# Create gradle.properties
echo "📝 Creating gradle.properties..."
cat > gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
android.nonTransitiveRClass=false
EOF

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Built application files
*.apk
*.ap_
*.aab

# Files for the ART/Dalvik VM
*.dex

# Java class files
*.class

# Generated files
bin/
gen/
out/
release/

# Gradle files
.gradle/
build/
*/build/

# Local configuration file
local.properties

# Android Studio
*.iml
.idea/
.DS_Store
/captures
.externalNativeBuild
.cxx

# Keystore files
*.jks
*.keystore

# Google Services
google-services.json

# Version control
*.orig
*.rej
EOF

echo ""
echo "✅ Android project structure created successfully!"
echo ""
echo "📦 Project: $PROJECT_NAME"
echo "📦 Package: $PACKAGE_NAME"
echo "🎯 Min SDK: $MIN_SDK"
echo "🎯 Target SDK: $TARGET_SDK"
echo ""
echo "🔧 Next steps:"
echo "  1. Install Gradle wrapper:"
echo "     gradle wrapper --gradle-version 8.9"
echo ""
echo "  2. Build the project:"
echo "     ./gradlew assembleDebug"
echo ""
echo "  3. Commit to Git:"
echo "     git add ."
echo "     git commit -m 'Initialize Android project structure'"
echo "     git push"
echo ""
echo "🚀 Your NTRLI DroidForge project is ready!"
echo ""
