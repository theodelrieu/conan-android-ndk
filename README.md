# conan-android-ndk

Build requirement to cross build to Android.

## Setup

Create a profile for cross building and including this package:

**android_profile**
    
    include(default)
   
    [settings]
    os=Android
    os.api_level=21
    compiler=clang
    compiler.version=7.0
    arch=armv7

    [build_requires]
    android-ndk/r18@theodelrieu/testing
    

Go to your project and cross-build your dependency tree with this toolchain:

    conan install . --profile android_profile
