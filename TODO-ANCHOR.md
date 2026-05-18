# TODO Anchor — meshradio-node-runtime

This anchor was pruned to active, execution-critical items only.

## Priority Order (strict)

## [P1] Keep node runtime stable and field-usable
- [x] Connectivity-mode and control-plane outage events emitted by spool.
- [x] Collector parser integrity counters present (`checksum_ok`, `checksum_bad`, `malformed_frame`).
- [ ] Ensure runtime services are deterministic (known unit names, start/stop SOP, reboot persistence policy).
- [ ] Produce repeatable PASS/FAIL probe script for node serial, collector health, and sync backlog behavior.

## [P2] Telemetry schema parity + readiness evidence
- [ ] Enforce required-field shape with explicit null semantics for missing GNSS/cellular/weather fields.
- [ ] Emit machine-readable node readiness report (service state, schema parity, backlog health).

## [P3] Cellular telemetry ingestion (node)
- [ ] Add host-side cellular telemetry collector (ModemManager/NM based, null-safe when modem absent).
- [ ] Merge cellular status into node telemetry export path.
- [ ] Add validation matrix for modem present/absent and attached/detached states.

## Completion condition for this repo
- [ ] Node runtime can: (1) collect schema-valid telemetry, (2) survive outage windows, and (3) expose cellular telemetry state for analysis.
