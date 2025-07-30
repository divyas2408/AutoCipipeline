import argparse
import yaml
from pathlib import Path

def build_workflow(blueprint, mode):
    parts = []
    if mode == "terraform":
        parts.append(Path(".ci/templates/terraform.yml").read_text())
    else:
        tech = blueprint["project"]["tech_stack"]
        deploy = blueprint["project"]["deploy_method"]
        parts.extend([
            Path(f".ci/templates/{tech}.yml").read_text(),
            Path(".ci/templates/test.yml").read_text(),
            Path(f".ci/templates/deploy/{deploy}.yml").read_text()
        ])
    final = "\n".join(parts)
    filename = ".github/workflows/generated-terraform.yml" if mode == "terraform" else ".github/workflows/generated.yml"
    Path(filename).write_text(final)
    print(f"✅ Generated {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', default=None)
    args = parser.parse_args()
    blueprint = yaml.safe_load(open(".ci/blueprint.yml"))
    build_workflow(blueprint, args.type)

if __name__ == "__main__":
    main()
