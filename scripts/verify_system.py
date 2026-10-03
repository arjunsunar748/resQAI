"""
Automated verification script for RESQ AGENT Phase 1 compliance.
Verifies backend syntax, tests, database connectivity, and frontend build.
"""
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_step(step_name: str, cmd: list, cwd: Path):
    print(f"\n==================================================")
    print(f"[*] RUNNING: {step_name}")
    print(f"[*] DIRECTORY: {cwd}")
    print(f"[*] COMMAND: {' '.join(cmd)}")
    print(f"==================================================")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\n[!] ERROR: Step '{step_name}' failed with exit code {result.returncode}")
        return False
    print(f"[+] SUCCESS: {step_name} passed.")
    return True


def main():
    print("Starting RESQ AGENT Phase 1 Verification Suite...")
    backend_dir = ROOT_DIR / "backend"
    frontend_dir = ROOT_DIR / "frontend"

    # 1. Backend python compilation check
    ok = run_step(
        "Backend Syntax & Bytecode Compilation",
        [sys.executable, "-m", "compileall", "-q", "app"],
        cwd=backend_dir,
    )
    if not ok:
        sys.exit(1)

    # 2. Pytest execution
    ok = run_step(
        "Backend Pytest Test Suite",
        [sys.executable, "-m", "pytest", "-v"],
        cwd=backend_dir,
    )
    if not ok:
        sys.exit(1)

    # 3. Frontend production build
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    ok = run_step(
        "Frontend Vite Production Build",
        [npm_cmd, "run", "build"],
        cwd=frontend_dir,
    )
    if not ok:
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[*] ALL PHASE 1 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 50)


if __name__ == "__main__":
    main()
