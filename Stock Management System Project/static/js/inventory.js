// temporary inventory data, to be replaced when backend is ready
/* let inventory = [
    { item: "white wine", stock: 17, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "red wine", stock: 15, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "rose wine", stock: 9, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "beer Lager", stock: 80, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "non-alcoholic beer", stock: 20, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "cider", stock: 3, status: "Critical", lastRestock: "10-01-2026" },
    { item: "beer Ipa", stock: 100, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "vodka", stock: 7, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "gin", stock: 10, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "white rum", stock: 6, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "dark rum", stock: 9, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "tequila", stock: 7, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "whiskey", stock: 3, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "coke", stock: 50, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "diet coke", stock: 40, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "lemonade", stock: 30, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "soda water", stock: 20, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "tonic water", stock: 18, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "still water", stock: 100, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "sparkling water", stock: 75, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "apple juice", stock: 8, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "orange juice", stock: 22, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "cranberry juice", stock: 14, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "lychee juice", stock: 12, status: "In Stock", lastRestock: "10-01-2026" },
    { item: "elderflower cordial", stock: 8, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "vermouth", stock: 2, status: "Critical", lastRestock: "10-01-2026" },
    { item: "cinnamon syrup", stock: 5, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "simple syrup", stock: 5, status: "Low Stock", lastRestock: "10-01-2026" },
    { item: "grenadine", stock: 2, status: "Critical", lastRestock: "10-01-2026" }

]; */
let selectedItemId= null;
let selectedItemName="";

const role = localStorage.getItem("role");
if (role !== "manager" && role !== "inventory"){
    alert("Access Denied.");
    window.location.href = "/dashboard";
}

function provideInventory() {
    fetch("/get_items")
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("inventoryTable");
            tableBody.innerHTML = "";
            data.forEach((i, index) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${i.name}</td><td>${i.stock}</td><td>${i.price}</td><td>${i.Status}</td><td>${i.LastRestock}</td>
                <td>
                <button class="btn btn-danger btn-sm" onclick="removeItem(${i.id})">Remove</button>
                <button class="btn btn-warning btn-sm ms-2" onclick="openWasteModal(${i.id}, '${i.name}')">Waste</button>
                </td>`;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error("Error fetching inventory:", error));
}
function getStatus(item) {
    if (item.stock <= 5) return "Critical";
    else if (item.stock <= 10) return "Low Stock";
    else return "In Stock";
}
function removeItem(id) {
    fetch("/delete_item/" + id, {
        method: "DELETE"
    })
        .then(response => response.json())
        .then(() => {
            provideInventory();
        })
        .catch(error => console.error("Error deleting item:", error));
}
function openWasteModal(itemId, itemName){
    selectedItemId = itemId;
    selectedItemName = itemName;

    document.getElementById("wasteModal").style.display="block";
    document.getElementById("wasteTitle").textContent = `Mark Waste: ${itemName}`;
}
function closeWasteModal(){
    document.getElementById("wasteModal").style.display = "none"
}

function submitWaste(){
    fetch("/add_waste", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            item_id: selectedItemId,
            quantity: document.getElementById("wasteQuantity").value,
            cost: document.getElementById("wasteCost").value,
            reason: document.getElementById("wasteReason").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        closeWasteModal();
        updateDashboard();
    })
    .catch(error => console.error("Waste error:", error))
}
document.getElementById("addItemForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const item = document.getElementById("newItemName").value;
    const stock = parseInt(document.getElementById("newItemStock").value);
    const price = parseInt(document.getElementById("newItemPrice").value);
    const status = document.getElementById("newItemStatus").value;
    const lastRestock = document.getElementById("newLastStock").value;

    fetch("/add_item", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name: item, stock: stock, price: price, Status: status, LastRestock: lastRestock })
    })
        .then(response => response.json())
        .then(() => {
            provideInventory();
            document.getElementById("addItemForm").reset();
        })
        .catch(error => console.error("Error adding item:", error));
});
document.addEventListener("DOMContentLoaded", provideInventory);