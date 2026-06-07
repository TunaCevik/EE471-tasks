import sys


def bump_version():
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
        with open("VERSION", "w") as f:
            f.write(new_version)
        print(f"Version updated to {new_version}")
    else:
        print("Error: No version string provided.")
        sys.exit(1)


if __name__ == "__main__":
    bump_version()
