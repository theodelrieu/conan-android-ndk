from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add(settings={"os": "Android", "os.api_level": "21", "arch": "armv7", "compiler": "clang", "compiler.version": "7.0", "compiler.libcxx": "libc++"},
                options={"android-ndk:libcxx": "shared", "android-ndk:arm_mode": "thumb", "android-ndk:neon": "True"})
    builder.add(settings={"os": "Android", "os.api_level": "28", "arch": "armv8", "compiler": "clang", "compiler.version": "7.0", "compiler.libcxx": "libc++"})
    builder.run()
