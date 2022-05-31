""" The setup file for managing setup of the API """
import os, sys
import time
import xmltodict
import subprocess
import pytest

import setuptools
from setuptools.command.test import test as TestCommand

#repo/API meta info
API_name = 'jlUtils'
url="https://github.com/jlnerd/jlUtils"
repo_dir = os.path.dirname(__file__)
exclude_dirs = ["tests", "scipts", "docs"]
scripts = ["scripts/%s" % f for f in os.listdir("scripts")]
README = open(str(repo_dir.joinpath("README.md"))).read()

# Code coverage and quality thresholds
coverage_threshold = 0.0
quality_threshold = 0.0

def run_command(command, raise_=True, verbose=True):
    """
    Executes a terminal/bash/CLI command passed as a string and returns 
    the outputs or raises an error if the command fails
    
    Args:
        command: string. The command to be executed
        raise_: boolean. whether or not to raise an exception if an error occurs
        
    Returns:
        output: string. The CLI/terminal/bash output
    """
    if verbose: print('command:\n\t'+command)

    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        e = BaseException(e.output.decode("utf-8"))
        if raise_:
            raise e
        else:
            output = str(e)
                
    if verbose: print('output:\n\t'+output)

    return output

def fetch_branch_name(verbose=True):
    """
    Fetch the branch name from the CI env. variables
    
    Args:
        verbose: boolean. Whether or not to print outputs

    Returns:
        branch_name. string. The GIT_BRANCH used in the pipeline (i.e. the RIO_BRANCH_NAME)
    """
    if "GIT_BRANCH" in os.environ:
        if "prb" in os.environ["BUILD_SPEC_ID"]:
            branch_name = "PRB"
        else:
            branch_name = os.environ["GIT_BRANCH"]
    else:
        branch_name = "PRB"

    if verbose:
        print("\n" + f"branch_name: {branch_name}" + "\n")

    return branch_name

def fetch_current_version(API_name):
    """
    Fetch current versions from the __init__.py file after update
    
    Args:
        API_name: str. The name of the API
    
    Returns:
        current_version: str. The current version number from
            the __init__.py file for the API
    """
    with open(os.path.join(API_name, "__init__.py"), "r") as f:
        text = f.read()
        current_version = (
            text.split("__version__")[1]
            .split("\n")[0]
            .replace('"', "")
            .replace(" ", "")
            .replace("=", "")
        )
    return current_version


def fetch_new_tag(version, branch_name, push_to_branch=True, verbose=True):
    """
    Fetch a tagged version name based on the passed `version` 
    and `branch_name`. Then, if `push_to_branch`, push the new tag to github
    
    Args:
        version:
    """
    #don't raise errors of `run_command`
    raise_ = False

    if branch_name == "master":
        new_tag = f"v{version}"
    elif branch_name in ["qa", 'dev']:
        new_tag = f"v{version}.{branch_name}"
    else:
        new_tag = f"v{version}.ftdev"

    current_tags = run_command(f"git tag", rasie_, verbose)

    if new_tag in current_tags and push_to_branch:  # delete the tag
        run_command(f"git tag -d {new_tag}", raise_, verbose)
        run_command(f"git push --delete origin -d {new_tag}", raise_, verbose)

    run_command(f"git tag {new_tag}", raise_, verbose)
    run_command(f"git add .", raise_, verbose)

    # push the new tag
    run_command(f"git push origin {new_tag}", raise_, verbose)
    
    if push_to_branch:
        run_command(f'git commit -m "tag update"', raise_, verbose)
        run_command(f"git push origin {branch_name}", raise_, verbose)

    return new_tag

def fetch_remote_versions():
    remote_versions = run_command("git ls-remote --tags")
    remote_versions = [
        line.split("refs/tags/")[1].replace("v", "")
        for line in remote_versions.split("\n")
        if "refs/tags/" in line
    ]
    remote_versions = [
        version.split("-")[0] for version in remote_versions
    ]  # drop the -rc suffixes
    remote_versions = [
        ".".join(version.split(".")[:3]) for version in remote_versions
    ]  # only get the first 3 version IDs split by '.'
    return remote_versions

def fetch_new_version(current_version, version_increment, remote_versions):
    if current_version in remote_versions:  # update
        while current_version in remote_versions:
            new_version = []
            for current, increment in zip(
                current_version.split("."), version_increment.split(".")
            ):
                new_version.append(str(int(current) + int(increment)))
                if increment == "1":
                    break

            # append 0's for new major or minor versions
            if len(new_version) == 1:
                new_version += ["0", "0"]
            elif len(new_version) == 2:
                new_version += ["0"]

            new_version = ".".join(new_version)
            current_version = new_version
    else:  # don't update
        new_version = current_version
    return new_version

