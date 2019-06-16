'''
Text
'''
import json
from matrix_client.api import MatrixHttpApi, MatrixRequestError
from flask import Flask, request
from flask.logging import create_logger
import settings

try:
    import local_settings as settings
except ImportError:
    pass

app = Flask(__name__) # pylint: disable=invalid-name
LOG = create_logger(app)
LOG.setLevel(settings.LOG_LEVEL)

LOG.info('Matrix server: %s', settings.MATRIX_SERVER)

@app.route("/", methods=['POST'])
def main_route():
    '''
    Other
    '''
    if request.method == 'POST':
        pingdom_payload = request.json
        current_state = pingdom_payload['current_state']
        previous_state = pingdom_payload['previous_state']

        if current_state == 'DOWN' and previous_state == 'UP':
            pingdom_payload.update({"state": "DOWN", "color": "#ff0000"})
        elif current_state == 'UP' and previous_state == 'DOWN':
            pingdom_payload.update({"state": "UP", "color": "#33cc33"})
        else:
            return "message did't change"

        message_plain = "[{check_name}] {description}".format(**pingdom_payload)
        message = """<p>
                        <strong>
                            <font color="{color}">[{check_name}] {description}</font>
                        </strong>
                    </p>
                    <blockquote>
                        <p>{long_description}</p>
                        <p><em>{state_changed_utc_time}</em></p>
                    </blockquote>""".format(**pingdom_payload)


        # Init matrix API
        matrix = MatrixHttpApi(settings.MATRIX_SERVER, token=settings.MATRIX_TOKEN)

        try:
            response = matrix.send_message_event(
                room_id=settings.MATRIX_ROOM,
                event_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "format": "org.matrix.custom.html",
                    "body": message_plain,
                    "formatted_body": message,
                }
            )
        except MatrixRequestError as ex:
            LOG.error('send_message_event failure %s', ex)
            return json.dumps({'success':False}), 417, {'ContentType':'application/json'}

        LOG.debug('Matrix Response: %s', response)
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    return json.dumps({'success':False}), 405, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8089, debug=settings.debug_enabled, threaded=True)
