[app]

title = Poster Maker
package.name = postermaker
package.domain = org.osp

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,atlas

version = 1.0

requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
