# SPDX-License-Identifier: MIT
# Copyright (c) 2026 EoS Project
"""Minimal ELF parser — extract entry point, segments, and symbols.

Pure Python implementation using struct. No external dependencies.
Optionally uses pyelftools if installed for richer symbol info.
"""
import struct
from typing import List, Dict, Optional, NamedTuple


class ELFSegment(NamedTuple):
    type: int
    offset: int
    vaddr: int
    paddr: int
    filesz: int
    memsz: int
    flags: int
    data: bytes


class ELFSymbol(NamedTuple):
    name: str
    value: int
    size: int
    type: str
    bind: str


class ELFInfo:
    """Parsed ELF file information."""

    def __init__(self):
        self.entry_point: int = 0
        self.arch: str = ''
        self.bits: int = 32
        self.endian: str = 'little'
        self.segments: List[ELFSegment] = []
        self.symbols: List[ELFSymbol] = []
        self.sections: Dict[str, dict] = {}

    @property
    def load_segments(self) -> List[ELFSegment]:
        """Return only PT_LOAD segments."""
        return [s for s in self.segments if s.type == 1]


ELF_MAGIC = b'\x7fELF'

ELF_ARCH_MAP = {
    0x28: 'arm',
    0xB7: 'aarch64',
    0xF3: 'riscv',
    0x03: 'x86',
    0x3E: 'x86_64',
    0x08: 'mips',
}

SYM_TYPE_MAP = {0: 'NOTYPE', 1: 'OBJECT', 2: 'FUNC', 3: 'SECTION', 4: 'FILE'}
SYM_BIND_MAP = {0: 'LOCAL', 1: 'GLOBAL', 2: 'WEAK'}


def parse_elf(path: str) -> ELFInfo:
    """Parse an ELF file and return entry point, segments, symbols."""
    with open(path, 'rb') as f:
        data = f.read()
    return parse_elf_bytes(data)


def parse_elf_bytes(data: bytes) -> ELFInfo:
    """Parse ELF from bytes."""
    if data[:4] != ELF_MAGIC:
        raise ValueError("Not an ELF file")

    info = ELFInfo()
    ei_class = data[4]
    ei_data = data[5]

    info.bits = 64 if ei_class == 2 else 32
    info.endian = 'big' if ei_data == 2 else 'little'
    endian_char = '>' if ei_data == 2 else '<'

    if info.bits == 32:
        fmt = f'{endian_char}HHIIIIIHHHHHH'
        hdr = struct.unpack_from(fmt, data, 16)
        info.arch = ELF_ARCH_MAP.get(hdr[0], f'unknown({hdr[0]:#x})')
        info.entry_point = hdr[2]
        phoff = hdr[3]
        shoff = hdr[4]
        phentsize = hdr[7]
        phnum = hdr[8]
        shentsize = hdr[9]
        shnum = hdr[10]
        shstrndx = hdr[11]
    else:
        fmt = f'{endian_char}HHIQQQIHHHHHH'
        hdr = struct.unpack_from(fmt, data, 16)
        info.arch = ELF_ARCH_MAP.get(hdr[0], f'unknown({hdr[0]:#x})')
        info.entry_point = hdr[2]
        phoff = hdr[3]
        shoff = hdr[4]
        phentsize = hdr[7]
        phnum = hdr[8]
        shentsize = hdr[9]
        shnum = hdr[10]
        shstrndx = hdr[11]

    # Parse program headers
    for i in range(phnum):
        off = phoff + i * phentsize
        if info.bits == 32:
            ph = struct.unpack_from(f'{endian_char}IIIIIIII', data, off)
            seg = ELFSegment(
                type=ph[0], offset=ph[1], vaddr=ph[2], paddr=ph[3],
                filesz=ph[4], memsz=ph[5], flags=ph[6],
                data=data[ph[1]:ph[1] + ph[4]],
            )
        else:
            ph = struct.unpack_from(f'{endian_char}IIQQQQQQ', data, off)
            seg = ELFSegment(
                type=ph[0], offset=ph[2], vaddr=ph[3], paddr=ph[4],
                filesz=ph[5], memsz=ph[6], flags=ph[1],
                data=data[ph[2]:ph[2] + ph[5]],
            )
        info.segments.append(seg)

    # Parse section headers to find string table and symbol table
    if shoff and shnum and shstrndx < shnum:
        _parse_sections(data, info, endian_char, shoff, shentsize, shnum, shstrndx)

    return info


