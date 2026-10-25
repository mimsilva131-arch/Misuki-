(function () {
    "use strict";

    const wrapper = document.getElementById("notificationWrapper");
    const button = document.getElementById("notificationButton");
    const dropdown = document.getElementById("notificationDropdown");
    const list = document.getElementById("notificationList");
    const enableButton = document.getElementById("notificationEnableButton");

    if (!wrapper || !button || !dropdown || !list) return;

    let notifications = [];

    function getCurrentLanguage() {
        return localStorage.getItem("misuki_language") || "en";
    }

    function getTranslation(key) {
        const parts = key.split(".");
        let value = window.MisukiTranslations;
        for (const part of parts) {
            value = value && value[part];
        }
        return typeof value === "string" ? value : key;
    }

    function formatDate(value) {
        if (!value) return "—";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        const language = getCurrentLanguage();
        return new Intl.DateTimeFormat(language === "pt" ? "pt-PT" : language, {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }).format(date);
    }

    function renderNotifications() {
        if (!notifications.length) {
            list.innerHTML = '<div class="notification-empty" data-i18n="notifications.empty">' +
                getTranslation("notifications.empty") + '</div>';
            updateDot(0);
            return;
        }

        list.innerHTML = notifications.map(function (item) {
            const title = getTranslation(item.title_key);
            let body = getTranslation(item.body_key);
            const payload = item.payload || {};
            if (payload.advertisement) {
                body = body.replace("{advertisement}", payload.advertisement);
            }

            return '<a class="notification-item ' + (item.is_read ? "" : "unread") +
                '" href="' + (item.url || "/advertise/status") +
                '" data-notification-id="' + item.id + '">' +
                '<span class="notification-item-title">' + escapeHtml(title) + '</span>' +
                '<span class="notification-item-body">' + escapeHtml(body) + '</span>' +
                '<span class="notification-item-date">' + escapeHtml(formatDate(item.created_at)) + '</span>' +
                '</a>';
        }).join("");

        updateDot(notifications.filter(function (item) { return !item.is_read; }).length);

        list.querySelectorAll(".notification-item").forEach(function (item) {
            item.addEventListener("click", function () {
                const id = item.getAttribute("data-notification-id");
                fetch("/api/notifications/read", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({id: Number(id)})
                }).catch(function () {});
            });
        });
    }

    function escapeHtml(value) {
        return String(value || "").replace(/[&<>"']/g, function (char) {
            return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char];
        });
    }

    function updateDot(unread) {
        button.classList.toggle("has-unread", unread > 0);
    }

    async function loadNotifications() {
        try {
            const response = await fetch("/api/notifications", {
                credentials: "same-origin",
                cache: "no-store"
            });
            if (!response.ok) return;
            const data = await response.json();
            notifications = Array.isArray(data.notifications) ? data.notifications : [];
            renderNotifications();
        } catch (error) {
            console.error("Misuki notifications:", error);
        }
    }

    function openDropdown() {
        wrapper.classList.add("open");
        button.setAttribute("aria-expanded", "true");
        dropdown.setAttribute("aria-hidden", "false");
        loadNotifications();
    }

    function closeDropdown() {
        wrapper.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
        dropdown.setAttribute("aria-hidden", "true");
    }

    async function enablePushNotifications() {
        if (!("Notification" in window) || !("serviceWorker" in navigator) || !("PushManager" in window)) {
            setMessage("unsupported");
            return;
        }
        if (Notification.permission === "denied") {
            setMessage("denied");
            return;
        }

        try {
            const permission = await Notification.requestPermission();
            if (permission !== "granted") {
                setMessage("denied");
                return;
            }

            const registration = await navigator.serviceWorker.register("/service-worker.js", {scope: "/"});
            const publicKeyResponse = await fetch("/api/notifications/public-key", {credentials:"same-origin", cache:"no-store"});
            if (!publicKeyResponse.ok) throw new Error("Notification service is not configured.");
            const publicKeyData = await publicKeyResponse.json();
            let subscription = await registration.pushManager.getSubscription();

            if (!subscription) {
                subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicKeyData.public_key)
                });
            }

            const response = await fetch("/api/notifications/subscribe", {
                method: "POST",
                credentials: "same-origin",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify(subscription.toJSON())
            });
            if (!response.ok) throw new Error("Could not save notification subscription.");

            setMessage("enabled");
        } catch (error) {
            console.error("Misuki notifications:", error);
            setMessage("error");
        }
    }

    function setMessage(key) {
        if (!enableButton) return;
        enableButton.textContent = getTranslation("notifications." + key);
    }

    function urlBase64ToUint8Array(base64String) {
        const padding = "=".repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
        const rawData = window.atob(base64);
        return Uint8Array.from([...rawData].map(function (char) { return char.charCodeAt(0); }));
    }

    button.addEventListener("click", function (event) {
        event.stopPropagation();
        if (wrapper.classList.contains("open")) closeDropdown();
        else openDropdown();
    });

    if (enableButton) {
        enableButton.addEventListener("click", function (event) {
            event.stopPropagation();
            enablePushNotifications();
        });
    }

    document.addEventListener("click", function (event) {
        if (!wrapper.contains(event.target)) closeDropdown();
    });

    window.addEventListener("misukiLanguageChanged", function () {
        renderNotifications();
        setMessage("enable");
    });

    loadNotifications();
})();