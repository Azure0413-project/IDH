// base.js
document.addEventListener("DOMContentLoaded", function() {
    const originalFavicon = "/static/img/kidney.svg"; // Use the static path
    const alertFavicon = "/static/img/kidney_warning.svg"; // Use the static path
    let alertInterval;

    function createFavicon(href) {
        const existingFavicon = document.getElementById("favicon");
        if (existingFavicon) {
            existingFavicon.remove();
        }
        const newFavicon = document.createElement("link");
        newFavicon.id = "favicon";
        newFavicon.rel = "icon";
        newFavicon.href = href;
        newFavicon.type = "image/x-icon";
        document.head.appendChild(newFavicon);
    }

    function startFaviconAlert() {
        if (!alertInterval) {
            alertInterval = setInterval(() => {
                const currentFavicon = document.getElementById("favicon").href;
                createFavicon(currentFavicon.includes("kidney.svg") ? alertFavicon : originalFavicon);
            }, 100); // flashing interval
        }
    }

    function stopFaviconAlert() {
        clearInterval(alertInterval);
        alertInterval = null;
        createFavicon(originalFavicon);
    }

    document.addEventListener("visibilitychange", () => {
        if (document.hidden) {
            startFaviconAlert();
        } else {
            stopFaviconAlert();
        }
    });
});
