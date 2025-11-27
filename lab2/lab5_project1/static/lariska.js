/**
 * lariska.js is a micro-framework designed for rapid development of socket-based applications.
 * It features routing, templating, and state management, along with configurable payload options
 * for outgoing requests, streamlining the development of real-time, interactive applications.
 */

/**
 * Конструктор фреймворка Lariska
 * @param {Object} store - Объект для хранения состояния приложения
 * @param {string} container - CSS-селектор контейнера для отображения приложения
 * @param {Object} pages - Объект с шаблонами страниц приложения
 * @param {string} url - URL-адрес сервера для подключения по веб-сокету
 */
function Lariska({store, container, pages, url}) {

  // Проверяем наличие необходимых библиотек
  if (!window.Handlebars) { throw new Error('Handlebars should be loaded to document'); }
  if (!window.io) { throw new Error('io from socketio should be loaded to document'); }

  this.store = store;                // Объект для хранения состояния приложения
  this.container = container;        // CSS-селектор контейнера для отображения приложения
  this.pages = pages;                // Объект с шаблонами страниц приложения
  this.handlers = {};                // Объект для хранения обработчиков событий
  this.url = url;                    // URL-адрес сервера для подключения по веб-сокету
  this.socket = io.connect(this.url, {transports: ['websocket', 'polling']});  // Подключение к серверу

  /**
   * Метод для отображения шаблона в указанном контейнере
   * @param {string} template - CSS-селектор шаблона
   * @param {string} container - CSS-селектор контейнера для отображения (необязательный)
   */
  this.render = function(template, container=null) {

          data = this.store;
          if (!container) {container = this.container}

          console.log(`Rendering template ${template}  to ${container}`)

          try {
            const templateElement = document.querySelector(template);

            if (!templateElement) {
              throw new Error(`Template element ${template} not found`);
            }


            const outputElement = document.querySelector(container);

            if (!outputElement) {
              throw new Error('No element to put page into ');
            }

            var templateText = templateElement.innerHTML;
            var template = Handlebars.compile(templateText);
            var renderedHTML = template(data);

            outputElement.innerHTML = renderedHTML;

          } catch (error) {
            console.error(error);
          }
     }


  /**
   * Метод для перехода на указанную страницу приложения
   * @param {string} state - Имя страницы для перехода
   */
  this.go = function (state) {

    if (this.pages[state]) {
      this.render("#"+state, this.container, this.store);
    } else {
      console.error(`State ${state} not found`);
    }
    this.state = state;
  };


  this.payload = [];  // Массив для хранения ключей полезной нагрузки
  
  /**
   * Метод для добавления ключа в полезную нагрузку
   * @param {string} key - Ключ для добавления
   */
  this.addPayload = function(key){
     if (!this.store.hasOwnProperty(key)) {
        throw new Error(`Payload error: ${key} not in store`);
     } else {
        this.payload.push(key);
     }
  }

  /**
   * Метод для отправки события на сервер
   * @param {string} event - Имя события
   * @param {Object} data - Данные для отправки
   */
   this.emit = function(event, data={}){
     this.payload.forEach(key => data[key] = key in data ? data[key] : store[key]);
     this.socket.emit(event, data);
     console.log(`Socket event ${event} emitted`);
   }

   /**
    * Метод для добавления обработчика события
    * @param {string} name - Имя обработчика
    * @param {Function} func - Функция-обработчик
    */
   this.addHandler = function(name, func) {
       this.handlers[name] = func;
       console.log(`Handler ${name} added`);
   }

   /**
    * Метод для запуска обработчика события
    * @param {string} name - Имя обработчика
    * @param {*} data - Данные для передачи в обработчик
    */
   this.run = function(name, data) {

       if (typeof this.handlers[name] !== 'function') {
          throw new Error(`Handler with name ${name} doesn't exist.`);
      }

       console.log(`Handler ${name} running`);
       func = this.handlers[name](data);
   }

   /**
    * Метод для подписки на событие с сервера
    * @param {string} event - Имя события
    * @param {string} frame - CSS-селектор шаблона для отображения (необязательный)
    * @param {Function} callback - Функция-обработчик полученных данных (необязательный)
    * @param {string} container - CSS-селектор контейнера для отображения (необязательный)
    */
   this.on = function(event, frame=null, callback=null, container=null){


      this.socket.on(event, (data) => {

        console.log(`Socket event ${event} received`);
        console.log(data);

         if (callback) { callback(data); }
         if (frame) {
             this.render(frame, container);
         }
      });
   }
}
