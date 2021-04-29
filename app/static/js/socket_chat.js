function uuidv4() {
    // From the Internet
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

let socket;
let messages;
let current_user_uuid = uuidv4();
let messages_offset = 0;

document.addEventListener('DOMContentLoaded', () => {
    socket = io(window.location.href); // /chats/going
    messages = document.querySelector('.content__messages');
    let send_message_form = document.querySelector('#send_message_form');
    // Initial loading messages.
    socket.emit('get_more_messages', {'messages_offset': messages_offset});

    socket.on('connect', function () {
        socket.emit('enter_room');
    });

    socket.on('status', function (data) {
        console.log(data.message);
    });

    socket.on('print_message', function (data) {
        print_message(data);
        // increase not to obtain from db a duplicates of messages.
        messages_offset++;
        // to stay down after sending messages.
        messages.scrollTop = messages.scrollHeight;
    });

    socket.on('load_more_messages', function (data) {
        let scrollHeightOld = messages.scrollHeight;
        if (data['messages_number'] !== 0)
            load_more_messages(data);
        if (messages_offset === 0) {
            //to stay down after the first request to the server
            messages.scrollTop = messages.scrollHeight;
        } else {
            //not to move up after loading addition messages
            messages.scrollTop = messages.scrollHeight - scrollHeightOld;
        }
        // increase not to obtain from db a duplicates of messages.
        messages_offset += data['messages_number']
    });

    send_message_form.addEventListener('submit', (event) => {
        event.preventDefault();
        let message = new FormData(send_message_form).get('message').trim();
        if (message.length !== 0) {
            socket.emit('put_data', {
                'message': message,
                'timestamp_milliseconds': Date.now(),
                'uuid': current_user_uuid
            });
            send_message_form.querySelector('#input_message').value = '';
        }
    });
    messages.addEventListener('scroll', () => {
        if (messages.scrollTop === 0) {
            socket.emit('get_more_messages', {'messages_offset': messages_offset});
        }
    })

});

function get_current_user_message_div(message_text, timestamp_milliseconds) {
    let div_message = document.createElement('div');
    let div_time = document.createElement('div');
    let div_text = document.createElement('div');
    div_message.classList.add('message');
    div_time.classList.add('user_message_time');
    div_text.classList.add('user_message_text');
    div_time.innerText = new Date(timestamp_milliseconds).toLocaleTimeString();
    div_text.innerText = message_text;
    div_message.append(div_time, div_text);
    return div_message;
}

function get_companion_message_div(message_text, timestamp_milliseconds) {
    let div_message = document.createElement('div');
    let div_time = document.createElement('div');
    let div_text = document.createElement('div');
    div_message.classList.add('message');
    div_time.classList.add('companion_message_time');
    div_text.classList.add('companion_message_text');
    div_time.innerText = new Date(timestamp_milliseconds).toLocaleTimeString();
    div_text.innerText = message_text;
    div_message.append(div_text, div_time);
    return div_message;
}

function leave_room() {
    socket.emit('leave_room', () => {
        socket.disconnect();
        window.location.href = '/chats/end';
    });
}

function print_message(data) {
    if (data['uuid'] === current_user_uuid) {
        messages.append(get_current_user_message_div(data.message, data.timestamp_milliseconds));
    } else {
        messages.append(get_companion_message_div(data.message, data.timestamp_milliseconds));
    }
}

function load_more_messages(data) {
    for (let message of data['messages']) {
        if (message['is_current_user']) {
            messages.prepend(get_current_user_message_div(message['message_text'], message['timestamp_milliseconds']));
        } else {
            messages.prepend(get_companion_message_div(message['message_text'], message['timestamp_milliseconds']));
        }
    }
}
