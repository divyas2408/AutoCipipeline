import argparse
import yaml
from pathlib import Path
import subprocess

def detect_tech_and_deploy():
    try:
        changed_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1"], text=True
        ).splitlines()
    except subprocess.CalledProcessError:
        print("⚠️ Could not get changed files from git.")
        return None, None

    tech_stack = None
    deploy_method = None

    for file in changed_files:
        file = file.lower()
        if file.endswith(".py"):
            tech_stack = tech_stack or "python"
        elif file.endswith(".java"):
            tech_stack = tech_stack or "java"
        elif file.endswith(".cpp") or file.endswith(".cxx"):
            tech_stack = tech_stack or "cpp"
        elif file.endswith(".js") or "node_modules" in file:
            tech_stack = tech_stack or "node"

        # Deployment methods
        if file.endswith(".tf"):
            deploy_method = deploy_method or "terraform"
        elif "k8s" in file or "deployment.yaml" in file:
            deploy_method = deploy_method or "k8s"
        elif "s3" in file:
            deploy_method = deploy_method or "s3"
        elif "dockerfile" in file or "docker" in file:
            deploy_method = deploy_method or "docker"

    return tech_stack, deploy_method

def build_workflow(blueprint, mode):
    parts = []
    if mode == "terraform":
        parts.append(Path(".ci/templates/deploy/terraform.yml").read_text())
    else:
        tech = blueprint["project"]["tech_stack"]
        deploy = blueprint["project"]["deploy_method"]
        if not tech or not deploy:
            raise ValueError("❌ Missing tech_stack or deploy_method in blueprint.")
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

    blueprint_file = Path(".ci/blueprint.yml")
    if blueprint_file.exists():
        blueprint = yaml.safe_load(blueprint_file.read_text())
    else:
        blueprint = {"project": {}}

    tech_stack = blueprint["project"].get("tech_stack")
    deploy_method = blueprint["project"].get("deploy_method")

    if not tech_stack or not deploy_method:
        auto_tech, auto_deploy = detect_tech_and_deploy()
        if not tech_stack:
            blueprint["project"]["tech_stack"] = auto_tech
        if not deploy_method:
            blueprint["project"]["deploy_method"] = auto_deploy

    build_workflow(blueprint, args.type)

if __name__ == "__main__":
    main()
