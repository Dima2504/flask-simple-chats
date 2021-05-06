document.addEventListener('DOMContentLoaded', () => {
    let search_form = document.querySelector('.search-form form');
    search_form.addEventListener('submit', (event) => {
        event.preventDefault();
        document.getElementById('search-button').blur();
        let search_string = new FormData(search_form).get('search-string');
        if (search_string.length !== 0) {
            let url = '/chats/ajax-search?' + new URLSearchParams({'search-string': search_string}).toString();
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-type': 'application/x-www-form-url',
                }
            }).then(response => {
                return response.json()
            }).then(data => {
                let ul_content__searched_users = document.querySelector('.content__searched_users ul');
                ul_content__searched_users.innerHTML = '';
                let users = data['data'];
                if (users.length === 0) {
                    let h1 = document.getElementById('not-found');
                    if (!h1) {
                        let h1 = document.createElement('h1');
                        h1.innerText = 'Nothing is found';
                        h1.id = 'not-found';
                        document.querySelector('.content__search').append(h1);
                    }
                    document.querySelector('.edge').style.opacity = '0';
                } else {
                    document.querySelector('.edge').style.opacity = '1';
                    let h1 = document.getElementById('not-found');
                    if (h1) {
                        h1.remove();
                    }
                    for (let user of users) {
                        let li = document.createElement('li');
                        li.append(get_chat_link(user.name, user.username));
                        ul_content__searched_users.append(li);
                    }
                }
            });
        }
    })
});

function get_chat_link(name, username) {
    let link = document.createElement('a');
    link.href = `/chats/begin/${username}`;
    let div_user_chat_link = document.createElement('div');
    let div_name = document.createElement('div');
    let div_username = document.createElement('div');
    div_user_chat_link.classList.add('content__user_chat_link');
    div_name.classList.add('user_chat_link_name');
    div_name.innerText = name;
    div_username.classList.add('user_chat_link_username');
    div_username.innerText = username;
    div_user_chat_link.append(div_name, div_username);
    link.append(div_user_chat_link);
    return link
}