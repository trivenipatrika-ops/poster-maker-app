[app]

title = Poster Maker Pro
package.name = postermakerpro
package.domain = org.osp

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,atlas

version = 1.0

requirements = python3,kivy==2.3.0,pillow,pyjnius,plyer

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,INTERNET,ACCESS_NETWORK_STATE

android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
