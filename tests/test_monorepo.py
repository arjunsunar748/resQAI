"""
Monorepo structure and security hygiene tests.
"""
from pathlib import Path
import re

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_monorepo_required_directories_exist():
    required_paths = [
        "frontend",
        "backend",
        "infrastructure",
        "docs",
        "scripts",
        "tests",
        ".github/workflows/ci.yml",
        ".env.example",
        ".gitignore",
        "docker-compose.yml",
        "README.md",
        "LICENSE",
    ]
    for path_str in required_paths:
        target = ROOT_DIR / path_str
        assert target.exists(), f"Required monorepo path missing: {path_str}"


def test_backend_modular_structure_exists():
    required_backend_modules = [
        "app/main.py",
        "app/core",
        "app/api",
        "app/models",
        "app/schemas",
        "app/services",
        "app/repositories",
        "app/middleware",
        "app/utils",
        "tests",
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/prod.txt",
    ]
    backend_dir = ROOT_DIR / "backend"
    for mod_path in required_backend_modules:
        target = backend_dir / mod_path
        assert target.exists(), f"Required backend modular path missing: {mod_path}"


def test_env_example_required_placeholders():
    env_example = (ROOT_DIR / ".env.example").read_text(encoding="utf-8")
    required_placeholders = [
        "DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET",
        "JWT_REFRESH_SECRET",
        "AI_PROVIDER",
        "AI_BASE_URL",
        "AI_MODEL",
        "MAP_PROVIDER",
        "LOG_LEVEL",
        "CORS_ORIGINS",
    ]
    for placeholder in required_placeholders:
        assert f"{placeholder}=" in env_example, f"Missing required placeholder in .env.example: {placeholder}"


def test_documentation_files_exist():
    docs_dir = ROOT_DIR / "docs"
    required_docs = [
        "architecture.md",
        "development.md",
        "security.md",
        "api.md",
        "deployment.md",
    ]
    for doc in required_docs:
        doc_path = docs_dir / doc
        assert doc_path.exists(), f"Required documentation file missing: {doc}"
        assert doc_path.stat().st_size > 100, f"Documentation file is empty or trivial: {doc}"
