# GXVM downstream branch

The `gx` branch is based on upstream commit
`5ba42078a09cd3270ab6bcef029c7e73f152a19e`. Fixes are committed directly to the
source, not applied by the consuming project's build script.

Included changes:

- bounded persistent ELF dynamic-table scans, with core unit coverage;
- sparse `close_range` descriptor handling;
- TLS-safe asynchronous takeover of existing native pthreads;
- optional huge-page code-cache mappings;
- exact direct/indirect trace side-exit refund instrumentation;
- diagnostics for missing trace continuation targets;
- trace termination at native `drwrap` replacement boundaries.

The old user-level task-switch segment-base API is deliberately not included.
GXVM uses native Linux pthreads and does not virtualize their TLS.

GX/NEX pins this branch by submodule commit. Core checks use
`ctest --test-dir BUILD -R '^core_unit_tests$' --output-on-failure` after building
that target. The subprocess regression is
`python3 suite/tests/gxvm_close_range.py --drrun INSTALL/bin64/drrun`.