def write_new_version(name, current_version, new_version):
    with open(os.path.join(name, "__init__.py"), "r+") as f:
        update = f.read().replace(current_version, new_version)
        f.write(update)

def auto_tag():
    """
    Automatically pushes a tagged version of the repo/API to github
    
    Args:
        name: string. The name of the API directory (i.e. fuegodata)
        verbose: boolean. Whether to print-out various statements during auto-versioning
        tag: boolean. Whether or not to tag the version
        
    Returns:
        version: The version string after updating
    """
    if not tag:
        version_tag = fetch_current_version(name)

    else:
        branch_name = fetch_branch_name()

        if branch_name is "PRB":

            if verbose:
                print(
                    f"branch_name is {branch_name}"
                    + "\nThe version will not be updated and no tag will be generated for git.\n"
                )

            version_tag = fetch_current_version(name) + ".dev" + str(int(time.time()))

        else:

            run_command('git config --global user.email ""')
            run_command('git config --global user.name ""')

            run_command("git init")
            run_command("git fetch")
            run_command(f"git checkout {branch_name}")

            # Remove rio added files/folders
            for file in [".rio-env", ".rio-user-env"]:
                if os.path.isfile(file):
                    os.remove(file)

            # Inspect the last commit message
            commit_message = run_command("git log -1")

            version_increments = {
                "MAJOR": "1.0.0",
                "MINOR": "0.1.0",
                "PATCH": "0.0.1",
                "version update": "0.0.0",
            }

            versioning_commit = False
            for version_increment_key in version_increments:
                if version_increment_key in commit_message:
                    versioning_commit = True
                    break
            forced_tagging_branches = ["master", "qa", "test", "dev"]
            if (
                versioning_commit is False
                and branch_name not in forced_tagging_branches
            ):

                print(
                    f"Branch is not in {forced_tagging_branches}"
                    + " and commit message did not contain any of the version_increment keys:"
                    + f"{str(list(version_increments.keys()))}"
                    + "\nThe version will not be updated and no tag will be generated for git.\n"
                )

                version_tag = (
                    fetch_current_version(name) + ".dev" + str(int(time.time()))
                )

            else:

                if branch_name in forced_tagging_branches:
                    version_increment_key = (
                        "version update"  # Force tagging for master and dev branches
                    )

                version_increment = version_increments[version_increment_key]

                # Fetch existing tags:
                remote_versions = fetch_remote_versions()

                current_version = fetch_current_version(name)

                if verbose:
                    print(f"current_version: {current_version}")

                if (
                    "version update" in version_increment_key
                ):  # Don't push to the repo, just update the tag

                    version_tag = tag_new_version(
                        current_version, branch_name, push_to_branch=False
                    )

                else:  # push a new tag and update the version in the branch

                    new_version = fetch_new_version(
                        current_version, version_increment, remote_versions
                    )

                    if verbose:
                        print(f"new_version: {new_version}" + "\n")

                    write_new_version(name, current_version, new_version)

                    version_tag = tag_new_version(
                        new_version, branch_name, push_to_branch=True
                    )

    if verbose:
        print(f"version tag: {version_tag}" + "\n")

    return version_tag


