# Flash FIR workspace

PrismStudio imports Flash FIR v1 as data. It does not execute Flash source,
shell commands, or host code. The resulting photonic design and detector traces
are software simulation evidence; they are not fabricated-hardware validation.

Open **Debug → Flash FIR Workspace** or run **Flash FIR Workspace** from the
command palette. Enter a `.fir` path, choose **Import FIR**, then use
**Run/Pause**, **Step**, or **Reset**. The left pane shows the bounded FIR source;
the right pane lists each imported operation, lattice opcode, expected trit, and
verification status. Invalid headers, unsupported operations, oversize inputs,
placement failures, and detector mismatches are surfaced as errors.

`examples/flash_reference.fir` is the maintained four-operation UI fixture. The
larger canonical reference remains `examples/flash_photonic_massive.zpa` and is
available through **Open Reference Flash PCU**.

Verification is provided by the `reference-pcu-ui`, `flash-photonic`,
`reference-tamper`, `simulation-properties`, and parser-corpus gates. Any future
hardware result must be reported separately with its exact device tuple and
hardware gate evidence.
