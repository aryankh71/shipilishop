document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =========================================
           Profile Tabs
        ========================================= */

        const tabs =
            document.querySelectorAll(
                ".profile-tab"
            );


        const sections =
            document.querySelectorAll(
                ".profile-section"
            );


        tabs.forEach(
            function (tab) {

                tab.addEventListener(
                    "click",
                    function () {


                        const targetId =
                            this.dataset.target;


                        if (!targetId) {
                            return;
                        }


                        /*
                         * Remove active
                         * from all tabs
                         */

                        tabs.forEach(
                            function (item) {

                                item.classList.remove(
                                    "active"
                                );

                            }
                        );


                        /*
                         * Hide all sections
                         */

                        sections.forEach(
                            function (section) {

                                section.classList.remove(
                                    "active"
                                );

                            }
                        );


                        /*
                         * Activate selected tab
                         */

                        this.classList.add(
                            "active"
                        );


                        /*
                         * Activate selected section
                         */

                        const targetSection =
                            document.getElementById(
                                targetId
                            );


                        if (targetSection) {

                            targetSection.classList.add(
                                "active"
                            );

                        }


                        /*
                         * Keep selected tab
                         * in URL hash
                         */

                        if (
                            window.history &&
                            window.history.replaceState
                        ) {

                            window.history.replaceState(
                                null,
                                "",
                                "#" + targetId
                            );

                        }

                    }
                );

            }
        );



        /* =========================================
           Open Tab From URL Hash
        ========================================= */

        function activateTabFromHash() {


            const hash =
                window.location.hash;


            if (!hash) {
                return;
            }


            const targetId =
                hash.substring(1);


            const targetTab =
                document.querySelector(
                    '.profile-tab[data-target="' +
                    targetId +
                    '"]'
                );


            if (targetTab) {

                targetTab.click();

            }

        }


        activateTabFromHash();



        /* =========================================
           Auto Remove Messages
        ========================================= */

        const messages =
            document.querySelectorAll(
                ".message"
            );


        messages.forEach(
            function (message) {

                setTimeout(
                    function () {

                        message.style.transition =
                            "opacity 0.3s ease, transform 0.3s ease";

                        message.style.opacity =
                            "0";

                        message.style.transform =
                            "translateY(-5px)";


                        setTimeout(
                            function () {

                                message.remove();

                            },
                            300
                        );

                    },
                    4000
                );

            }
        );



        /* =========================================
           Address Edit
        ========================================= */

        const editAddress =
            new URLSearchParams(
                window.location.search
            ).get(
                "edit_address"
            );


        if (editAddress) {

            const addressTab =
                document.querySelector(
                    '.profile-tab[data-target="address-section"]'
                );


            if (addressTab) {

                addressTab.click();

            }

        }



        /* =========================================
           Confirm Logout
        ========================================= */

        const logoutButton =
            document.querySelector(
                ".logout-button"
            );


        if (logoutButton) {

            logoutButton.addEventListener(
                "click",
                function (event) {


                    const confirmed =
                        window.confirm(
                            "آیا مطمئن هستید که می‌خواهید از حساب کاربری خارج شوید؟"
                        );


                    if (!confirmed) {

                        event.preventDefault();

                    }

                }
            );

        }



        /* =========================================
           Prevent Double Submit
        ========================================= */

        const forms =
            document.querySelectorAll(
                ".profile-form"
            );


        forms.forEach(
            function (form) {

                form.addEventListener(
                    "submit",
                    function () {


                        const submitButton =
                            form.querySelector(
                                'button[type="submit"]'
                            );


                        if (!submitButton) {
                            return;
                        }


                        /*
                         * Give visual feedback
                         */

                        submitButton.disabled =
                            true;


                        submitButton.dataset.originalText =
                            submitButton.innerHTML;


                        submitButton.innerHTML =
                            "در حال ذخیره...";


                        /*
                         * In case browser does not
                         * navigate because of validation,
                         * restore button shortly.
                         */

                        setTimeout(
                            function () {

                                if (
                                    submitButton.disabled
                                ) {

                                    submitButton.disabled =
                                        false;

                                    submitButton.innerHTML =
                                        submitButton.dataset.originalText;

                                }

                            },
                            5000
                        );

                    }
                );

            }
        );


    }
);