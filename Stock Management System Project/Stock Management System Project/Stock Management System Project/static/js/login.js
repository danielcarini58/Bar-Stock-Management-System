document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: email, password: password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                localStorage.setItem("role", data.role);

                if (data.role === "manager") {
                    window.location.href = "/dashboard";
                }
                else if (data.role === "bartender") {
                    window.location.href = "/sales";
                }
                else if (data.role === "inventory") {
                    window.location.href = "/inventory";
                }
                else if (data.role === "supplier") {
                    window.location.href = "/purchases";
                }
                else {
                    alert("Invalid email or password. Please try again.");
                }
            }
        });
});