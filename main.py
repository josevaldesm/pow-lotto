from aiohttp import web

from proyecto.events import shutdown_handler
from proyecto.models import LotteryState
from proyecto.parser import get_args
from proyecto.routes.handler import index_handler, websocket_handler


def main():
    args = get_args()
    app = web.Application()
    app["state"] = LotteryState()
    app.add_routes([web.get("/", index_handler), web.get("/ws", websocket_handler)])

    # app.on_shutdown(shutdown_handler)
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
