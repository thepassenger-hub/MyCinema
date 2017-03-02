from channels.routing import route
from live_chat.consumers import ws_connect, ws_disconnect, ws_chat_connect, ws_chat_disconnect


channel_routing = [
    route('websocket.connect', ws_connect, path=r"^/users/$"),
    route('websocket.disconnect', ws_disconnect, path=r"^/users/$"),
    route('websocket.connect', ws_chat_connect, path=r'^/inbox/$'),
    route('websocket.disconnect', ws_chat_disconnect, path=r'^/inbox/$'),
]