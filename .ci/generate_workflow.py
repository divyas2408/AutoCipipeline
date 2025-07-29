import yaml
from pathlib import Path

def load_blueprint():
    with open(".ci/blueprint.yml", "r") as f:
        return yaml.safe_load(f)

def build_workflow(blueprint):
    output = []

    tech_stack = blueprint["project"]["tech_stack"]
    deploy_method = blueprint["project"]["deploy_method"]

    output.append(Path(f".ci/templates/{tech_stack}.yml").read_text())
    output.append(Path(f".ci/templates/deploy/{deploy_method}.yml").read_text())

    if blueprint["project"].get("lint"):
        output.append(Path(".ci/templates/lint.yml").read_text())
    if blueprint["project"].get("test"):
        output.append(Path(".ci/templates/test.yml").read_text())

    final_workflow = "\n".join(output)
    Path(".github/workflows/generated.yml").write_text(final_workflow)
    print("✅ GitHub Actions workflow generated at .github/workflows/generated.yml")

if __name__ == "__main__":
    build_workflow(load_blueprint())
