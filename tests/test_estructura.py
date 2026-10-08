from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_existe_readme():
    assert (ROOT / "README.md").exists()


def test_existe_directorio_github():
    assert (ROOT / ".github").is_dir()


def test_existe_directorio_workflows():
    assert (ROOT / ".github" / "workflows").is_dir()


def test_existe_ci_yml():
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()


def test_existe_directorio_labs():
    assert (ROOT / "labs").is_dir()


def test_existe_directorio_manifiestos():
    assert (ROOT / "manifiestos").is_dir()