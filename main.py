import argparse

from fbserver import database, app


def main():
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(title="Subcommands", dest="cmd")
    db_p = subp.add_parser("db")
    db_p.add_argument("db_cmd")
    run_p = subp.add_parser('run')
    create_and_run_p = subp.add_parser('create_and_run')

    args = parser.parse_args()

    if args.cmd == "db":
        if args.db_cmd == "create":
            database.create_all()
        elif args.db_cmd == "destroy":
            database.drop_all()
    elif args.cmd == "run":
        app.run(host='0.0.0.0', debug=True)
    elif args.cmd == "create_and_run":
        database.create_all()
        app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    main()
