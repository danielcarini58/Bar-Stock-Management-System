//temporary sales data to be replaced with backend when ready
/*let sales = [
    { item: "Beer Lager", quantity: 2, date: "22-01-2026", cost: "£10" },
    { item: "Red Wine", quantity: 1, date: "22-01-2026", cost: "£8" },
    { item: "Lemonade", quantity: 3, date: "22-01-2026", cost: "£9" },
    { item: "Apple Juice", quantity: 1, date: "21-01-2026", cost: "£2" },
    { item: "Beer Lager", quantity: 4, date: "21-01-2026", cost: "£20" },
    { item: "White Wine", quantity: 2, date: "21-01-2026", cost: "£16" },
    { item: "Beer Lager", quantity: 1, date: "21-01-2026", cost: "£5" },
    { item: "Whiskey", quantity: 1, date: "21-01-2026", cost: "£8.50" },
    { item: "Coke", quantity: 2, date: "19-01-2026", cost: "£6" },
    { item: "Diet Coke", quantity: 1, date: "19-01-2026", cost: "£3" }

]; */

const role = localStorage.getItem("role");
if (role !== "manager" && role !== "bartender" && role !== "inventory"){
    alert("Access Denied.");
    window.location.href = "/dashboard";
}

function provideSales() {
    fetch("/get_sales")
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const tableBody = document.getElementById("salesTable");
            tableBody.innerHTML = "";
            data.forEach(s => {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${s.name}</td><td>${s.quantity}</td><td>${s.sale_date}</td><td>£${s.cost}</td>`;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error("Error fetching sales:", error));


}
let itemsData=[];

function loadItems(){
    fetch("/get_items")
        .then(response => response.json())
        .then(data => {
            itemsData = data;
            const select = document.getElementById("itemSelect");
            select.innerHTML = '<option value="">Select Item</option>';

            data.forEach(i => {
                const option = document.createElement("option");
                option.value = i.id;
                option.textContent = `${i.name} (Stock: ${i.stock})`;
                select.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching items:", error));
}

function updateCost(){
    const itemId = document.getElementById("itemSelect").value;
    const quantity = parseInt(document.getElementById("quantity").value) || 0;
    const selectedItem = itemsData.find(i=> i.id == itemId);

    if (selectedItem){
        const total = selectedItem.price * quantity;
        document.getElementById("calculatedCostDisplay").textContent= "£" + total.toFixed(2);
    } else{
        document.getElementById("calculatedCostDisplay").textContent= "£0.00";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    provideSales();
    loadItems();
    document.getElementById("itemSelect").addEventListener("change", updateCost);
    document.getElementById("quantity").addEventListener("input", updateCost);

    document.getElementById("addSaleForm").addEventListener("submit", function (e) {
        e.preventDefault();
    
        const itemId = document.getElementById("itemSelect").value;
        if (!itemId){
            alert("Please select an item.");
            return;
        }
        const quantity = parseInt(document.getElementById("quantity").value);
        if (quantity <= 0) {
            alert("Please enter a quantity greater than 0.");
            return;
        }
        const date = document.getElementById("sale_date").value;


        fetch("/add_sale", {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
        },
            body: JSON.stringify({ 
                item_id: itemId, quantity: quantity, sale_date: date})

        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            provideSales();
            document.getElementById("addSaleForm").reset();
        })
        .catch(error => console.error("Error adding sale:", error));
    });
        
});