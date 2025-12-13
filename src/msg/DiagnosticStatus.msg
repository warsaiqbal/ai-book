# Diagnostic information from robot subsystems
int8 level                 # Diagnostic level (0=OK, 1=Warn, 2=Error, 3=Stale)
string name                # Name of the subsystem
string message             # Human-readable message
string hardware_id         # Hardware ID of the subsystem
# DiagnosticValue[] values   # Additional diagnostic values (commented out to avoid circular reference)