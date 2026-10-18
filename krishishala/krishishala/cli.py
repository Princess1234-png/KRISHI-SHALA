"""Command line entry point: python -m krishishala.cli <command>."""
import argparse
import json

from . import analytics, api, db, ingest


def main(argv=None):
    p = argparse.ArgumentParser(prog="krishishala")
    p.add_argument("--db", default="krishishala.db")
    sub = p.add_subparsers(dest="cmd", required=True)
    load = sub.add_parser("load", help="load sample schools and readings")
    load.add_argument("--schools", default="data/sample_schools.json")
    load.add_argument("--readings", default="data/sample_readings.csv")
    serve = sub.add_parser("serve", help="run the HTTP API")
    serve.add_argument("--port", type=int, default=8000)
    cmp_ = sub.add_parser("compare", help="compare two schools")
    cmp_.add_argument("a", type=int)
    cmp_.add_argument("b", type=int)
    args = p.parse_args(argv)

    conn = db.connect(args.db)
    if args.cmd == "load":
        ingest.load_schools(conn, args.schools)
        loaded, rejected = ingest.load_readings_csv(conn, args.readings)
        print(f"loaded {loaded} readings, rejected {rejected}")
    elif args.cmd == "serve":
        server = api.make_server(conn, port=args.port)
        print(f"Serving on http://127.0.0.1:{args.port}")
        server.serve_forever()
    elif args.cmd == "compare":
        result = analytics.compare(db.readings_for(conn, args.a), db.readings_for(conn, args.b))
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