def get_requirements(requirements="requirements.txt"):
    """Get the list of requirements from the pip `requirements` file.
    Args:
        requirements (str): path to the pip requirements file.
    Examples:
        ['django==1.5.1', 'mezzanine==1.4.6']
    Returns:
        List[str]: the list of requirements
    """
    requirements_fpath = os.path.join(repo_dir, "requirements.txt")

    with open(requirements_fpath, "r") as requirements_txt:
        install_reqs = [
            str(requirement)
            for requirement in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_reqs

class PyTest_PyLint_Tests(TestCommand):

    """
    Setup a custom py.test test runner which calls pytest and 
    pylint and checks whether or not the code satisfies the 
    coverage_threshold and quality_threshold specified
    """

    def finalize_options(self):
        """Set options for the command line."""

        TestCommand.finalize_options(self)

        self.test_args = [str(repo_dir)]

        self.pytest_args = [
            str(repo_dir),
            f"--cov={API_name}",
            "--cov-report=term",  # Print coverage report to terminal
            f'--cov-report=xml:{os.path.join(repo_dir, "cov.xml")}',
            "-x",  # Escape/end after first failed test
        ]

        self.pylint_args = [
            str(repo_dir.joinpath("fuegodata")),
            "-d "
            + ",".join(  # List out error codes to ignore
                [
                    "C0303",  # trailing white spaces
                    "C0103",  # Argument name doesn't conform to snake_case naming style
                    "C0305",  # Trailing newlines'
                    "W0201",  # Class attribute defined outside __init__
                    "C0304",  # Final newline missing
                    "E221",  # multiple spaces before operator
                    "C0413",  # wrong import position
                    "C0330",  # Wrong hanging indentation before bloc
                    "W0621",  # redefined-outer-name
                    "R0913",  # too-many-arguments
                    "R0914",  # too-many-locals
                    "W0102",  # dangerous-default-value
                    "R1715",  # Consider using dict.get for getting values from a dict
                    "W0212",  # Access to a protected member _<function> of a client class
                    "R0902",  # Too many instance attributes'
                    "W1203",  # Use lazy % formatting in logging functions
                    "W1201",  # Use lazy % formatting in logging functions
                    "W0703",  # Catching too general exception Exception (broad-except)
                    "R0201",  # Method could be a function (no-self-use"
                ]
            ),
        ]

        self.bats_command = " ".join(["bats", "tests/test_preprocess.sh"])

        self.test_suite = True

    def fetch_coverage_prc(self):
        """
        Fetch the coverage percent from the cov.xml file generated during setup via the PyTest class
        """

        time.sleep(1)

        with open(repo_dir.joinpath("cov.xml"), "r") as f:
            coverage = xmltodict.parse(f.read())

        coverage = coverage[list(coverage.keys())[0]]

        coverage_prc = float(coverage["@line-rate"])

        return coverage_prc

    def run_pylint(self):
        """
        Executes pytlint returning the output string and the code_quality score (x/10)
        Returns:
            code_quality: float. The code quality score (out of 10)
        """

        print("\ncoverage_threshold:", coverage_threshold)
        print("quality_threshold:", quality_threshold)

        print("\nrunning pylint")
        print("\npylint args:\n\t" + "\n\t".join(self.pylint_args), "\n")

        pylint_command = "pylint " + " ".join(self.pylint_args)

        try:  # Dummy try statement (pylint returns outputs as an error)

            subprocess.check_output(
                pylint_command, stderr=subprocess.STDOUT, shell=True
            ).decode("utf-8")

        except subprocess.CalledProcessError as e:

            output = e.output.decode("utf-8")

            # Strip out the repo_dir from the file paths in the output to make things less verbose
            output = output.replace(str(repo_dir) + "/", "")
            print(output)

        code_quality = output.split("Your code has been rated at ")[1]
        code_quality = float(code_quality.split("/10")[0])

        return code_quality

    def run_script_tests(self):
        """
        execute script tests using bats and return
        the number of failed .sh tests.
        If a failure occurs an error will be thrown
        """

        print("\nrunning bats tests")

        print("bats commands:\n\t" + self.bats_command)

        outputs = run_command(self.bats_command)
        print(outputs)

    def run_tests(self):
        """
        Execute the test runner command with run_pylint() as a sub-function
        """
        # Update the version
        auto_version(name, verbose=True)

        print(
            "\ncoverage_threshold",
            coverage_threshold,
            "\nquality_threshold:",
            quality_threshold,
        )

        print("\nrunning pytest")
        print("\npytest args:\n\t" + "\n\t".join(self.pytest_args), "\n")
        pytest_outputs = pytest.main(self.pytest_args)

        coverage_prc = self.fetch_coverage_prc()

        self.run_script_tests()

        code_quality = self.run_pylint()

        errors = []
        if coverage_prc < coverage_threshold:
            errors.append(
                f"\ncoverage {round(coverage_prc*100,2)}% "
                +f'< coverage threshold {coverage_threshold*100}%. '
                +'Add more unit tests to satisfy coverage threshold"
            )

        if code_quality < quality_threshold:
            errors.append(
                f"\npylint code quality {code_quality}/10 "
                +f'< quality threshold {quality_threshold}/10. '
                'Cleanup the code based on the pylint outputs.'
            )

        if len(errors) > 0:
            raise (AssertionError("\n\t".join(Errors)))

        sys.exit(pytest_outputs)

setuptools.setup(
    name=API_name,
    url=url,
    description=API_name,
    long_description=README,
    long_description_content_type="text/markdown",
    version=auto_version(name, verbose=False, tag=False),
    scripts=scripts,
    include_package_data=True,
    packages=setuptools.find_packages(exclude=exclude_dirs),
    classifiers=["Development Status :: 4 - Beta",],
    install_requires=get_requirements(),
    setup_requires=['setuptools', "pytest", 'pylint', 'xmltodict'],
    tests_require=["pytest", 'pylint', 'xmltodict'],
    cmdclass={"test": PyTest_PyLint_Tests},
    zip_safe=False,
)
