
function logout() {
    localStorage.removeItem("role");
    window.location.href = "/login";
}

document.addEventListener("DOMContentLoaded", function () {
    fetch("/sidebar")
        .then(response => response.text())
        .then(data => {
            document.getElementById("sidebarContainer").innerHTML = data;

            const currentPage = window.location.pathname.split("/").pop() || "index.html";

            document.querySelectorAll(".sidebar .nav-link").forEach(link => {
                if (link.getAttribute("href") === currentPage) {
                    link.classList.add("active");
                }
            });
        })
        .catch(error => console.error("Error loading sidebar:", error));
    });
document.addEventListener("click", function (e) {
            if (e.target && e.target.id === "sidebarToggle") {
                const sidebar = document.querySelector(".sidebar");

                if (sidebar) {
                    sidebar.classList.toggle("collapsed");
                    console.log("Sidebar toggled");
                }
            }
        });    

    