function uuidv4() {
    // From the Internet
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function print_message(data) {
    if (data['uuid'] === current_user_uuid) {
        let div_message = document.createElement('div');
        let div_time = document.createElement('div');
        let div_text = document.createElement('div');
        div_message.classList.add('message');
        div_time.classList.add('user_message_time');
        div_text.classList.add('user_message_text');
        div_time.innerText = new Date(data.timestamp_milliseconds).toLocaleTimeString();
        div_text.innerText = data.message;
        div_message.append(div_time, div_text);
        messages.append(div_message);
    } else {
        let div_message = document.createElement('div');
        let div_time = document.createElement('div');
        let div_text = document.createElement('div');
        div_message.classList.add('message');
        div_time.classList.add('companion_message_time');
        div_text.classList.add('companion_message_text');
        div_time.innerText = new Date(data.timestamp_milliseconds).toLocaleTimeString();
        div_text.innerText = data.message;
        div_message.append(div_text, div_time);
        messages.append(div_message);
    }
}

function leave_room() {
    socket.emit('leave_room', () => {
        socket.disconnect();
        window.location.href = '/chats/end';
    });
}

let socket;
let messages;
let send_message_form;
let current_user_uuid = uuidv4();
document.addEventListener('DOMContentLoaded', () => {
    socket = io(window.location.href); // /chats/going
    messages = document.querySelector('.content__messages');
    send_message_form = document.querySelector('#send_message_form');

    socket.on('connect', function () {
        console.log('connected');
        socket.emit('enter_room');
    });

    socket.on('status', function (data) {
        console.log(data.message);
    });

    socket.on('print_message', function (data) {
        print_message(data);
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
});
