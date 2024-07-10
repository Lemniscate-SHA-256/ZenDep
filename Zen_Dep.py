import re
import subprocess
import pkg_resources

def read_requirements(file_path):
    with open(file_path, 'r') as f:
        requirements = f.readlines()
    return [req.strip() for req in requirements]

def parse_requirement(req):
    match = re.match(r'([^=<>!]+)([=<>!]+.+)?', req)
    if match:
        package, version = match.groups()
        if version:
            version = version.strip()
        return package, version
    return req, None

def get_installed_packages():
    installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    return installed

def find_conflicts(requirements, installed):
    conflicts = []
    for req in requirements:
        package, version = parse_requirement(req)
        if package in installed:
            installed_version = installed[package]
            if version and not pkg_resources.Requirement.parse(req).specifier.contains(installed_version):
                conflicts.append((package, version, installed_version))
    return conflicts

def suggest_resolution(conflicts):
    resolutions = []
    for package, req_version, inst_version in conflicts:
        resolutions.append(f"{package} {req_version} conflicts with installed version {inst_version}.")
        resolutions.append(f"Suggested resolution: Update {package} to a compatible version.")
    return resolutions

def update_requirements(file_path, conflicts):
    updated_requirements = read_requirements(file_path)
    for package, req_version, _ in conflicts:
        for i, req in enumerate(updated_requirements):
            if req.startswith(package):
                updated_requirements[i] = f"{package}=={req_version.split('=')[-1]}"
    with open(file_path, 'w') as f:
        f.write('\n'.join(updated_requirements) + '\n')

def resolve_dependencies(requirements_file):
    requirements = read_requirements(requirements_file)
    installed = get_installed_packages()
    conflicts = find_conflicts(requirements, installed)
    if conflicts:
        print("Conflicts found:")
        for conflict in conflicts:
            print(conflict)
        resolutions = suggest_resolution(conflicts)
        for resolution in resolutions:
            print(resolution)
        update_requirements(requirements_file, conflicts)
        print(f"Updated {requirements_file} with suggested resolutions.")
    else:
        print("No conflicts found.")

if __name__ == "__main__":
    requirements_file = 'requirements.txt'
    resolve_dependencies(requirements_file)
