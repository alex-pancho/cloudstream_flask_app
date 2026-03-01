export async function addRepository(url) {
    const response = await fetch("/api/repo/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Failed to add repository");
    }

    return data;
}

export async function fetchPlugins() {
    const response = await fetch("/api/plugins");
    return await response.json();
}