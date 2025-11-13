document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("job-search-input");
    const box = document.getElementById("suggestions-box");

    input.addEventListener("keyup", function () {
        const term = this.value;

        if (term.length < 3) {
            box.style.display = "none";
            return;
        }

        fetch(`/jobs/suggestions/?term=${term}`)
            .then(response => response.json())
            .then(data => {
                box.innerHTML = "";

                data.forEach(title => {
                    const item = document.createElement("div");
                    item.classList.add("suggestion-item");
                    item.textContent = title;

                    item.onclick = () => {
                        input.value = title;
                        box.style.display = "none";
                    };

                    box.appendChild(item);
                });

                box.style.display = data.length ? "block" : "none";
            });
    });
});