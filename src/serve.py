from textual_serve.server import Server


def serve(config_path, port=8080, public_url=None, host='localhost'):
    server = Server(f'python textual_review_app/app.py {config_path}', host=host, port=port,
                    public_url=public_url)
    server.serve()


def main():
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('config_path',
                        help='Path to toml file.')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port (if not default)')
    parser.add_argument('--host', default='localhost',
                        help='Host (specify 0.0.0.0 to serve content)')
    parser.add_argument('--public-url', dest='public_url', default=None,
                        help='Public URL if using a reverse proxy to serve the application.')
    args = parser.parse_args()

    serve(args.config_path, host=args.host, port=args.port, public_url=args.public_url)


if __name__ == '__main__':
    main()
