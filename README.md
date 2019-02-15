# conan-android-ndk

Build requirement to cross build to Android.

## Setup

Since this package is not *yet* on conan-center, you must either:

1. Add my Bintray remote
1. Clone/fork this repository and create the package yourself

Here is how to add the remote:

```shell
$ conan remote add theodelrieu https://api.bintray.com/conan/theodelrieu/conan-repo
```

Now, create a profile for cross building and including this package:

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

    conan install . --profile android_profile --build missing
