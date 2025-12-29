#!/usr/bin/env python

"""Interactive REPL for reading and writing Vestaboard messages.

Commands:
    read        - Read the current message from the board
    write TEXT  - Write a text message to the board
    clear       - Clear the board (write blank message)
    quit        - Exit the REPL
"""

import argparse
import readline

import vesta


def setup_readline():
    """Configure readline with command completion."""
    commands = ["read", "write ", "clear", "quit", "exit", "help"]

    def completer(text, state):
        options = [cmd for cmd in commands if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    readline.set_completer(completer)

    # Different readline implementations use different syntax
    if "libedit" in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--rw-key", metavar="KEY", help="Read/Write API key")
    group.add_argument("--local-key", metavar="KEY", help="Local API key")

    args = parser.parse_args()

    if args.rw_key:
        client = vesta.ReadWriteClient(args.rw_key)
        print("Connected via Read/Write API\n")
    else:
        client = vesta.LocalClient(args.local_key)
        print("Connected via Local API\n")

    setup_readline()
    print("Vestaboard REPL - Type 'help' for commands\n")

    while True:
        try:
            command = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not command:
            continue

        if command in ("quit", "exit"):
            print("Goodbye!")
            break

        if command == "help":
            print(__doc__)
            continue

        if command == "read":
            try:
                message = client.read_message()
                if message:
                    vesta.pprint(message)
                else:
                    print("(board is empty)")
            except Exception as e:
                print(f"Error reading message: {e}")
            continue

        if command == "clear":
            try:
                blank = [[0] * 22] * 6
                if client.write_message(blank):
                    print("Board cleared")
                else:
                    print("Failed to clear board")
            except Exception as e:
                print(f"Error clearing board: {e}")
            continue

        if command.startswith("write "):
            text = command[6:].strip()
            if not text:
                print("Usage: write TEXT")
                continue

            try:
                chars = vesta.encode_text(text, valign="middle")
                if client.write_message(chars):
                    print("Message sent!")
                    vesta.pprint(chars)
                else:
                    print("Failed to send message")
            except ValueError as e:
                print(f"Error encoding message: {e}")
            except Exception as e:
                print(f"Error writing message: {e}")
            continue

        print(f"Unknown command: {command}")
        print("Type 'help' for available commands")


if __name__ == "__main__":
    main()
