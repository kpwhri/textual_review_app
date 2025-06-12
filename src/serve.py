from textual_serve.server import Server


def serve(config_path, port=8080, public_url=None):
    server = Server(f'python textual_review_app/app.py {config_path}', port=port,
                    public_url=public_url)
    server.serve()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--config-path', dest='config_path', required=True,
                        help='Path to toml file.')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port (if not default)')
    parser.add_argument('--public-url', dest='public_url', default=None,
                        help='Public URL if using a reverse proxy to serve the application.')
    args = parser.parse_args()

    serve(args.config_path, args.port)
