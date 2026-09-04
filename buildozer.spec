[app]

title = Poster Maker Pro
package.name = postermakerpro
package.domain = org.osp

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,atlas

version = 1.0

requirements = python3,kivy==2.3.0,pillow,kivmob,pyjnius,plyer

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

# Android 13+ ke liye READ_MEDIA_IMAGES zaroori hai (purane Android
# ke liye READ_EXTERNAL_STORAGE bhi rakha hai, taaki dono chalen)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,INTERNET,ACCESS_NETWORK_STATE

android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# AdMob ke liye Google Play Services library aur App ID Manifest me chahiye
android.gradle_dependencies = com.google.android.gms:play-services-ads:23.0.0
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713

android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
