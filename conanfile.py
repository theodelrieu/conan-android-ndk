from conans import ConanFile, tools
import posixpath
import os

ANDROID_ABIS = {"x86": "x86",
                "x86_64": "x86_64",
                "armv7": "armeabi-v7a",
                "armv8": "arm64-v8a"}

SYSROOT_ABIS = {"x86": "x86",
                "x86_64": "x86_64",
                "armv7": "arm",
                "armv8": "arm64"}

TRIPLE_ABIS = {"x86": "i686",
               "x86_64": "x86_64",
               "armv7": "arm",
               "armv8": "aarch64"}

class AndroidNDKConan(ConanFile):
    name = "android-ndk"
    version = "r18"
    license = "APACHE2"
    description = "Android NDK"
    url = "https://github.com/theodelrieu/conan-android-ndk"
    settings = "os_build", "arch_build", "os", "arch", "compiler", "build_type"
    options = { "libcxx": ["static", "shared"], "arm_mode": ["thumb", "arm"], "neon": [True, False] }
    default_options = "libcxx=static", "arm_mode=thumb", "neon=True"
    exports_sources = "android-toolchain.cmake"
    short_paths = True
    no_copy_source = True

    @property
    def zip_folder(self):
        return "android-ndk-%s" % self.version

    def translate_arch(self, arch_map):
        arch_str = str(self.settings.arch)
        return arch_map.get(arch_str, arch_str)

    @property
    def posix_package_folder(self):
        return posixpath.join(*self.package_folder.split('\\'))

    @property
    def host(self):
        if self.settings.os_build == "Windows":
            if self.settings.arch_build == "x86_64":
                return "windows-x86_64"
            return "windows"
        elif self.settings.os_build == "Macos":
            return "darwin-x86_64"
        return "linux-x86_64"

    @property
    def android_abi(self):
        return self.translate_arch(ANDROID_ABIS)

    @property
    def sysroot_abi(self):
        return self.translate_arch(SYSROOT_ABIS)

    @property
    def llvm_triple(self):
        arch = self.translate_arch(TRIPLE_ABIS)
        if self.settings.arch == "armv7":
            suffix = "androideabi"
        else:
            suffix = "android"
        return "%s-none-linux-%s%s" % (arch, suffix, self.settings.os.api_level)

    @property
    def header_triple(self):
        arch = self.translate_arch(TRIPLE_ABIS)
        if self.settings.arch == "armv7":
            suffix = "androideabi"
        else:
            suffix = "android"
        return "%s-linux-%s" % (arch, suffix)

    @property
    def toolchain_triple(self):
        if self.settings.arch in ["x86", "x86_64"]:
            return self.android_abi
        else:
            return self.header_triple

    @property
    def toolchain_name(self):
        return self.header_triple

    def config_options(self):
        if self.settings.arch != "armv7":
            del self.options.arm_mode
            del self.options.neon

        api_level = int(str(self.settings.os.api_level))
        # The NDK's CMake Toolchain file automatically raise the API level to 16
        # It also raises the API level to 21 on 64-bit platform
        # But this does not work well with Conan settings and package IDs...
        # Hence the exceptions
        if api_level < 16:
            raise Exception("Minimum API level supported is 16")
        if api_level < 21 and self.settings.arch in ["x86_64", "armv8"]:
            raise Exception("64-bit platforms require API level 21+")
        if self.settings.compiler != "clang":
            raise Exception("clang is the only supported compiler")
        if self.settings.compiler.version != "7.0":
            raise Exception("clang 7.0 required")
        if self.settings.os_build not in ["Linux", "Macos", "Windows"]:
            raise Exception("Unsupported build machine OS")
        if self.settings.arch_build != "x86_64":
            if self.settings.os_build != "Windows" or self.settings.arch_build != "x86":
                raise Exception("Unsupported build machine architecture")
        if self.settings.os != "Android":
            raise Exception("self.settings.os must be Android")
        if self.settings.arch not in ["armv7", "armv8", "x86", "x86_64"]:
            raise Exception("Arch %s is not supported" % self.settings.arch)

    def source(self):
        urls = {"Windows_x86_64": ["https://dl.google.com/android/repository/android-ndk-%s-windows-x86_64.zip" % self.version,
                                   "7fc0e0f94d86ea389bd18761abdc1bae2c005587"],
                "Windows_x86": ["https://dl.google.com/android/repository/android-ndk-%s-windows-x86.zip" % self.version,
                                "c3422e060b3ea955516e86737bf4237b8482d59a"],
                "Macos_x86_64": ["https://dl.google.com/android/repository/android-ndk-%s-darwin-x86_64.zip" % self.version,
                                 "2070c9a5799671e34b88d383a93af255a5ea260d"],
                "Linux_x86_64": ["https://dl.google.com/android/repository/android-ndk-%s-linux-x86_64.zip" % self.version,
                                 "2ac2e8e1ef73ed551cac3a1479bb28bd49369212"]
        }

        url, sha1 = urls.get("%s_%s" % (self.settings.os_build, self.settings.arch_build))

        tools.download(url, "ndk.zip")
        tools.check_sha1("ndk.zip", sha1)
        tools.unzip("ndk.zip", keep_permissions=True)
        os.unlink("ndk.zip")

    def package(self):
        # some STL headers in experimental/ simply contain an #error
        # This can cause invalid feature detection (via __has_include or similar, e.g. Boost.Asio tries to use experimental/string_view)
        # Therefore, do not copy those files
        files_to_exclude = ["any", "chrono", "numeric", "optional", "ratio", "string_view", "system_error", "tuple"]
        exclude_list = ["*/experimental/%s" % f for f in files_to_exclude]

        self.copy("*", dst="", src=self.zip_folder, keep_path=True, symlinks=True, excludes=exclude_list)
        self.copy("android-toolchain.cmake")

    def package_info(self):
        android_platform = "android-%s" % self.settings.os.api_level
        platform_path = posixpath.join(self.posix_package_folder, "platforms", android_platform, "arch-%s" % self.sysroot_abi)
        # This cannot be considered to be the "real" sysroot, since arch-specific files are in a subfolder
        sysroot_path = posixpath.join(self.posix_package_folder, "sysroot")
        stl_path = posixpath.join(self.posix_package_folder, "sources", "cxx-stl", "llvm-libc++")
        stl_abi_path = posixpath.join(self.posix_package_folder, "sources", "cxx-stl", "llvm-libc++abi")
        toolchain_root_path = posixpath.join(self.posix_package_folder, "toolchains", "%s-4.9" % self.toolchain_triple, "prebuilt", self.host)
        toolchain_bin_path = posixpath.join(toolchain_root_path, self.toolchain_triple, "bin")

        llvm_toolchain_prefix = posixpath.join(self.posix_package_folder, "toolchains", "llvm", "prebuilt", self.host, "bin")

        # All those flags are taken from the NDK's android.toolchain.cmake file.
        # Set C library headers at the end of search path, otherwise #include_next will fail in C++ STL
        compiler_flags = ["-isystem%s" % posixpath.join(stl_abi_path, "include")]
        compiler_flags.append("-isystem%s" % posixpath.join(stl_path, "include"))
        # Find asm files
        compiler_flags.append("-isystem%s" % posixpath.join(sysroot_path, "usr", "include", self.header_triple))
        target = self.llvm_triple
        compiler_flags.append("--target=%s" % target)
        compiler_flags.append("--sysroot=%s" % sysroot_path)
        compiler_flags.extend(["-g", "-DANDROID", "-ffunction-sections", "-funwind-tables", "-fstack-protector-strong", "-no-canonical-prefixes"])
        # --gcc-toolchain is set by CMAKE_<LANG>_COMPILER_EXTERNAL_TOOLCHAIN
        compiler_flags.append("--gcc-toolchain=%s" % toolchain_root_path)

        if self.settings.arch == "armv7":
            if self.options.neon:
                compiler_flags.append("-mfpu=neon")
            compiler_flags.extend(["-march=armv7-a", "-mfloat-abi=softfp", "-mfpu=vfpv3-d16", "-m%s" % self.options.arm_mode])
        elif self.settings.arch == "x86" and int(str(self.settings.os.api_level)) < 24:
            compiler_flags.append("-mstackrealign")

        # disable execstack (default)
        compiler_flags.append("-Wa,--noexecstack")

        # build_type dependent flags
        if self.settings.build_type == "Debug":
            compiler_flags.extend(["-O0", "-fno-limit-debug-info"])
        else:
            compiler_flags.append("-DNDEBUG")
            if self.settings.arch == "armv7":
                compiler_flags.append("-Oz")
            else:
                compiler_flags.append("-O2")
        # enable format string checks (default)
        compiler_flags.extend(["-Wformat", "-Werror=format-security"])
        # workaround for a bug in libsodium RDRAND detection...
        compiler_flags.append("-Werror=implicit-function-declaration")

        # do not re-export libgcc symbols in every binary
        linker_flags = ["-Wl,--exclude-libs,libgcc.a", "-Wl,--exclude-libs,libatomic.a", "--target=%s" % target]
        linker_flags.append("--gcc-toolchain=%s" % toolchain_root_path)
        # do not use system libstdc++
        # different sysroots for linking/compiling
        linker_flags.extend(["-nostdlib++", "--sysroot=%s" % platform_path])
        # set C++ library search path
        linker_flags.append("-L%s" % posixpath.join(stl_path, "libs", self.android_abi))
        # link default libraries
        if self.options.libcxx == "static":
            linker_flags.extend(["-lc++_static", "-lc++abi"])
            if self.settings.arch == "armv7":
                linker_flags.extend(["-lunwind", "-ldl"])
        else:
            linker_flags.append("-lc++_shared")
            if self.settings.arch == "armv7":
                linker_flags.append("-lunwind")
        linker_flags.extend(["-latomic", "-lm"])
        if int(str(self.settings.os.api_level)) < 21:
            compiler_flags.append("-isystem%s" % posixpath.join(self.posix_package_folder, "sources", "android", "support", "include"))
            linker_flags.append("-landroid_support")

        # do not disable relro (default)
        linker_flags.extend(["-Wl,-z,relro", "-Wl,-z,now"])

        # disable execstack (default)
        linker_flags.append("-Wl,-z,noexecstack")
        # workaround clang warnings
        linker_flags.append("-Qunused-arguments")

        # generic flags
        linker_flags.extend(["-Wl,--build-id", "-Wl,--warn-shared-textrel", "-Wl,--fatal-warnings", "-Wl,--no-undefined"])
        if self.settings.arch == "armv7":
            linker_flags.extend(["-Wl,--exclude-libs,libunwind.a", "-Wl,--fix-cortex-a8"])
        # specific flags for executables
        pie_flags = ["-pie"]
        if self.settings.arch in ["x86", "x86_64"]:
            pie_flags.append("-fPIE")
        else:
            pie_flags.append("-fpie")
        exe_linker_flags = linker_flags[:]
        exe_linker_flags.extend(["-Wl,--gc-sections", "-Wl,-z,nocopyreloc"])
        exe_linker_flags.extend(pie_flags)

        self.cpp_info.cflags = compiler_flags
        self.cpp_info.cppflags = compiler_flags
        self.cpp_info.sharedlinkflags = linker_flags
        self.cpp_info.exelinkflags = exe_linker_flags

        if self.settings.os_build == "Windows":
            suffix = ".exe"
        else:
            suffix = ""
        clang = posixpath.join(llvm_toolchain_prefix, "clang%s" % suffix)
        clangxx = posixpath.join(llvm_toolchain_prefix, "clang++%s" % suffix)
        lld = posixpath.join(llvm_toolchain_prefix, "ld.lld%s" % suffix)
        self.env_info.PATH.append(llvm_toolchain_prefix)
        self.env_info.CC = clang
        self.env_info.CXX = clangxx
        self.env_info.CPP = "%s -E" % clangxx
        self.env_info.CCAS = clang
        self.env_info.LD = lld
        self.env_info.CFLAGS = " ".join(self.cpp_info.cflags)
        self.env_info.CPPFLAGS = " ".join(self.cpp_info.cflags)
        self.env_info.CXXFLAGS = " ".join(self.cpp_info.cppflags)
        self.env_info.ASFLAGS = " ".join(self.cpp_info.cflags)
        # There is no env var for executable linker flags...
        self.env_info.LDFLAGS = " ".join(self.cpp_info.sharedlinkflags)
        self.env_info.AR = posixpath.join(toolchain_bin_path, "ar%s" % suffix)
        self.env_info.RANLIB = posixpath.join(toolchain_bin_path, "ranlib%s" % suffix)
        # Provide a CMake Toolchain file, the two first flags are used inside android-toolchain.cmake
        if self.settings.arch == "armv7":
            self.env_info.CONAN_ANDROID_ARM_MODE = str(self.options.arm_mode)
            if self.options.neon:
                self.env_info.CONAN_ANDROID_ARM_NEON = "TRUE"
        self.env_info.CONAN_ANDROID_STL = "c++_%s" % self.options.libcxx
        self.env_info.CONAN_ANDROID_ABI = str(self.android_abi)
        self.env_info.CONAN_ANDROID_NATIVE_API_LEVEL = str(self.settings.os.api_level)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = posixpath.join(self.posix_package_folder, "android-toolchain.cmake")

    def package_id(self):
        self.info.settings.arch = "ANY"
        self.info.settings.build_type = "ANY"
        self.info.options.neon = "ANY"
        self.info.options.arm_mode = "ANY"
        self.info.options.libcxx = "ANY"
        self.info.settings.os.api_level = "ANY"
        self.info.include_build_settings()
