# Copyright (c) 2017 Trail of Bits, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  # See the License for the specific language governing permissions and
# limitations under the License.

import time
import os
import platform
import sys
import shutil

from .utils import *
from distutils import spawn
from distutils.dir_util import copy_tree

PATCHES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "patches")

def patch_file(file_path, patch_name):
  if sys.platform == "win32":
    patch_executable = spawn.find_executable("patch.exe")
    if patch_executable is None:
      patch_executable = os.path.join(os.environ["ProgramFiles"], "Git", "usr", "bin", "patch.exe")
      if not os.path.exists(patch_executable):
        print(" x The patch.exe executable could not be found")
        print(" i Install Git for Windows to solve this error")

        return False

  else:
    patch_executable = "patch"

  patch_path = os.path.join(PATCHES_DIR, "{}.patch".format(patch_name))
  if not os.path.exists(patch_path):
    print(" x Failed to find patch file {}".format(patch_name))
    return False

  if not run_program("Patching {}".format(file_path), [patch_executable, file_path, patch_path], os.getcwd()):
    return False

  return True

def get_python_path(version):
  # some distributions have choosen to set python 3 as the default version
  # always request the exact executable name first

  if version == 2:
    return sys.executable

  elif version == 3:
    extension = ""
    if sys.platform == "win32":
      extension = ".exe"

    version_string = str(version)
    if sys.version_info[0] == 3 and \
      sys.version_info[1] > 0:
      version_string = str(sys.version_info[0]) + \
           "." + str(sys.version_info[1])

    # Check for the exact version executable first
    path = spawn.find_executable("python" + version_string + extension)
    if path is not None:
      return path

    path = spawn.find_executable("python" + str(version) + extension)
    if path is not None:
      return path

    path = spawn.find_executable("python" + extension)
    if path is not None:
      return path

    return None

  else:
    return None

