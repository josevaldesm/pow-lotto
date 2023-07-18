from aiohttp import web

from server.events import shutdown_handler
from server.models import LotteryState
from server.parser import get_args
from server.routes.handler import index_handler, websocket_handler


def main():
    args = get_args()
    app = web.Application()
    state = LotteryState(difficulty=args.difficulty, max_rounds=args.max_rounds if args.max_rounds != -1 else None, evaluate=args.evaluate)
    app["state"] = state
    if args.evaluate is False:
        print(
            "Initializating Lottery Server with current state:\n"
            f"\tCurrent Round: {state.round}\n"
            f"\tDifficulty: {state.difficulty}\n"
            f"\tCurrent Message: {state.current_message}\n"
        )
    app.add_routes([web.get("/", index_handler), web.get("/ws", websocket_handler)])
    app.on_shutdown.append(shutdown_handler)
    web.run_app(app, host=args.host, port=args.port, access_log=None)


if __name__ == "__main__":
    main()
