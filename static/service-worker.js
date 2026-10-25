self.addEventListener("push", function (event) {
    let data = {};

    try {
        data = event.data ? event.data.json() : {};
    } catch (error) {
        data = {
            title: "Misuki",
            body: event.data ? event.data.text() : "You have a new notification."
        };
    }

    const title = data.title || "Misuki";
    const options = {
        body: data.body || "",
        icon: data.icon || "/assets/images/favicon.png?v=3",
        badge: data.badge || "/assets/images/favicon.png?v=3",
        tag: data.tag || "misuki-notification",
        renotify: true,
        data: {
            url: data.url || "/advertise/status"
        }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener("notificationclick", function (event) {
    event.notification.close();

    const targetUrl = event.notification.data && event.notification.data.url
        ? event.notification.data.url
        : "/advertise/status";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (clientList) {
            for (const client of clientList) {
                if ("focus" in client) {
                    client.navigate(targetUrl);
                    return client.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
