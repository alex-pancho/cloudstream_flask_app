import { addRepository, fetchPlugins } from "./api.js";
import { showStatus, renderPlugins } from "./ui.js";

async function handleAddRepo() {
    const input = document.getElementById("repoUrl");
    const url = input.value.trim();

    if (!url) {
        showStatus("URL is required", "error");
        return;
    }

    try {
        await addRepository(url);
        showStatus("Repository added successfully", "success");
        input.value = "";
        loadPlugins();
    } catch (error) {
        showStatus(error.message, "error");
    }
}

async function loadPlugins() {
    const plugins = await fetchPlugins();
    renderPlugins(plugins);
}

function init() {
    document
        .getElementById("addRepoBtn")
        .addEventListener("click", handleAddRepo);

    loadPlugins();
}

window.addEventListener("DOMContentLoaded", init);