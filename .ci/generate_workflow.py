import argparse
import yaml
from pathlib import Path
import subprocess


def get_current_branch():
    """Detect the current Git branch."""
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
        return branch
    except subprocess.CalledProcessError:
        return None


def get_branching_rules(branch):
    """
    Returns the YAML for branch/tag rules for the current branch only.
    Properly indented for GitHub Actions syntax.
    """
    return f"""
  push:
    branches:
      - {branch}
    paths:
      - '**/*.java'
      - '**/*.py'
      - '**/*.cpp'
      - '**/*.cxx'
      - '**/Dockerfile'
      - '.ci/**'
    tags:
      - 'v*.*.*'  # semantic version tags like v1.0.0
"""


def inject_branch_rules(content):
    """
    Finds the 'workflow_dispatch:' section in the template
    and adds branch/tag rules right after it, preserving indentation.
    """
    branch = get_current_branch() or "main"
    rules = get_branching_rules(branch)

    if "on:" in content and "workflow_dispatch:" in content:
        return content.replace("workflow_dispatch:", f"workflow_dispatch:\n{rules}", 1)
    return content


def detect_tech_and_deploy():
    """Detect tech stack and deployment method based on changed files."""
    try:
        changed_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"], text=True
        ).splitlines()
        print("------------------")
        print(changed_files)
        print("------------------")
    except subprocess.CalledProcessError:
        print("⚠️ Could not get changed files from git.")
        return set(), set()

    tech_stacks = set()
    deploy_methods = set()

    for file in changed_files:
        file = file.lower()

        # Tech stack detection
        if file.endswith(".py"):
            tech_stacks.add("python")
        elif file.endswith(".java"):
            tech_stacks.add("java")
        elif file.endswith(".cpp") or file.endswith(".cxx"):
            tech_stacks.add("cpp")
        elif file.endswith(".js") or "node_modules" in file:
            tech_stacks.add("node")

        # Deployment method detection
        if file.endswith(".tf"):
            deploy_methods.add("terraform")
        elif "k8s" in file or "deployment.yaml" in file:
            deploy_methods.add("k8s")

    # Default to docker if other deploy methods not found
    if not deploy_methods and tech_stacks:
        deploy_methods.add("docker")

    print(f"📦 Detected tech_stacks: {tech_stacks}, deploy_methods: {deploy_methods}")
    return tech_stacks, deploy_methods


def build_workflow(tech, deploy):
    """Builds the final workflow YAML from templates."""
    parts = []

    try:
        tech_content = Path(f".ci/templates/{tech}.yml").read_text()

        # Inject branch rules only if NOT Terraform
        if deploy != "terraform":
            tech_content = inject_branch_rules(tech_content)

        parts.append(tech_content)
    except FileNotFoundError:
        print(f"⚠️ Template not found for tech: {tech}")
        return

    # Append test step if available
    test_path = Path(".ci/templates/test.yml")
    if test_path.exists():
        parts.append(test_path.read_text())

    try:
        deploy_content = Path(f".ci/templates/deploy/{deploy}.yml").read_text()
        parts.append(deploy_content)
    except FileNotFoundError:
        print(f"⚠️ Deployment template not found for: {deploy}")
        return

    final = "\n".join(parts)
    filename = f".github/workflows/generated_{tech}_{deploy}.yml"
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

    # Terraform-only run
    if args.type == "terraform":
        terraform_path = Path(".ci/templates/deploy/terraform.yml")
        if terraform_path.exists():
            terraform_content = terraform_path.read_text()
            # No branch rules for Terraform
            Path(".github/workflows/generated-terraform.yml").write_text(terraform_content)
            print("✅ Generated Terraform-only pipeline.")
        else:
            print("❌ Missing .ci/templates/deploy/terraform.yml")
        return

    # Auto-detect if missing
    if not tech_stack or not deploy_method:
        detected_techs, detected_deploys = detect_tech_and_deploy()
    else:
        detected_techs = {tech_stack}
        detected_deploys = {deploy_method}

    # If still missing, exit
    if not detected_techs or not detected_deploys:
        print("❌ tech_stack or deploy_method is missing and could not be auto-detected.")
        print("➡️ Please either:")
        print("   • Set them manually in .ci/blueprint.yml")
        print("   • Or ensure recent commits include files related to Python/Java/etc. and Terraform/Docker/S3/etc.")
        exit(1)

    # Build workflows
    for tech in detected_techs:
        for deploy in detected_deploys:
            build_workflow(tech, deploy)


if __name__ == "__main__":
    main()
