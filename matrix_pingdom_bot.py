'''
Text
'''
import json
import ast
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

def check_token(token):
    '''
    check_token function
    '''
    if token in ACCESS_TOKENS.values():
        return True
    return False

def check_room(room):
    '''
    check_room function
    '''
    # matrix_rooms = ast.literal_eval(matrix_rooms)
    if room in MATRIX_ROOMS.keys():
        return MATRIX_ROOMS[room]
    return False

def send_message(matrix_room, message_plain, message):
    '''
    One day
    '''
    # Init matrix API
    matrix = MatrixHttpApi(settings.MATRIX_SERVER, token=settings.MATRIX_TOKEN)

    try:
        response = matrix.send_message_event(
            room_id=matrix_room,
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

def prepare_message(matrix_room):
    '''
    One day
    '''
    pingdom_payload = request.json
    current_state = pingdom_payload['current_state']
    previous_state = pingdom_payload['previous_state']

    if current_state == 'DOWN' and previous_state == 'UP':
        pingdom_payload.update({"state": "DOWN", "color": "#ff0000"})
    elif current_state == 'UP' and previous_state == 'DOWN':
        pingdom_payload.update({"state": "UP", "color": "#33cc33"})
    else:
        return json.dumps({'success': True, 'message': 'nothing changed'}), 200, {'ContentType':'application/json'} # pylint: disable=line-too-long

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

    return send_message(matrix_room, message_plain, message)


# Normalizing dictionary when comes from an environment variable
if isinstance(settings.ACCESS_TOKENS, str):
    ACCESS_TOKENS = ast.literal_eval(settings.ACCESS_TOKENS)
else:
    ACCESS_TOKENS = settings.ACCESS_TOKENS

# Normalizing dictionary when comes from an environment variable
if isinstance(settings.MATRIX_ROOMS, str):
    MATRIX_ROOMS = ast.literal_eval(settings.MATRIX_ROOMS)
else:
    MATRIX_ROOMS = settings.MATRIX_ROOMS

@app.route("/", methods=['GET', 'POST'])
def main_route():
    '''
    Other
    '''

    # Validating token
    token = request.args.get('token')
    if token:
        is_valid_token = check_token(token)

        if not is_valid_token:
            return json.dumps({'success':False, 'reason': 'token not valid'}), 403, {'ContentType':'application/json'} # pylint: disable=line-too-long
    else:
        return json.dumps({'success':False, 'reason': 'token not provided'}), 403, {'ContentType':'application/json'} # pylint: disable=line-too-long


    # Validating room
    room = request.args.get('room')

    if room:
        matrix_room = check_room(room)

        if not matrix_room:
            return json.dumps({'success':False, 'reason': 'room not valid'}), 403, {'ContentType':'application/json'} # pylint: disable=line-too-long
    else:
        return json.dumps({'success':False, 'reason': 'room not provided'}), 403, {'ContentType':'application/json'} # pylint: disable=line-too-long



    if request.method == 'POST':

        return prepare_message(matrix_room)



    return json.dumps({'success':False}), 405, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8089, debug=settings.debug_enabled, threaded=True)
