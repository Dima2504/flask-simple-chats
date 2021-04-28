let socket;
document.addEventListener('DOMContentLoaded', () => {
    socket = io(window.location.href); // /chats/going
    socket.on('connect', function () {
        console.log('connected');
        socket.emit('enter_room');
    });

    socket.on('status', function (data) {
        console.log(data.message);
    });

    socket.on('print_message', function (data) {
        console.log(data['user_name'] + ': ' + data['message']);
        let area = document.querySelector('#chat');
        area.value = area.value + data['user_name'] + ': ' + data['message'] + '\n';
    });

    let send_message_form = document.querySelector('#send_message_form');
    send_message_form.addEventListener('submit', (event) => {
        event.preventDefault();
        let message = new FormData(send_message_form).get('message').trim();
        if (message.length !== 0) {
            socket.emit('put_data', {'message': message, 'timestamp_seconds': Date.now() / 1000});
            send_message_form.querySelector('#message').value = '';
        }
    });
});

function leave_room() {
    socket.emit('leave_room', () => {
        socket.disconnect();
        window.location.href = '/chats/end';
    });
}