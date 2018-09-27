# Those variables will be used by the Android NDK CMake Toolchain later on
set(ANDROID_ABI $ENV{CONAN_ANDROID_ABI})
set(ANDROID_NATIVE_API_LEVEL $ENV{CONAN_ANDROID_NATIVE_API_LEVEL})
set(ANDROID_ARM_MODE $ENV{CONAN_ANDROID_ARM_MODE})
set(ANDROID_ARM_NEON $ENV{CONAN_ANDROID_ARM_NEON})
set(ANDROID_STL $ENV{CONAN_ANDROID_STL})

# Those variables are not set by the NDK CMake toolchain, but
# CMAKE_<LANG>_STANDARD_LIBRARIES_INIT is.
# Therefore we must force clear it everytime
unset(CMAKE_C_STANDARD_LIBRARIES CACHE)
unset(CMAKE_CXX_STANDARD_LIBRARIES CACHE)

# This would break every find_* methods if left undefined...
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# Finally, include the Android NDK CMake Toolchain
include(${CMAKE_CURRENT_LIST_DIR}/build/cmake/android.toolchain.cmake)
