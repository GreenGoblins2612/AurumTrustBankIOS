[app]

# (str) Title of your application
title = Aurum Trust Bank

# (str) Package name
package.name = aurumtrustbank

# (str) Package domain (needed for android/ios packaging)
package.domain = org.aurum

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,db

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements for iOS
requirements = python3,kivy,sqlite3,numpy,matplotlib

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# -----------------------------------------------------------------------------
# iOS specific (kivy-ios / toolchain)
# -----------------------------------------------------------------------------

# (str) iOS bundle identifier
ios.bundle_identifier = org.aurum.aurumtrustbank

# (str) iOS codesign identity (leave blank for simulator / untrusted dev build)
ios.codesign.identity = 

# (str) iOS development team (leave blank if unsigned / simulator)
ios.codesign.development_team = 

# (list) iOS frameworks to link with
ios.frameworks = 

# -----------------------------------------------------------------------------
# Buildozer
# -----------------------------------------------------------------------------
[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with compiler output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
