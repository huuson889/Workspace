"""Linux-only restricted LibreOffice launcher. Not a complete document sandbox."""
import ctypes
import ctypes.util
import errno
import os
import resource
import sys


def restrict():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (150, 150))
    resource.setrlimit(resource.RLIMIT_FSIZE, (120 * 1024**2, 120 * 1024**2))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_DATA, (512 * 1024**2, 512 * 1024**2))
    lib = ctypes.CDLL(ctypes.util.find_library('seccomp') or 'libseccomp.so.2', use_errno=True)
    class Compare(ctypes.Structure):
        _fields_ = [('arg', ctypes.c_uint), ('op', ctypes.c_int),
                    ('a', ctypes.c_uint64), ('b', ctypes.c_uint64)]
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint, Compare]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW
    if not ctx:
        raise RuntimeError('seccomp_init failed')
    try:
        call = lib.seccomp_syscall_resolve_name(b'socket')
        # AF_INET / AF_INET6 / AF_PACKET; local UNIX sockets remain available.
        for domain in (2, 10, 17):
            if lib.seccomp_rule_add(ctx, 0x00050000 | errno.EPERM, call, 1,
                                    Compare(0, 4, domain, 0)) != 0:
                raise RuntimeError('seccomp rule failed')
        if lib.seccomp_load(ctx) != 0:
            raise RuntimeError('seccomp_load failed')
    finally:
        lib.seccomp_release(ctx)


if __name__ == '__main__':
    restrict()  # Fail closed if Linux/libseccomp is unavailable.
    os.execvp(sys.argv[1], sys.argv[1:])
