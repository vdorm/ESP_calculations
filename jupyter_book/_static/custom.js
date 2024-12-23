document.addEventListener("DOMContentLoaded", function () {
    // Заменить 'Fig.' на 'Рис.' в подписях
    let captions = document.querySelectorAll('figcaption .caption-number');
    captions.forEach(function(caption) {
        caption.innerText = caption.innerText.replace('Fig.', 'Рис.');
    });

    // Заменить 'Fig.' на 'Рис.' в тексте ссылок
    let links = document.querySelectorAll('a.reference.internal');
    links.forEach(function(link) {
        link.innerHTML = link.innerHTML.replace('Fig.', 'Рис.');
    });
});

document.addEventListener('DOMContentLoaded', function() {
    let section = document.getElementById("section1"); // Указываем нужный раздел
    let headers = section.querySelectorAll("h1, h2, h3"); // Выбираем заголовки всех уровней внутри раздела

    let counter = {
        h1: 1,
        h2: 1,
        h3: 1
    };

    headers.forEach(function(header) {
        let tagName = header.tagName.toLowerCase();

        // Добавляем нумерацию только в пределах одного раздела
        if (tagName === "h1") {
            header.innerHTML = `${counter.h1++}. ${header.innerHTML}`;
        } else if (tagName === "h2") {
            header.innerHTML = `${counter.h1 - 1}.${counter.h2++} ${header.innerHTML}`;
        } else if (tagName === "h3") {
            header.innerHTML = `${counter.h1 - 1}.${counter.h2 - 1}.${counter.h3++} ${header.innerHTML}`;
        }
    });
});
