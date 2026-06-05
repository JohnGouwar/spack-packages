import os
import re
from spack_repo.builtin.build_systems.generic import Package
from spack.package import *

class LlvmRuntime(Package):
    """Package for LLVM compiler runtime libraries"""

    #FIXME: real homepage
    homepage = "https://gcc.gnu.org"
    has_code = False

    tags = ["runtime"]

    # llvm-runtime versions are declared dynamically
    skip_version_audit = ["platform=linux", "platform=darwin", "platform=windows"]

    depends_on("libc", type="link", when="platform=linux")
    depends_on("llvm", type="build")
    
    # These libraries are libNAME.so
    LIB_LIBRARIES = [
        "c++",
        "omp",
        "unwind"
    ]
    # These libraries are prefixed with libclang_rt.NAME.so
    COMPILER_RT_LIBRARIES = [
        "asan",
        "dyndd",
        "hwasan_aliases",
        "hwasan",
        "memprof",
        "nsan",
        "scudo_standalone",
        "tsan", 
        "ubsan_minimal",
        "ubsan_standalone"
    ]
    
    def install(self, spec, prefix):
        llvm_pkg = self.spec["llvm"].package
        libraries = get_compiler_rt_libraries(compiler=llvm_pkg, libraries=self.COMPILER_RT_LIBRARIES)
        mkdir(prefix.lib)

        if not libraries:
            tty.warn("Could not detect any shared OneAPI runtime libraries")
            return

        for path in libraries:
            install(path, os.path.join(prefix.lib, os.path.basename(path)))

            
def get_compiler_rt_libraries(compiler, libraries):
    """Get the llvm runtime libraries for ELF binaries"""
    cc = Executable(compiler.cc)
    paths = []
    
    for name in libraries:
        # Look for the dynamic library that gcc would use to link,
        # that is with .so extension and without abi suffix.
        path = cc(f"-print-file-name=libclang_rt.{name}.so", output=str).strip()
        
        # gcc reports an absolute path on success
        if not os.path.isabs(path):
            continue

        paths.append(path)

    return paths

    
