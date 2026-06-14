import subprocess
import sys
p = subprocess.run([sys.executable, "main.py", "dramaga", "--min", "10", "--pages", "1"], capture_output=True, text=True)
print("--- STDOUT ---")
print(p.stdout)
print("--- STDERR ---")
print(p.stderr)
print(f"Exit code: {p.returncode}")
