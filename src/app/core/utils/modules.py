import importlib
from pathlib import Path


def collect_domain_modules(module_name: str) -> list:
    import app

    modules = []
    root = Path(app.__file__).parent
    for domain_root in root.iterdir():
        init_module = domain_root.joinpath(f"{module_name}.py")
        if init_module.exists():
            module_name = module_name.replace("/", ".")
            module = importlib.import_module(f"app.{domain_root.stem}.{module_name}")
            modules.append(module)
    return modules
