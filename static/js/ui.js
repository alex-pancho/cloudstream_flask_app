export function showStatus(message, type) {
    const status = document.getElementById("status");
    status.innerText = message;
    status.className = type;
}

export function renderPlugins(plugins) {
    const container = document.getElementById("plugins");
    container.innerHTML = "";

    plugins.forEach(plugin => {
        const div = document.createElement("div");
        div.className = "plugin";
        div.innerText = plugin.name;
        container.appendChild(div);
    });
}