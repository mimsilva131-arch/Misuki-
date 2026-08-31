
/* =========================================================
   MISUKI — STAR SYSTEM
   NORMAL STARS + SHOOTING STARS
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       INITIALIZATION
       ===================================================== */

    function initMisukiStars() {

        /*
         * Procura o container.
         *
         * Se não existir, cria automaticamente.
         * Isto permite colocar o script no <head>
         * ou antes do </body>.
         */

        let container =
            document.getElementById("misuki-stars");


        if (!container) {

            container =
                document.createElement("div");

            container.id =
                "misuki-stars";

            document.body.appendChild(container);
        }


        /*
         * Evita inicializar duas vezes
         * na mesma página.
         */

        if (container.dataset.misukiInitialized === "true") {
            return;
        }

        container.dataset.misukiInitialized =
            "true";


        /* =================================================
           NORMAL STARS
           ================================================= */

        const STAR_COUNT = 150;


        for (
            let i = 0;
            i < STAR_COUNT;
            i++
        ) {

            const star =
                document.createElement("span");


            star.className =
                "misuki-star";


            /* ---------------------------------------------
               TAMANHO
               --------------------------------------------- */

            const size =
                Math.random() * 2.2 + 0.6;


            star.style.width =
                size + "px";

            star.style.height =
                size + "px";


            /* ---------------------------------------------
               POSIÇÃO
               --------------------------------------------- */

            star.style.left =
                Math.random() * 100 + "%";

            star.style.top =
                Math.random() * 100 + "%";


            /* ---------------------------------------------
               OPACIDADE
               --------------------------------------------- */

            star.style.setProperty(
                "--star-opacity",
                Math.random() * 0.65 + 0.25
            );


            /* ---------------------------------------------
               CINTILAÇÃO
               --------------------------------------------- */

            star.style.setProperty(
                "--blink-duration",
                Math.random() * 4 + 2 + "s"
            );


            star.style.setProperty(
                "--blink-delay",
                Math.random() * -6 + "s"
            );


            container.appendChild(star);
        }


        /* =================================================
           SHOOTING STAR
           ================================================= */

        function createShootingStar() {

            const star =
                document.createElement("span");


            star.className =
                "misuki-shooting-star";


            /* ---------------------------------------------
               ESCOLHER LADO
               --------------------------------------------- */

            const fromLeft =
                Math.random() < 0.5;


            /* ---------------------------------------------
               POSIÇÃO INICIAL
               --------------------------------------------- */

            const startX =
                fromLeft
                    ? -120
                    : window.innerWidth + 120;


            const startY =
                Math.random() *
                window.innerHeight *
                0.45;


            /* ---------------------------------------------
               DISTÂNCIA HORIZONTAL
               --------------------------------------------- */

            const distanceX =
                fromLeft

                    ? window.innerWidth *
                        (
                            0.75 +
                            Math.random() * 0.55
                        )

                    : -window.innerWidth *
                        (
                            0.75 +
                            Math.random() * 0.55
                        );


            /* ---------------------------------------------
               DISTÂNCIA VERTICAL

               A estrela continua para fora do ecrã.
               --------------------------------------------- */

            const distanceY =
                window.innerHeight *
                (
                    1.15 +
                    Math.random() * 0.45
                );


            /* ---------------------------------------------
               ÂNGULO REAL DA TRAJETÓRIA

               NÃO ALTERAR.

               Este é o ângulo do movimento.
               --------------------------------------------- */

            const angle =
                Math.atan2(
                    distanceY,
                    distanceX
                ) *
                180 /
                Math.PI;


            /* ---------------------------------------------
               TAMANHO DA ESTRELA
               --------------------------------------------- */

            const size =
                Math.random() * 2 + 1.5;


            /* ---------------------------------------------
               RASTO
               --------------------------------------------- */

            const trail =
                Math.random() * 90 + 120;


            /* ---------------------------------------------
               LARGURA DO RASTO
               --------------------------------------------- */

            const trailWidth =
                Math.random() * 1.2 + 1.5;


            /* ---------------------------------------------
               VELOCIDADE
               --------------------------------------------- */

            const duration =
                Math.random() * 0.8 + 1.6;


            /* ---------------------------------------------
               POSIÇÃO
               --------------------------------------------- */

            star.style.left =
                startX + "px";

            star.style.top =
                startY + "px";


            /* ---------------------------------------------
               MOVIMENTO
               --------------------------------------------- */

            star.style.setProperty(
                "--distance-x",
                distanceX + "px"
            );

            star.style.setProperty(
                "--distance-y",
                distanceY + "px"
            );


            /* ---------------------------------------------
               ÂNGULO
               --------------------------------------------- */

            star.style.setProperty(
                "--meteor-angle",
                angle + "deg"
            );


            /* ---------------------------------------------
               TAMANHO
               --------------------------------------------- */

            star.style.setProperty(
                "--meteor-size",
                size + "px"
            );


            /* ---------------------------------------------
               RASTO
               --------------------------------------------- */

            star.style.setProperty(
                "--trail-length",
                trail + "px"
            );

            star.style.setProperty(
                "--trail-width",
                trailWidth + "px"
            );


            /* ---------------------------------------------
               DURAÇÃO
               --------------------------------------------- */

            star.style.setProperty(
                "--shoot-duration",
                duration + "s"
            );


            /* ---------------------------------------------
               ADICIONAR
               --------------------------------------------- */

            container.appendChild(star);


            /* ---------------------------------------------
               REMOVER DEPOIS DA ANIMAÇÃO
               --------------------------------------------- */

            setTimeout(
                function () {

                    if (star.parentNode) {
                        star.remove();
                    }

                },
                (duration + 0.3) * 1000
            );
        }


        /* =================================================
           SPAWN
           ================================================= */

        function scheduleShootingStar() {

            const delay =
                Math.random() * 7000 + 5000;


            setTimeout(
                function () {

                    createShootingStar();

                    scheduleShootingStar();

                },
                delay
            );
        }


        /* =================================================
           START
           ================================================= */

        scheduleShootingStar();
    }


    /* =====================================================
       DOM READY
       ===================================================== */

    /*
     * Se o script estiver no <head>, o body ainda pode
     * não existir.
     *
     * Neste caso esperamos pelo DOM.
     */

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initMisukiStars
        );

    } else {

        initMisukiStars();
    }


})();

