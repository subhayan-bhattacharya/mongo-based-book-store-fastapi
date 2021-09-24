import os

import nox


@nox.session
def flake8(session):
    session.install("flake8")
    session.run(
        "flake8",
        "--exclude",
        ".git,.nox",
        "--max-line-length",
        "91",
        "--ignore",
        "E203",
    )


@nox.session
def tests_unit(session):
    session.install(
        "-r",
        "requirements/tests.txt",
        "-r",
        "requirements/requirements.txt",
    )
    os.chdir("tests")
    session.run("python", "-m", "pytest", "-s", "-v", "unit")


@nox.session
def tests_integration(session):
    session.install(
        "-r",
        "requirements/integration.txt",
        "-r",
        "requirements/tests.txt",
        "-r",
        "requirements/requirements.txt",
    )
    os.chdir("tests")
    session.run("python", "-m", "pytest", "-s", "-v", "integration")
