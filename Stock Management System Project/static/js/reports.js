// temporary data for reports to be replaced with backend when ready

const role = localStorage.getItem("role");
if (role !== "manager"){
    alert("Access Denied.");
    window.location.href = "/dashboard";
}

document.getElementById("reportForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const data = {
        report_type: document.getElementById("reportType").value,
        start_date: document.getElementById("startDate").value,
        end_date: document.getElementById("endDate").value  
    };

    fetch("/generate_report", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(() => loadReports());
});

function loadReports() {
    fetch("/get_reports")
        .then(response => response.json())
        .then(data => {
            const table= document.getElementById("reportsTable");
            table.innerHTML = "";
            data.forEach(r => {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${r.report_type}</td><td>${r.range}</td><td>${r.details}</td><td>${r.generated_at}</td>`;
                table.appendChild(tr);
            });
        });
}

document.addEventListener("DOMContentLoaded", loadReports);