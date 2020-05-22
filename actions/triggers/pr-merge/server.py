from nebula_sdk import Interface, WebhookServer
from quart import Quart, request, jsonify, make_response

import logging

relay = Interface()
app = Quart('pr-merge')

logging.getLogger().setLevel(logging.INFO)


@app.route('/', methods=['POST'])
async def handler():
    github_event = request.headers.get('X-GitHub-Event')

    if github_event is None:
        return await make_response(jsonify(message='not a valid GitHub event'), 400)
    if github_event == 'ping':
        return await make_response(jsonify(message='success'), 200)
    if github_event != 'pull_request':
        return await make_response(jsonify(message='only pull_request events are supported'), 400)

    logging.info("receiving event from GitHub: {}".format(github_event))

    event_payload = await request.get_json()
    if event_payload is None:
        return await make_response(jsonify(message='not a valid GitHub event'), 400)

    pr = event_payload['pull_request']
    if event_payload['action'] == 'closed' and pr['merged'] is True:
        relay.events.emit({
            'repository': event_payload['repository']['full_name'],
            'branch': pr['base']['ref']
        })

    return await make_response(jsonify(message='success'), 200)


if __name__ == '__main__':
    WebhookServer(app).serve_forever()