def google_installer_glog(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  source_folder = download_github_source_archive(properties, "google", "glog")
  if source_folder is None:
    return False

  build_folder = os.path.join("build", "glog")
  if not os.path.isdir(build_folder):
    try:
      os.mkdir(build_folder)

    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator()
  cmake_command += ["-DCMAKE_CXX_STANDARD=11",
                    "-DBUILD_TESTING=OFF",
                    "-DWITH_GFLAGS=OFF",
                    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
                    "-DCMAKE_EXE_LINKER_FLAGS=-g",
                    "-DCMAKE_C_FLAGS=-g",
                    "-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "glog"),
                    source_folder]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  return True

def common_installer_capstone(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  source_folder = download_github_source_archive(properties, "aquynh", "capstone")
  if source_folder is None:
    return False

  build_folder = os.path.join("build", "capstone")
  if not os.path.isdir(build_folder):
    try:
      os.mkdir(build_folder)

    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator()
  cmake_command += ["-DCMAKE_EXE_LINKER_FLAGS=-g",
                    "-DCMAKE_C_FLAGS=-g",
                    "-DCAPSTONE_SPARC_SUPPORT=1",
                    "-DCAPSTONE_BUILD_STATIC=ON",
                    "-DCAPSTONE_BUILD_DIET=OFF",
                    "-DCAPSTONE_BUILD_SHARED=OFF",
                    "-DCAPSTONE_BUILD_TESTS=OFF",
                    "-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "capstone"),
                    source_folder]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  return True

def common_installer_xed(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  xed_source_folder = os.path.join("sources", "xed")
  if os.path.isdir(xed_source_folder):
    shutil.rmtree(xed_source_folder)

  mbuild_source_folder = os.path.join("sources", "mbuild")
  if os.path.isdir(mbuild_source_folder):
    shutil.rmtree(mbuild_source_folder)

  # out of source builds are not supported, so we'll have to build
  # inside the source directory
  xed_source_folder = download_github_source_archive(properties, "intelxed", "xed")
  if xed_source_folder is None:
    return False

  mbuild_source_folder = download_github_source_archive(properties, "intelxed", "mbuild")
  if mbuild_source_folder is None:
    return False

  env_file_path = os.path.realpath(os.path.join("sources", "mbuild", "mbuild", "env.py"))
  if not patch_file(env_file_path, "mbuild"):
    return False

  python_executable = get_python_path(3)
  if python_executable is None:
    return False

  mbuild_script = [python_executable, "mfile.py", "install", "--extra-flags=-fPIC"]
  if debug:
    mbuild_script.append("--debug")

  if not run_program("Building...", mbuild_script, xed_source_folder, verbose=verbose_output):
    return False

  print(" > Installing...")
  kit_folder_name = "xed-install-base-" + time.strftime("%Y-%m-%d") + "-"
  if sys.platform == "linux" or sys.platform == "linux2":
    kit_folder_name += "lin"

  elif sys.platform == "darwin":
    kit_folder_name += "mac"

  elif sys.platform == "win32" or sys.platform == "cygwin":
    kit_folder_name += "win"

  else:
    print(" x Failed to determine the kit name")
    return False

  kit_folder_name += "-{}".format(platform.machine().replace("_", "-"))
  kit_folder_path = os.path.realpath(os.path.join("sources", "xed", "kits", kit_folder_name))

  try:
    copy_tree(kit_folder_path, os.path.join(repository_path, "xed"))
  except Exception as e:
    print(" x Failed to install the XED library: {}".format(str(e)))
    return False

  return True

def google_installer_gflags(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  source_folder = download_github_source_archive(properties, "gflags", "gflags")
  if source_folder is None:
    return False

  build_folder = os.path.join("build", "gflags")
  if not os.path.isdir(build_folder):
    try:
      os.mkdir(build_folder)

    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator()
  cmake_command += ["-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "gflags"),
                    "-DCMAKE_CXX_STANDARD=11",
                    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
                    "-DGFLAGS_BUILD_TESTING=OFF",
                    "-DGFLAGS_BUILD_SHARED_LIBS=OFF",
                    "-DGFLAGS_BUILD_STATIC_LIBS=ON",
                    "-DGFLAGS_NAMESPACE=google",
                    source_folder]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  return True

def google_installer_googletest(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  source_folder = download_github_source_archive(properties, "google", "googletest")
  if source_folder is None:
    return False

  build_folder = os.path.join("build", "googletest")
  if not os.path.isdir(build_folder):
    try:
      os.mkdir(build_folder)

    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator(False)
  cmake_command += ["-DCMAKE_CXX_STANDARD=11",
                    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
                    "-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "googletest"),
                    source_folder]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  return True

def common_installer_google(properties):
  if not google_installer_gflags(properties):
    return False

  print("")
  if not google_installer_glog(properties):
    return False

  print("")
  if not google_installer_googletest(properties):
    return False

  print("")
  if not google_installer_protobuf(properties):
    return False

  return True

def google_installer_protobuf(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  version = "2.6.1"
  url = "https://github.com/google/protobuf/archive/v" + version + ".tar.gz"

  source_tarball_path = download_file(properties, url, "sources")
  if source_tarball_path is None:
    return False

  if not extract_archive(source_tarball_path, "sources"):
    return False

  source_folder = os.path.realpath(os.path.join("sources", "protobuf-" + version))

  # this version is too old and doesn't support cmake out of the box
  # so we need to use an external project
  try:
    copy_tree(os.path.join(properties["cxx_common_dir"], "cmake", "protobuf_project"), 
              os.path.join(source_folder, "cmake"))
    print(" > Copying the CMake project...")

  except:
    print(" x Failed to copy the CMake project")
    return False

  build_folder = os.path.join("build", "protobuf")
  if not os.path.isdir(build_folder):
    try:
      os.makedirs(build_folder)
 
    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator(False)
  cmake_command += ["-DPROTOBUF_ROOT=" + source_folder,
                    "-DBUILD_SHARED_LIBS=OFF",
                    "-Dprotobuf_BUILD_TESTS=OFF",
                    "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
                    "-Dprotobuf_WITH_ZLIB=OFF",
                    "-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "protobuf"),
                    os.path.join(source_folder, "cmake")]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  module_folders = ["lib"]

  if sys.platform == "win32" or sys.platform == "cygwin":
    protoc_executable = "protoc.exe"
    os.environ["PATH"] = os.path.join(repository_path, "protobuf", "lib") + ":" + os.environ["PATH"]

  else:
    os.environ["LIBRARY_PATH"] = os.path.join(repository_path, "protobuf", "lib")
    os.environ["LD_LIBRARY_PATH"] = os.environ["LIBRARY_PATH"]

    protoc_executable = "protoc"
    if sys.platform == "linux" or sys.platform == "linux2":
      module_folders.append("lib.linux-{}-{}.{}".format(platform.machine(), sys.version_info.major, sys.version_info.minor))

  os.environ["PROTOC"] = os.path.realpath(os.path.join(repository_path, "protobuf", "bin", protoc_executable))
  python_command = [get_python_path(2), "setup.py", "build"]
  if not run_program("Building the Python module...", python_command, os.path.join(source_folder, "python"), verbose=verbose_output):
    return False

  try:
    print(" > Copying the Python module...")
    for module_folder in module_folders:
      python_package = os.path.realpath(os.path.join("sources", "protobuf-" + version, "python", "build", module_folder, "google"))
      if os.path.isdir(python_package):
        copy_tree(python_package, os.path.join(repository_path, "protobuf", "python"))

  except:
    print(" x Failed to copy the Python module")
    return False

  return True

def common_installer_capnproto(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  source_folder = download_github_source_archive(properties, "capnproto", "capnproto")
  if source_folder is None:
    return False

  build_folder = os.path.join("build", "capnproto")
  if not os.path.isdir(build_folder):
    try:
      os.mkdir(build_folder)

    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator()
  cmake_command += ["-DCMAKE_CXX_STANDARD=11",
                    "-DCMAKE_CXX_EXTENSIONS=ON",
                    "-DBUILD_TESTING=OFF",
                    "-DEXTERNAL_CAPNP=OFF",
                    "-DCAPNP_LITE=OFF",
                    "-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "capnproto"),
                    source_folder]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  return True

def make_llvm_url(long_version, product):
  int_version = int(long_version.replace(".", ""))
  # LLVM from 9.0.1 is hosted on github
  if int_version > 900:
    #https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/llvm-10.0.0.src.tar.xz
    if product == "cfe":
      product = "clang"
    url = "https://github.com/llvm/llvm-project/releases/download/llvmorg-" + long_version + "/" + product + "-" + long_version + ".src.tar.xz"
  else:
    #https://releases.llvm.org/9.0.0/llvm-9.0.0.src.tar.xz
    url = "https://releases.llvm.org/"  + long_version + "/" + product + "-" + long_version + ".src.tar.xz"
  return url

def common_installer_llvm(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  sv = str(properties["llvm_version"])
  lv = str(properties["long_llvm_version"])
  llvm_tarball_url = make_llvm_url(lv, product="llvm")
  llvm_tarball_name = "llvm-" + sv + ".tar.xz"

  clang_tarball_url = make_llvm_url(lv, product="cfe")
  clang_tarball_name = "clang-" + sv + ".tar.xz"
  use_libcxx = sys.platform != "win32" and properties["include_libcxx"]
  if use_libcxx:
    libcxx_tarball_url = make_llvm_url(lv, product="libcxx")
    libcxx_tarball_name = "libcxx-" + sv + ".tar.xz"

    libcxxabi_tarball_url = make_llvm_url(lv, product="libcxxabi")
    libcxxabi_tarball_name = "libcxxabi-" + sv + ".tar.xz"

  # download everything we need
  llvm_tarball_path = download_file(properties, llvm_tarball_url, "sources", llvm_tarball_name)
  if llvm_tarball_path is None:
    return False

  clang_tarball_path = download_file(properties, clang_tarball_url, "sources", clang_tarball_name)
  if clang_tarball_path is None:
    return False

  if use_libcxx:
    libcxx_tarball_path = download_file(properties, libcxx_tarball_url, "sources", libcxx_tarball_name)
    if libcxx_tarball_path is None:
      return False

    libcxxabi_tarball_path = download_file(properties, libcxxabi_tarball_url, "sources", libcxxabi_tarball_name)
    if libcxxabi_tarball_path is None:
      return False
  else:
    print(" i Excluding libc++")

  # extract everything in the correct folders
  if not extract_archive(llvm_tarball_path, "sources"):
    return False

  if not extract_archive(clang_tarball_path, "sources"):
    return False

  if use_libcxx:
    if not extract_archive(libcxx_tarball_path, "sources"):
      return False

    if not extract_archive(libcxxabi_tarball_path, "sources"):
      return False

  llvm_root_folder = os.path.realpath(os.path.join("sources", "llvm-" + lv + ".src"))

  try:
    print(" > Moving the project folders in the LLVM source tree...")

    if use_libcxx:
      libcxx_destination = os.path.join(llvm_root_folder, "projects", "libcxx")
      if not os.path.isdir(libcxx_destination):
        shutil.move(os.path.join("sources", "libcxx-" + properties["long_llvm_version"] + ".src"), libcxx_destination)

      libcxxabi_destination = os.path.join(llvm_root_folder, "projects", "libcxxabi")
      if not os.path.isdir(libcxxabi_destination):
        shutil.move(os.path.join("sources", "libcxxabi-" + properties["long_llvm_version"] + ".src"), libcxxabi_destination)

    clang_destination = os.path.join(llvm_root_folder, "tools", "clang")
    if not os.path.isdir(clang_destination):
      cfe_name = "cfe-"

      if int(properties["llvm_version"]) > 900:
        cfe_name = "clang-"

      shutil.move(os.path.join("sources", cfe_name + properties["long_llvm_version"] + ".src"), clang_destination)

  except Exception as e:
    print(" ! " + str(e))
    print(" x Failed to build the source tree")
    return False
  
  # make sure to patch clang.
  if int(properties["llvm_version"]) < 401:
    print(" i Patching LLVM")
    intrusive_cnt_ptr = os.path.realpath(os.path.join(llvm_root_folder, "include", "llvm", "ADT", "IntrusiveRefCntPtr.h"))
    if not patch_file(intrusive_cnt_ptr, "llvm"):
      print(" x Failed to patch LLVM")
      return False

  if int(properties["llvm_version"]) <= 1100:
    print(" i Fixing LLVM's FindZ3.cmake")
    fz3_location = os.path.realpath(os.path.join(llvm_root_folder, "cmake", "modules", "FindZ3.cmake"))
    have_fz3 = os.path.exists(fz3_location)
    if have_fz3:
      src_file = os.path.join(PATCHES_DIR, "FindZ3.cmake")
      # overwrite the bad FindZ3.cmake with our version
      shutil.copyfile(src_file, fz3_location)

      src_file = os.path.join(PATCHES_DIR, "testz3.cpp")
      tz3_location = os.path.realpath(os.path.join(llvm_root_folder, "cmake", "modules", "testz3.cpp"))
      shutil.copyfile(src_file, tz3_location)


  # create the build directory and compile the package
  llvm_build_path = os.path.realpath(os.path.join("build", "llvm-" + str(properties["llvm_version"])))
  if not os.path.isdir(llvm_build_path):
    try:
      os.makedirs(llvm_build_path)

    except Exception as e:
      print(" ! " + str(e))
      print(" x Failed to create the build folder")
      return False

  destination_path = os.path.join(repository_path, "llvm")

  arch_list = "'X86"
  if sys.platform != "win32":
    arch_list += ";AArch64;Sparc;NVPTX;ARM"
  arch_list += "'"

  if properties["ccache"]:
    # Remove this so we don't clash with LLVM's built-in ccache config
    if "CMAKE_CXX_COMPILER_LAUNCHER" in os.environ:
      del(os.environ["CMAKE_CXX_COMPILER_LAUNCHER"])
    if "CMAKE_C_COMPILER_LAUNCHER" in os.environ:
      del(os.environ["CMAKE_C_COMPILER_LAUNCHER"])

  cppstd = "11"
  if int(properties["llvm_version"]) > 900:
    cppstd = "14"
  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + ["-DCMAKE_INSTALL_PREFIX=" + destination_path,
                                                                                           "-DCMAKE_CXX_STANDARD="+cppstd, "-DLLVM_TARGETS_TO_BUILD=" + arch_list,
                                                                                           "-DLLVM_ENABLE_RTTI=ON", "-DLLVM_INCLUDE_EXAMPLES=OFF",
                                                                                           "-DLLVM_INCLUDE_TESTS=OFF"]

  if properties["llvm_has_z3"]:
    cmake_command += ["-DLLVM_ENABLE_Z3_SOLVER=ON", "-DLLVM_Z3_INSTALL_DIR=" + os.path.join(repository_path, "z3"), "-DCLANG_ANALYZER_Z3_INSTALL_DIR=" + os.path.join(repository_path, "z3")]
  else:
    cmake_command += ["-DLLVM_ENABLE_Z3_SOLVER=OFF", "-DCLANG_ANALYZER_ENABLE_Z3_SOLVER=OFF"]

  if properties["ccache"]:
    ccache_dir = f"{os.getcwd()}/cache/ccache"
    print(f" i Enabling ccache on {ccache_dir} ... ")
    # some versions of LLVM use CCACHE_MAX_SIZE, others use CCACHE_SIZE
    cmake_command.extend(
        ["-DLLVM_CCACHE_BUILD=ON",
         "-DLLVM_CCACHE_SIZE=5G",
         f'-DLLVM_CCACHE_DIR="{ccache_dir}"',
         "-DLLVM_CCACHE_MAXSIZE=5G"])

  if use_libcxx:
    if int(properties["llvm_version"]) < 371:
      cmake_command += ["-DLIBCXX_ENABLE_SHARED=NO"]
    else:
      cmake_command += ["-DLIBCXX_ENABLE_STATIC=YES", "-DLIBCXX_ENABLE_SHARED=YES",
                        "-DLIBCXX_ENABLE_EXPERIMENTAL_LIBRARY=YES",
                        "-DLIBCXX_ENABLE_FILESYSTEM=YES",
                        "-LIBCXX_INCLUDE_BENCHMARKS=NO"]
  if "darwin" == sys.platform:
    cmake_command += ["-DLLVM_CREATE_XCODE_TOOLCHAIN=YES", "-DDEFAULT_SYSROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"]

  #cmake_command += ["-DLLVM_USE_SANITIZER=Address"]

  cmake_command += [llvm_root_folder] + get_cmake_generator()

  if not run_program("Configuring...", cmake_command, llvm_build_path, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, llvm_build_path, verbose=verbose_output):
    return False


  cmake_command = ["cmake", "--build", "."]
  cmake_command += get_cmake_build_configuration(debug)
  cmake_command += ["--target", "install"]

  if not run_program("Installing...", cmake_command, llvm_build_path, verbose=verbose_output):
    return False

  return True

def common_installer_z3(properties):
  repository_path = properties["repository_path"]
  verbose_output = properties["verbose"]
  debug = properties["debug"]

  source_folder = download_github_source_archive(properties, "Z3Prover", "z3", branch="z3-4.8.8")
  if source_folder is None:
    return False

  build_folder = os.path.join("build", "z3")
  if not os.path.isdir(build_folder):
    try:
      os.mkdir(build_folder)

    except:
      print(" x Failed to create the build folder")
      return False

  if properties["ccache"]:
      set_ccache_compiler()

  cmake_command = ["cmake"] + get_env_compiler_settings() + get_cmake_build_type(debug) + get_cmake_generator()
  cmake_command += ["-DZ3_BUILD_LIBZ3_SHARED=False",
                    "-DZ3_ENABLE_EXAMPLE_TARGETS=False",
                    "-DZ3_BUILD_DOCUMENTATION=False",
                    "-DZ3_BUILD_EXECUTABLE=True",
                    "-DZ3_BUILD_TEST_EXECUTABLES=False",
                    "-DZ3_USE_LIB_GMP=False",
                    "-DZ3_ENABLE_TRACING_FOR_NON_DEBUG=False",
                    "-DCMAKE_INSTALL_PREFIX=" + os.path.join(repository_path, "z3"),
                    source_folder]

  if not run_program("Configuring...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + [ "--", get_parallel_build_options()]
  if not run_program("Building...", cmake_command, build_folder, verbose=verbose_output):
    return False

  cmake_command = ["cmake", "--build", "."] + get_cmake_build_configuration(debug) + ["--target", "install"]
  if not run_program("Installing...", cmake_command, build_folder, verbose=verbose_output):
    return False

  return True
