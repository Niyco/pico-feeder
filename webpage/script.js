index = 0;
index_element = document.getElementById('index');
value_element = document.getElementById('value');
index_unformatted = index_element.innerHTML;
value_unformatted = value_element.innerHTML;

function update() {
    index += 1;
    index_element.innerHTML = index_unformatted.replace('{}', index)

    fetch('/random', {method: 'POST'})
    .then((response) => response.json())
    .then((value) => {
        value_element.innerHTML = value_unformatted.replace('{}', value)
    });
}
update()
setInterval(update, 2500);