# High-level executor status
string state          # "IDLE", "EXECUTING", "DONE", "ERROR"
string intent_type
string[] args
float32 progress      # 0.0 to 1.0
string detail         # optional human-readable info
