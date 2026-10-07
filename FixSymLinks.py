"""
Jatin Gandhi
Python code to fix broken symbolic link. See prompt for more details.

Generated with AI.
Fixed few correction on my own.
prompt:
I have a qt library folder with broken symbolic links.
Symbolic links are replaced with the file link name
file containing file name it used to point to. 
E.g., libQtWidget.so contains the actual file name 
it used to point to libQtWidget.so.5.15.7.

Write a python program to find all symbolic links 
and fix it.

I mean find a symbolic link file
(it will be ascii file instead of 
symbolic link) ,
read the name it used to point to,
remove that ascii file and 
create a symbolic link and point it 
to actual file name we just read from it.
"""
#!/usr/bin/env python3

import argparse
import os
import sys


MAX_TEXT_FILE_SIZE = 4096


def read_symlink_target_file(path):
    """
    Return the presumed symlink target if 'path' is a small ASCII text file.

    Otherwise return None.
    """
    try:
        # Never touch an actual symbolic link.
        if os.path.islink(path):
            return None

        # A replacement symlink file should be tiny.
        if os.path.getsize(path) > MAX_TEXT_FILE_SIZE:
            return None

        # It should end with exactly .so, not .so.5 or not .so.5.6
        if not path.endswith(".so"):
            return None

        with open(path, "rb") as f:
            data = f.read()

        # Must contain valid ASCII.
        text = data.decode("ascii").strip()

        # Validate if file has valid text and it is pointing to .so library file
        if not text:
            return None

        if not ".so" in text:
            return None;

        # The target should be a single line.
        if "\n" in text or "\r" in text:
            return None

        return text

    except (OSError, UnicodeDecodeError):
        return None


def fix_symlinks(root, do_fix=False):
    fixed = 0
    candidates = 0
    skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            path = os.path.join(dirpath, filename)

            # Don't touch real symlinks.
            if os.path.islink(path):
                continue

            target = read_symlink_target_file(path)
            if target is None:
                continue

            candidates += 1

            # The original symlink target is relative to the symlink's
            # containing directory.
            target_path = os.path.join(dirpath, target)

            # Don't modify anything if the target doesn't exist.
            if not os.path.exists(target_path):
                print(f"SKIP: {path}")
                print(f"      target does not exist: {target}")
                skipped += 1
                continue

            if not os.path.isfile(target_path) and not os.path.islink(target_path):
                print(f"SKIP: {path}")
                print(f"      target is not a regular file/symlink: {target}")
                skipped += 1
                continue

            if do_fix:
                print(f"FIX:  {path} -> {target}")

                try:
                    # Remove the ASCII replacement file.
                    os.remove(path)

                    # Recreate the original symbolic link.
                    os.symlink(target, path)

                    fixed += 1

                except OSError as e:
                    print(f"ERROR: could not fix {path}: {e}", file=sys.stderr)
                    skipped += 1

            else:
                print(f"WOULD FIX: {path} -> {target}")

    print()
    print("Summary")
    print("-------")

    if do_fix:
        print(f"Fixed:      {fixed}")
    else:
        print(f"Candidates: {candidates}")
        print("Nothing changed (dry-run).")
        print("Run again with --fix to make the changes.")

    print(f"Skipped:    {skipped}")


def main():
    parser = argparse.ArgumentParser(
        description="Repair Qt symlinks that were replaced by ASCII files."
    )

    parser.add_argument(
        "directory",
        help="Qt library directory to scan recursively"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Actually replace ASCII files with symbolic links"
    )

    args = parser.parse_args()

    root = os.path.abspath(args.directory)

    if not os.path.isdir(root):
        print(f"Error: not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning: {root}")

    if args.fix:
        print("MODE: FIX -- files will be modified")
    else:
        print("MODE: DRY-RUN -- no files will be modified")

    print()

    fix_symlinks(root, do_fix=args.fix)


if __name__ == "__main__":
    main()

