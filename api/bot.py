from sanic import Sanic, response

from Testbot import bot_register

# https://api.telegram.org/bot{your_bot_token}/setWebhook?url={your_vercel_domain_url}/api/bot

app = Sanic(__name__)


@app.route("/api/bot", strict_slashes=False)
async def _bot(request):
    bot_register(True)
    return response.text("This endpoint is meant for bot and telegram communication.")


if __name__ == "__main__":
    app.run(debug=True, auto_reload=True, host="0.0.0.0", port=8080)