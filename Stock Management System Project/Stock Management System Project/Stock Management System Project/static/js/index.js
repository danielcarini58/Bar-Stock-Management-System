// Temporary data to be replaced with backend when ready


function updateDashboard() {
    fetch("/dashboard_data")
        .then(response => response.json())
        .then(data => {
    document.getElementById("totalItems").textContent = data.total_items;
    document.getElementById("lowStock").textContent = data.low_stock;
    document.getElementById("inventoryValue").textContent = data.inventory_value;
    document.getElementById("lowStockCount").textContent = data.low_stock;

    document.getElementById("todaySales").textContent = data.today_sales;
    document.getElementById("todayRevenue").textContent = data.today_revenue;
    document.getElementById("weekRevenue").textContent = data.week_revenue;
    document.getElementById("topItem").textContent = data.top_item;
    document.getElementById("worstItem").textContent = data.worst_item;

    document.getElementById("pendingOrdersText").textContent = data.pending_orders;
    document.getElementById("weeklyOrders").textContent = data.weekly_orders;
    document.getElementById("totalCost").textContent = data.total_cost;

    document.getElementById("wasteToday").textContent = data.waste_today;
    document.getElementById("costToday").textContent = data.cost_today;

    const lowStockList = document.getElementById("lowStockList");
    lowStockList.innerHTML = ""; // Clear existing list
    data.low_stock_items.forEach(item => {
        const listItem = document.createElement("li");
        listItem.textContent = `${item[0]} (Stock: ${item[1]})`;
    

        if (item[1] <=3){
            listItem.style.fontWeight = "bold";
            listItem.style.color = "red";
            listItem.textContent += " ⚠ Reorder Soon!"
        }
        lowStockList.appendChild(listItem);
    });
    
    const wasteList = document.getElementById("wasteList");
    wasteList.innerHTML = ""; // Clear existing list
    data.waste_today_items.forEach(item => {
        const listItem = document.createElement("li");
        listItem.textContent = `${item[0]} (Quantity: ${item[1]}, Cost: £${item[2]}) - Reason: ${item[3]}`;

        if (item[2] > 10){
            listItem.style.fontWeight = "bold";
            listItem.style.color = "red";
            listItem.textContent += " ⚠ High Cost!"
        }
        wasteList.appendChild(listItem);
    });

})
.catch(error => console.error("Error fetching dashboard data:", error));
}

function provideSalesChart() {
    fetch("/sales_by_item")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            
            const ctx = document.getElementById("salesChart").getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data:{
                    labels: data.labels,
                    datasets: [{
                        label: "Sales by Item",
                        data: data.values,
                        backgroundColor: "rgba(54, 162, 235, 0.6)"
                    }]
                },
                options: {
                    responsive: true
                }
            });
        });
    
}

    
document.addEventListener("DOMContentLoaded", () => {
    updateDashboard();
    provideSalesChart();
});