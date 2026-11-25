<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Generated in session M6 from the installed metadata: Python packages from `.venv` (`importlib.metadata`: License-Expression, else the licence classifiers), npm packages from `demo/node_modules/*/package.json`, with `demo/package-lock.json` for the dev flag and for optional platform packages that are not installed on this machine. Nothing here is legal advice; the owner decides on any licence question (G-PUBLIC).

Accepted without a flag: MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0 and 0BSD.

## Flags

1. **Bundled libraries in the numpy 2.3.5 and scipy 1.16.3 wheels.** Both packages are BSD-3-Clause, but their `LICENSE.txt` lists bundled binaries under other terms: the GCC runtime library (GPL-3.0-or-later WITH GCC-exception-3.1) and libquadmath (LGPL-2.1-or-later), besides OpenBLAS and LAPACK (BSD-3-Clause variants). This repository does not redistribute these wheels; users install them from the package index. The GCC runtime exception is intended to allow use by non-GPL programs. Recorded for the owner's information; no action taken.
2. **No dependency without a declared licence.** Every installed package declares a licence.
3. **Build backend not installed in `.venv`.** `hatchling` (`[build-system]` in `pyproject.toml`) is used by uv to build the project but is not installed in `.venv`, so its licence was not read from installed metadata in this session.

## Python (`.venv`, Python 3.12.1)

| Package | Version | Role | Licence (metadata) | Flag |
|---|---|---|---|---|
| hypothesis | 6.170.15 | test (dev group) | MPL-2.0 | none |
| iniconfig | 2.3.1 | test (pytest dependency) | MIT | none |
| numpy | 2.3.5 | runtime | BSD License | see flag 1 |
| packaging | 26.3 | test (pytest dependency) | Apache-2.0 OR BSD-2-Clause | none |
| pluggy | 1.7.0 | test (pytest dependency) | MIT License | none |
| Pygments | 2.21.0 | test (pytest dependency) | BSD-2-Clause | none |
| pytest | 8.4.2 | test (dev group) | MIT License | none |
| scipy | 1.16.3 | runtime | BSD License | see flag 1 |
| sortedcontainers | 2.4.0 | test (hypothesis dependency) | Apache Software License | none |

## npm (`demo/`, 84 packages in the lockfile: 3 runtime, 81 build and test)

Runtime packages are bundled into the static page; build and test packages are not shipped. Packages marked "lock only" are optional platform-specific binaries for other operating systems or CPUs; their licence is taken from the lockfile.

