# SCSCP C/C++ library 1.0.3: archived build input for Macaulay2

## Source copy and license

libscscp 1.0.3, the IMCCE implementation of the Symbolic Computation Software Composability Protocol (author Mickael
Gastineau), is retained unchanged as [scscp-1.0.3.tar.gz](../source_archives/scscp-1.0.3.tar.gz). Its origin URL,
https://www.imcce.fr/content/medias/recherche/equipes/asd/trip/scscp/download/scscp-1.0.3.tar.gz, refused
connections on 2026-10-28, so the copy comes from the Wayback Machine raw capture of 2023-06-13,
https://web.archive.org/web/20230613103250id_/https://www.imcce.fr/content/medias/recherche/equipes/asd/trip/scscp/download/scscp-1.0.3.tar.gz,
retrieved 2026-10-28. Its SHA-256
`a9d07b26e8f53dc723a521e991ffaa0fa62c7d37202d65919fc0ae391608ae1a` equals the checksum the Arch AUR package
`scscp` 1.0.3-2 pins in its PKGBUILD, and it holds 894717 bytes.

`readme.txt` declares the library dual-licensed, CeCILL-C or CeCILL v2.0 at the recipient's choice, and the archive
carries both texts (`COPYING_CECILL_C.LIB`, `COPYING_CECILL_V2.LIB`). This copy is redistributed under CeCILL-C,
which permits redistribution of the unchanged archive with its notices. [SOURCES.json](../SOURCES.json) binds the
archive, the CeCILL-C license member and every inspected member by SHA-256, and `verify_sources.py` admits the
Wayback route only as a 14-digit-timestamp `id_` capture.

## Role on the build host

The AUR `macaulay2` package depends on `scscp`; Macaulay2 serves the A_5 Gauss-fiber eliminations over `GF(p^2)` and
`Q(i)` beside Singular, msolve and giac ([PYTHON.md](../PYTHON.md#libraries-by-job)). When the origin URL stays
unreachable, copying this archive into the AUR build directory (`~/.cache/paru/clone/scscp/`) lets makepkg verify it
against the PKGBUILD checksum and build without a download.
