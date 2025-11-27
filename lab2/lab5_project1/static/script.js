/*
Скрипт для управления логикой клиентской части игры в загадки.
Содержит обработчики событий, взаимодействующие с сервером через веб-сокеты.
*/

// Объект для хранения состояния приложения
var store = {
    riddle: null,  // Текущая загадка
    score: 0,      // Счет игрока
};

// Определение страниц приложения
app_pages = {
    standby: {},      // Страница ожидания начала игры
    showriddle: {},   // Страница показа загадки
    showresult: {},   // Страница показа результата ответа
    disconnected: {}  // Страница при отключении
}

// Ждем загрузки DOM перед инициализацией приложения
document.addEventListener('DOMContentLoaded', function () {

    // Создаем экземпляр приложения Lariska
    app = new Lariska({
        store: store,           // Состояние приложения
        container: "#app",      // Контейнер для отображения приложения
        pages: app_pages,       // Страницы приложения
        url: window.location.host  // URL сервера
    });

    // Добавляем обработчик события "next" для запроса следующей загадки
    app.addHandler("next", () => {
        app.emit("next")
    })

    // Добавляем обработчик события "answer" для отправки ответа на загадку
    app.addHandler("answer", () => {
        // Получаем текст ответа из текстового поля
        user_answer = document.querySelector("textarea#answer").value
        // Отправляем ответ на сервер
        app.emit("answer", {text: user_answer})
    })

    // Обработчик события получения загадки с сервера
    app.on("riddle", "#showriddle", (data) => {
        console.log(data)
        app.store.riddle = data  // Сохраняем загадку в состоянии приложения
    })

    // Обработчик события получения результата ответа сервера
    app.on("result", "#showanswer", (data) => {
        console.log(data)
        app.store.riddle = data.riddle  // Сохраняем загадку в состоянии приложения
    })

    // Обработчик события получения обновления счета с сервера
    app.on("score", null, (data) => {
        console.log(data)
        app.store.score = data.value  // Обновляем счет в состоянии приложения
    })

    // Обработчик события завершения игры
    app.on("over", "#over", (data) => {
        console.log(data)
    })

    // Переходим на страницу ожидания
    app.go("standby");
})