| Package | Version | Role | Licence | Flag |
|---|---|---|---|---|
| react | 19.3.1 | runtime (bundled) | MIT | none |
| react-dom | 19.3.1 | runtime (bundled) | MIT | none |
| scheduler | 0.28.0 | runtime (bundled) | MIT | none |
| @emnapi/core | 2.0.0-beta.2 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @emnapi/runtime | 2.0.0-beta.2 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @emnapi/wasi-threads | 2.2.0 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @jridgewell/sourcemap-codec | 1.6.0 | build and test | MIT | none |
| @napi-rs/wasm-runtime | 1.2.6 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @oxc-project/types | 0.156.0 | build and test | MIT | none |
| @rolldown/binding-android-arm-eabi | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-android-arm64 | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-darwin-arm64 | 1.2.19 | build (optional platform binary) | MIT | none |
| @rolldown/binding-darwin-x64 | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-freebsd-x64 | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-arm-gnueabihf | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-arm64-gnu | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-arm64-musl | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-ppc64-gnu | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-s390x-gnu | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-x64-gnu | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-linux-x64-musl | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-openharmony-arm64 | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-wasm32-wasi | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-win32-arm64-msvc | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/binding-win32-x64-msvc | 1.2.19 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @rolldown/pluginutils | 1.1.1 | build and test | MIT | none |
| @standard-schema/spec | 1.1.0 | build and test | MIT | none |
| @tybys/wasm-util | 0.10.5 | build (optional platform binary) | MIT (lock only, not installed on this platform) | none |
| @types/chai | 5.2.3 | build and test | MIT | none |
| @types/deep-eql | 4.0.2 | build and test | MIT | none |
| @types/estree | 1.0.11 | build and test | MIT | none |
| @types/react | 19.3.0 | build and test | MIT | none |
| @types/react-dom | 19.3.0 | build and test | MIT | none |
| @vitejs/plugin-react | 6.1.2 | build and test | MIT | none |
| @vitest/expect | 4.1.12 | build and test | MIT | none |
| @vitest/mocker | 4.1.12 | build and test | MIT | none |
| @vitest/pretty-format | 4.1.12 | build and test | MIT | none |
| @vitest/runner | 4.1.12 | build and test | MIT | none |
| @vitest/snapshot | 4.1.12 | build and test | MIT | none |
| @vitest/spy | 4.1.12 | build and test | MIT | none |
| @vitest/utils | 4.1.12 | build and test | MIT | none |
| assertion-error | 2.0.1 | build and test | MIT | none |
| chai | 6.3.0 | build and test | MIT | none |
| convert-source-map | 2.0.0 | build and test | MIT | none |
| csstype | 3.2.4 | build and test | MIT | none |
| detect-libc | 2.1.2 | build and test | Apache-2.0 | none |
| es-module-lexer | 2.3.2 | build and test | MIT | none |
| estree-walker | 3.0.3 | build and test | MIT | none |
| expect-type | 1.4.0 | build and test | Apache-2.0 | none |
| fdir | 6.5.0 | build and test | MIT | none |
| fsevents | 2.3.3 | build (optional platform binary) | MIT | none |
| lightningcss | 1.33.0 | build and test | MPL-2.0 | none |
| lightningcss-android-arm64 | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-darwin-arm64 | 1.33.0 | build (optional platform binary) | MPL-2.0 | none |
| lightningcss-darwin-x64 | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-freebsd-x64 | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-linux-arm-gnueabihf | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-linux-arm64-gnu | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-linux-arm64-musl | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-linux-x64-gnu | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-linux-x64-musl | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-win32-arm64-msvc | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| lightningcss-win32-x64-msvc | 1.33.0 | build (optional platform binary) | MPL-2.0 (lock only, not installed on this platform) | none |
| magic-string | 0.30.21 | build and test | MIT | none |
| nanoid | 3.3.20 | build and test | MIT | none |
| obug | 2.2.1 | build and test | MIT | none |
| pathe | 2.0.3 | build and test | MIT | none |
| picocolors | 1.1.1 | build and test | ISC | none |
| picomatch | 4.0.7 | build and test | MIT | none |
| postcss | 8.5.33 | build and test | MIT | none |
| rolldown | 1.2.19 | build and test | MIT | none |
| siginfo | 2.0.0 | build and test | ISC | none |
| source-map-js | 1.2.4 | build and test | BSD-3-Clause | none |
| stackback | 0.0.2 | build and test | MIT | none |
| std-env | 4.3.0 | build and test | MIT | none |
| tinybench | 2.9.0 | build and test | MIT | none |
| tinyexec | 1.4.0 | build and test | MIT | none |
| tinyglobby | 0.2.17 | build and test | MIT | none |
| tinyrainbow | 3.2.0 | build and test | MIT | none |
| tslib | 2.9.1 | build (optional platform binary) | 0BSD (lock only, not installed on this platform) | none |
| typescript | 5.9.3 | build and test | Apache-2.0 | none |
| vite | 8.3.5 | build and test | MIT | none |
| vitest | 4.1.12 | build and test | MIT | none |
| why-is-node-running | 2.3.0 | build and test | MIT | none |

npm licence counts: MIT 65, MPL-2.0 12, Apache-2.0 3, ISC 2, BSD-3-Clause 1, 0BSD 1.
