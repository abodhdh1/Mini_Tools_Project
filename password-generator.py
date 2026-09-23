import argparse
import secrets
import string
 
DEFAULT_LENGTH = 16
MAX_TRIES = 1000
 
 
def build_parser():
    parser = argparse.ArgumentParser(description="Generate a password")
    parser.add_argument('-l', action='store_true', help="use lowercase")
    parser.add_argument('-u', action='store_true', help="use uppercase")
    parser.add_argument('-d', action='store_true', help="use digits")
    parser.add_argument('-s', action='store_true', help="use symbols")
    parser.add_argument('-c', action='store_true', help="copy password to clipboard (needs pyperclip)")
    parser.add_argument('-f', action='store_true', help="require at least one character from every selected type")
    parser.add_argument('-n', default=DEFAULT_LENGTH, type=int, help=f"password length (default {DEFAULT_LENGTH})")
    parser.add_argument('--include', default="", type=str, help="extra characters to use, e.g. --include 'äö'")
    parser.add_argument('--exclude', default="", type=str, help="characters to never use (overrides --include)")
    parser.add_argument('-r', default=1, type=int, help="how many passwords to generate (default 1)")
    return parser
 
 
def build_groups(args, parser):
    """
    Return a list of character groups (strings) the password may use,
    with excluded characters already removed from every group.
    """
    selected = [
        (args.l, string.ascii_lowercase),
        (args.u, string.ascii_uppercase),
        (args.d, string.digits),
        (args.s, string.punctuation),
        (bool(args.include), args.include),
    ]
 
    groups = []
    for enabled, chars in selected:
        if not enabled:
            continue
        filtered = "".join(sorted(set(c for c in chars if c not in args.exclude)))
        if filtered:
            groups.append(filtered)
        elif args.f:
           
            parser.error("--exclude removed every character of a type required by -f")
    return groups
 
 
def has_all_types(password, groups):
    """True if the password contains at least one character from every group."""
    return all(any(c in password for c in group) for group in groups)
 
 
def make_password(pool, length, groups, force):
    for _ in range(MAX_TRIES):
        password = "".join(secrets.choice(pool) for _ in range(length))
        if not force or has_all_types(password, groups):
            return password
    raise ValueError(f"could not make a valid password after {MAX_TRIES} tries")
 
 
def main():
    parser = build_parser()
    args = parser.parse_args()
 
   
    if not any([args.l, args.u, args.d, args.s, args.include]):
        args.l = args.u = args.d = args.s = True
 
    groups = build_groups(args, parser)
    pool = "".join(sorted(set("".join(groups))))  
 
    
    if not pool:
        parser.error("no characters left to build a password from")
    if args.n < 1:
        parser.error("password length must be at least 1")
    if args.r < 1:
        parser.error("-r must be at least 1")
    if args.f and args.n < len(groups):
        parser.error(f"with -f the length must be at least {len(groups)} (one per character type)")
 
    try:
        passwords = [make_password(pool, args.n, groups, args.f) for _ in range(args.r)]
    except ValueError as e:
        parser.error(str(e))
 
    output = "\n".join(passwords)
    if args.c:
        try:
            import pyperclip  
        except ImportError:
            parser.error("-c needs pyperclip: pip3 install pyperclip")
        pyperclip.copy(output)
        print("Password copied to clipboard!")
    else:
        print(output)
 
 
if __name__ == "__main__":
    main()