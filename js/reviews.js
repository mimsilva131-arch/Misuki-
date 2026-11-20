/* =========================================================
   MISUKI — REVIEWS.JS
   REVIEW ACTIONS + REVIEW FORM
   ========================================================= */

(function () {
    "use strict";

    function closeAllReviewMenus() {
        document.querySelectorAll(".review-actions-menu").forEach(function (menu) {
            menu.hidden = true;
        });

        document.querySelectorAll(".review-actions-button").forEach(function (button) {
            button.setAttribute("aria-expanded", "false");
        });
    }

    function initVoteButtons() {
        document.querySelectorAll(".review-votes").forEach(function (group) {
            group.addEventListener("click", async function (event) {
                const button = event.target.closest(".review-vote");
                if (!button || button.disabled) return;

                const target = group.closest("[data-vote-type][data-vote-id]") || group;
                const voteType = target.dataset.voteType || group.dataset.voteType;
                const voteId = target.dataset.voteId || group.dataset.voteId;
                if (!voteType || !voteId) return;

                const endpoint = voteType === "reply"
                    ? "/reviews/replies/" + encodeURIComponent(voteId) + "/vote"
                    : "/reviews/" + encodeURIComponent(voteId) + "/vote";

                const requestedVote = Number(button.dataset.vote);
                const like = group.querySelector(".review-vote-like");
                const dislike = group.querySelector(".review-vote-dislike");

                // Give immediate visual feedback; the network request reconciles the counts afterwards.
                group.querySelectorAll(".review-vote").forEach(function (item) {
                    item.disabled = true;
                });
                if (like) {
                    like.classList.toggle("is-active", requestedVote === 1);
                    like.setAttribute("aria-pressed", requestedVote === 1 ? "true" : "false");
                }
                if (dislike) {
                    dislike.classList.toggle("is-active", requestedVote === -1);
                    dislike.setAttribute("aria-pressed", requestedVote === -1 ? "true" : "false");
                }

                const body = new URLSearchParams();
                body.set("vote", button.dataset.vote);

                try {
                    const response = await fetch(endpoint, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "X-Requested-With": "XMLHttpRequest"
                        },
                        body: body.toString(),
                        credentials: "same-origin"
                    });

                    if (response.status === 401) {
                        window.location.href = "/login";
                        return;
                    }

                    const data = await response.json();
                    if (!data.ok) throw new Error(data.error || "Vote failed");

                    const like = group.querySelector(".review-vote-like");
                    const dislike = group.querySelector(".review-vote-dislike");

                    if (like) {
                        like.classList.toggle("is-active", data.user_vote === 1);
                        like.setAttribute("aria-pressed", data.user_vote === 1 ? "true" : "false");
                        const count = like.querySelector(".review-vote-count");
                        if (count) count.textContent = data.likes;
                    }

                    if (dislike) {
                        dislike.classList.toggle("is-active", data.user_vote === -1);
                        dislike.setAttribute("aria-pressed", data.user_vote === -1 ? "true" : "false");
                        const count = dislike.querySelector(".review-vote-count");
                        if (count) count.textContent = data.dislikes;
                    }
                } catch (error) {
                    console.error("Misuki vote error:", error);
                } finally {
                    group.querySelectorAll(".review-vote").forEach(function (item) {
                        item.disabled = false;
                    });
                }
            });
        });
    }

    function initReviewReplies() {
        document.querySelectorAll(".review-replies").forEach(function (container) {
            const toggle = container.querySelector(".review-replies-toggle");
            const list = container.querySelector(".review-replies-list");
            const open = container.querySelector(".review-reply-open");
            const form = container.querySelector(".review-reply-form");
            const cancel = container.querySelector(".review-reply-cancel");
            if (toggle && list) {
                toggle.addEventListener("click", function () {
                    const expanded = toggle.getAttribute("aria-expanded") === "true";
                    toggle.setAttribute("aria-expanded", String(!expanded));
                    list.hidden = expanded;
                });
            }
            if (open && form) {
                open.addEventListener("click", function () {
                    open.hidden = true;
                    form.hidden = false;
                    const textarea = form.querySelector("textarea");
                    if (textarea) textarea.focus();
                });
            }
            if (cancel && form && open) {
                cancel.addEventListener("click", function () {
                    form.hidden = true;
                    open.hidden = false;
                    form.reset();
                });
            }
        });
    }

    function initReviewCarousel() {
        const carousel = document.querySelector(".home-page .review-grid");
        if (!carousel || carousel.dataset.autoReviewCarousel === "true") return;

        const cards = Array.from(carousel.querySelectorAll(".review-card"));
        if (cards.length < 2) return;

        carousel.dataset.autoReviewCarousel = "true";
        let timer = null;
        let paused = false;
        let activeIndex = 0;

        const setActive = function (index) {
            // Circular loop: after the last review, continue directly with
            // the first one instead of reversing through the previous cards.
            activeIndex = ((index % cards.length) + cards.length) % cards.length;

            cards.forEach(function (card, cardIndex) {
                card.classList.toggle("is-carousel-center", cardIndex === activeIndex);
                card.classList.toggle("is-carousel-side", cardIndex !== activeIndex);
            });
        };


        const stop = function () {
            if (timer) {
                clearInterval(timer);
                timer = null;
            }
        };

        const start = function () {
            stop();
            timer = setInterval(function () {
                if (paused) return;
                setActive(activeIndex + 1);
            }, 11000);
        };

        ["mouseenter", "focusin"].forEach(function (eventName) {
            carousel.addEventListener(eventName, function () {
                paused = true;
            }, { passive: true });
        });

        ["mouseleave", "focusout"].forEach(function (eventName) {
            carousel.addEventListener(eventName, function () {
                paused = false;
            }, { passive: true });
        });

        setActive(0);
        start();
    }

    function revealTargetReview() {
        const hash = window.location.hash || "";
        if (!hash.startsWith("#review-")) return;

        const card = document.getElementById(hash.slice(1));
        if (!card) return;

        window.requestAnimationFrame(function () {
            card.scrollIntoView({ behavior: "smooth", block: "center" });
            card.classList.add("review-target-highlight");
            window.setTimeout(function () {
                card.classList.remove("review-target-highlight");
            }, 1800);
        });
    }

    function initReviews() {
        const textarea = document.querySelector('textarea[name="review"]');
        if (textarea) {
            textarea.addEventListener("input", function () {
                if (this.value.length > this.maxLength) {
                    this.value = this.value.substring(0, this.maxLength);
                }
            });
        }

        const rating = document.querySelector('select[name="rating"]');
        if (rating) {
            rating.addEventListener("change", function () {
                this.classList.add("review-rating-selected");
            });
        }

        // Delegated handlers keep this working even if review cards are re-rendered.
        document.addEventListener("click", function (event) {
            const actionButton = event.target.closest(".review-actions-button");

            if (actionButton) {
                event.preventDefault();
                event.stopPropagation();

                const actions = actionButton.closest(".review-actions");
                const menu = actions && actions.querySelector(".review-actions-menu");

                if (!menu) return;

                const wasOpen = !menu.hidden;
                closeAllReviewMenus();

                if (!wasOpen) {
                    menu.hidden = false;
                    actionButton.setAttribute("aria-expanded", "true");
                }
                return;
            }

            const editButton = event.target.closest(".review-action-edit");
            if (editButton) {
                event.preventDefault();
                event.stopPropagation();

                const card = editButton.closest(".review-card");
                const actions = card && card.querySelector(".review-actions");
                const editForm = card && card.querySelector(".review-edit-form");
                const reviewText = card && card.querySelector(".review-text");

                if (!editForm) return;

                if (actions) {
                    const menu = actions.querySelector(".review-actions-menu");
                    const button = actions.querySelector(".review-actions-button");
                    if (menu) menu.hidden = true;
                    if (button) button.setAttribute("aria-expanded", "false");
                }

                if (reviewText) reviewText.hidden = true;
                editForm.hidden = false;

                const editTextarea = editForm.querySelector("textarea");
                if (editTextarea) {
                    editTextarea.focus();
                    editTextarea.setSelectionRange(
                        editTextarea.value.length,
                        editTextarea.value.length
                    );
                }
                return;
            }

            const cancelButton = event.target.closest(".review-edit-cancel");
            if (cancelButton) {
                event.preventDefault();

                const card = cancelButton.closest(".review-card");
                const editForm = card && card.querySelector(".review-edit-form");
                const reviewText = card && card.querySelector(".review-text");

                if (editForm) editForm.hidden = true;
                if (reviewText) reviewText.hidden = false;
                return;
            }

            if (!event.target.closest(".review-actions")) {
                closeAllReviewMenus();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeAllReviewMenus();
            }
        });

        document.querySelectorAll('form[data-single-submit="true"]').forEach(function (writeForm) {
            writeForm.addEventListener("submit", async function (event) {
                event.preventDefault();

                if (writeForm.dataset.submitting === "true") {
                    return;
                }

                writeForm.dataset.submitting = "true";

                const submitButtons = Array.from(
                    writeForm.querySelectorAll('button[type="submit"]')
                );

                submitButtons.forEach(function (submitButton) {
                    submitButton.disabled = true;
                    submitButton.dataset.originalText = submitButton.textContent;
                    submitButton.classList.add("is-submitting");
                    submitButton.style.opacity = "0.7";
                    submitButton.style.cursor = "wait";
                });

                const controller = new AbortController();
                const timeout = window.setTimeout(function () {
                    controller.abort();
                }, 15000);

                try {
                    const response = await fetch(writeForm.action || window.location.href, {
                        method: "POST",
                        body: new FormData(writeForm),
                        credentials: "same-origin",
                        redirect: "follow",
                        signal: controller.signal
                    });

                    if (!response.ok) {
                        throw new Error("Review submission returned HTTP " + response.status);
                    }

                    window.location.assign(response.url || "/reviews");
                } catch (error) {
                    console.error("Misuki review submission error:", error);

                    if (error && error.name === "AbortError") {
                        window.location.reload();
                        return;
                    }

                    writeForm.dataset.submitting = "false";

                    submitButtons.forEach(function (submitButton) {
                        submitButton.disabled = false;
                        submitButton.classList.remove("is-submitting");
                        submitButton.style.opacity = "";
                        submitButton.style.cursor = "";
                        if (submitButton.dataset.originalText) {
                            submitButton.textContent = submitButton.dataset.originalText;
                            delete submitButton.dataset.originalText;
                        }
                    });

                    let errorMessage = writeForm.querySelector(".review-submit-error");
                    if (!errorMessage) {
                        errorMessage = document.createElement("p");
                        errorMessage.className = "review-submit-error";
                        errorMessage.setAttribute("role", "alert");
                        errorMessage.style.marginTop = "12px";
                        errorMessage.style.color = "#ff9b9b";
                        writeForm.appendChild(errorMessage);
                    }

                    errorMessage.textContent = "Não foi possível enviar a avaliação. Tente novamente.";
                } finally {
                    window.clearTimeout(timeout);
                }
            });
        });

        initVoteButtons();
        initReviewReplies();
        initReviewCarousel();
        closeAllReviewMenus();
        revealTargetReview();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initReviews, { once: true });
    } else {
        initReviews();
    }
})();