def _parse_sections(data, info, ec, shoff, shentsize, shnum, shstrndx):
    """Parse section headers for symbols."""
    is64 = info.bits == 64

    # Get section header string table
    strtab_off = shoff + shstrndx * shentsize
    if is64:
        sh = struct.unpack_from(f'{ec}IIQQQQIIQQ', data, strtab_off)
        shstr_offset, shstr_size = sh[4], sh[5]
    else:
        sh = struct.unpack_from(f'{ec}IIIIIIIIII', data, strtab_off)
        shstr_offset, shstr_size = sh[4], sh[5]

    def _get_str(strtab_data, offset):
        end = strtab_data.find(b'\x00', offset)
        if end < 0:
            return ''
        return strtab_data[offset:end].decode('ascii', errors='replace')

    shstr_data = data[shstr_offset:shstr_offset + shstr_size]

    # Find .symtab and .strtab sections
    symtab_off = symtab_sz = symtab_ent = 0
    sym_strtab_off = sym_strtab_sz = 0

    for i in range(shnum):
        off = shoff + i * shentsize
        if is64:
            sh = struct.unpack_from(f'{ec}IIQQQQIIQQ', data, off)
            sh_name, sh_type, sh_offset, sh_size, sh_entsize = sh[0], sh[1], sh[4], sh[5], sh[9]
            sh_link = sh[6]
        else:
            sh = struct.unpack_from(f'{ec}IIIIIIIIII', data, off)
            sh_name, sh_type, sh_offset, sh_size, sh_entsize = sh[0], sh[1], sh[4], sh[5], sh[9]
            sh_link = sh[6]

        name = _get_str(shstr_data, sh_name)
        info.sections[name] = {
            'type': sh_type, 'offset': sh_offset, 'size': sh_size,
            'entsize': sh_entsize,
        }

        if sh_type == 2:  # SHT_SYMTAB
            symtab_off = sh_offset
            symtab_sz = sh_size
            symtab_ent = sh_entsize or (24 if is64 else 16)
            # Get linked string table
            link_off = shoff + sh_link * shentsize
            if is64:
                lsh = struct.unpack_from(f'{ec}IIQQQQIIQQ', data, link_off)
                sym_strtab_off, sym_strtab_sz = lsh[4], lsh[5]
            else:
                lsh = struct.unpack_from(f'{ec}IIIIIIIIII', data, link_off)
                sym_strtab_off, sym_strtab_sz = lsh[4], lsh[5]

    if not symtab_off:
        return

    sym_strtab = data[sym_strtab_off:sym_strtab_off + sym_strtab_sz]
    num_syms = symtab_sz // symtab_ent

    for i in range(num_syms):
        off = symtab_off + i * symtab_ent
        if is64:
            st = struct.unpack_from(f'{ec}IBBHQQ', data, off)
            name_idx, st_info, st_other, st_shndx, st_value, st_size = st
        else:
            st = struct.unpack_from(f'{ec}IIIBBH', data, off)
            name_idx, st_value, st_size, st_info = st[0], st[1], st[2], st[3]

        sym_type = SYM_TYPE_MAP.get(st_info & 0xF, 'UNKNOWN')
        sym_bind = SYM_BIND_MAP.get(st_info >> 4, 'UNKNOWN')
        sym_name = _get_str(sym_strtab, name_idx)

        if sym_name and sym_type in ('FUNC', 'OBJECT'):
            info.symbols.append(ELFSymbol(
                name=sym_name, value=st_value, size=st_size,
                type=sym_type, bind=sym_bind,
            ))
