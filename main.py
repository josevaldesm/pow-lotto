from aiohttp import web

from server.events import shutdown_handler
from server.models import LotteryState
from server.parser import get_args
from server.routes.handler import index_handler, websocket_handler


def main():
    args = get_args()
    app = web.Application()
    state = LotteryState(difficulty=args.difficulty)
    app["state"] = state
    print(
        "Initializating Lottery Server with current state:\n"
        f"\tCurrent Round: {state.round}\n"
        f"\tDifficulty: {state.difficulty}\n"
        f"\tCurrent Message: {state.current_message}\n"
    )
    app.add_routes([web.get("/", index_handler), web.get("/ws", websocket_handler)])
    app.on_shutdown.append(shutdown_handler)
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
