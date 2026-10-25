(function () {
    "use strict";

    const button = document.getElementById("notificationButton");

    if (!button) {
        return;
    }

    function setState(enabled) {
        button.classList.toggle("is-enabled", enabled);
        button.setAttribute("aria-pressed", enabled ? "true" : "false");
        button.setAttribute("data-notifications-enabled", enabled ? "true" : "false");
    }

    function getText(key) {
        const element = document.querySelector('[data-i18n="notifications.' + key + '"]');
        return element ? element.textContent.trim() : key;
    }

    function showMessage(key) {
        const message = getText(key);
        if (message) {
            button.title = message;
            button.setAttribute("aria-label", message);
        }
    }

    async function getPublicKey() {
        const response = await fetch("/api/notifications/public-key", {
            credentials: "same-origin",
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Notification service is not configured.");
        }

        const data = await response.json();
        if (!data.public_key) {
            throw new Error("Missing VAPID public key.");
        }

        return data.public_key;
    }

    function urlBase64ToUint8Array(base64String) {
        const padding = "=".repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
        const rawData = window.atob(base64);
        return Uint8Array.from([...rawData].map(function (char) {
            return char.charCodeAt(0);
        }));
    }

    async function subscribe() {
        if (!("Notification" in window) || !("serviceWorker" in navigator) || !("PushManager" in window)) {
            showMessage("unsupported");
            return;
        }

        if (Notification.permission === "denied") {
            showMessage("denied");
            return;
        }

        const permission = await Notification.requestPermission();

        if (permission !== "granted") {
            showMessage("denied");
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register("/service-worker.js", { scope: "/" });
            const publicKey = await getPublicKey();
            let subscription = await registration.pushManager.getSubscription();

            if (!subscription) {
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicKey)
                });
            }

            const response = await fetch("/api/notifications/subscribe", {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(subscription.toJSON())
            });

            if (!response.ok) {
                throw new Error("Could not save notification subscription.");
            }

            setState(true);
            showMessage("enabled");
        } catch (error) {
            console.error("Misuki notifications:", error);
            showMessage("error");
        }
    }

    function syncLabel() {
        if (button.classList.contains("is-enabled")) {
            showMessage("enabled");
        } else {
            showMessage("enable");
        }
    }

    async function initialize() {
        if (!("Notification" in window) || !("serviceWorker" in navigator) || !("PushManager" in window)) {
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register("/service-worker.js", { scope: "/" });
            const subscription = await registration.pushManager.getSubscription();
            setState(Boolean(subscription && Notification.permission === "granted"));
            syncLabel();
        } catch (error) {
            console.error("Misuki notification initialization:", error);
        }
    }

    button.addEventListener("click", subscribe);
    window.addEventListener("misuki:language-changed", syncLabel);
    initialize();
})();
