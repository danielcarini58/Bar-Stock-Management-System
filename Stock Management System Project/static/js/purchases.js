// Temporary purchase data to be replaced with backend when ready
/*let purchases = [
    { id: "001", supplier: "Wine World", date: "21-01-2026", status: "Pending" },
    { id: "002", supplier: "LWC Drinks", date: "17-01-2026", status: "Ordered" },
    { id: "003", supplier: "Speciality Drinks", date: "12-01-2026", status: "Ordered" },
    { id: "004", supplier: "Brakes Foodservice", date: "01-01-2026", status: "Delivered" },
    { id: "005", supplier: "Matthew Clark", date: "25-12-2025", status: "Delivered" },
    { id: "006", supplier: "Primo Drinks", date: "15-12-2025", status: "Delivered" }

];*/
let purchaseItems = [];

const role = localStorage.getItem("role");
if (role !== "manager" && role !== "supplier" && role !== "inventory") {
    alert("Access Denied.");
    window.location.href = "/dashboard";
}

function providePurchases() {
    fetch("/get_purchases")
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById("purchasesTable");
            tableBody.innerHTML = "";
            data.forEach(p => {
                const tr = document.createElement("tr");
                tr.className = getStatusClass(p.status);

                tr.innerHTML = `<td>${p.order_id}</td><td>${p.supplier}</td><td>${p.description}</td><td>${p.purchase_date}</td><td>${p.status}</td>
                <td>${getTrackingButtons(p.order_id, p.status)}</td>`;
                tableBody.appendChild(tr);
            });
        })
        .catch(error => console.error("Error fetching purchases:", error));
}
function getTrackingButtons(orderId, status) {
    if (status === "Pending") {
        return `<button class="btn btn-warning btn-sm" onclick="updateStatus(${orderId}, 'Ordered')">Mark Ordered</button>`;
    }
    if (status === "Ordered") {
        return `<button class="btn btn-success btn-sm" onclick="updateStatus(${orderId}, 'Delivered')">Mark Delivered</button>`;
    }
    return `<span class ="text-muted">Complete</span>`;
}

function updateStatus(orderId, newStatus) {
    fetch("/update_purchase_status/" + orderId, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(() => providePurchases());
   
}

function getStatusClass(status) {
    if (status === "Pending") return "bg-secondary";
    if (status === "Ordered") return "bg-warning";
    if (status === "Delivered") return "bg-success";

}

function addItemToOrder(){
    const itemSelect = document.getElementById("itemSelectModal");
    const quantityInput = document.getElementById("itemQuantityModal");
    const itemId = itemSelect.value;
    const itemName = itemSelect.options[itemSelect.selectedIndex].text;
    const quantity = parseInt(quantityInput.value);
    if (!itemId || quantity <= 0) {
        alert("Please select an item and enter a valid quantity.");
        return;
    }
    purchaseItems.push({ item_id: itemId, item_name: itemName, quantity: quantity });

    updateItemLists();
    quantityInput.value = "";
}
function updateDescription() {
    const descriptionInput = document.getElementById("description");

    const text = purchaseItems.map(i => `${i.item_name} (x${i.quantity})`).join(", ");
    descriptionInput.value = text;
}

function updateItemLists() {
    const modalList = document.getElementById("modalItemsList");
    const mainList = document.getElementById("orderItemsList");
    modalList.innerHTML = "";
    mainList.innerHTML = "";
    purchaseItems.forEach(i => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        
        li.innerHTML = `${i.item_name} - Quantity: ${i.quantity} <button class="btn btn-sm btn-danger float-end" onclick="removeItemFromOrder(${i.item_id})">Remove</button>`;
        modalList.appendChild(li);
        mainList.appendChild(li.cloneNode(true));
    });
    updateDescription();
}

function removeItemFromOrder(itemId) {
    purchaseItems = purchaseItems.filter(i => String(i.item_id) !== String(itemId));
    updateItemLists();
}

function loadItemsForModal() {
    fetch("/get_items")
        .then(response => response.json())
        .then(data => {
           const dropdown = document.getElementById("itemSelectModal");

            data.forEach(i => {
                const option =document.createElement("option");
                option.value = i.id;
                option.textContent = i.name;
                dropdown.appendChild(option);
            });
        });
    }
    document.addEventListener("DOMContentLoaded", () => {
        loadItemsForModal();
    });

document.getElementById("addPurchaseForm").addEventListener("submit", function (e) {
    e.preventDefault();
    
    const orderId = document.getElementById("orderId").value;
    const supplier = document.getElementById("supplier").value;
    const description = document.getElementById("description").value;
    const date = document.getElementById("purchase_date").value;
    const status = "Pending";

    

    fetch("/add_purchase", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ order_id: orderId, supplier: supplier, description: description, purchase_date: date, status: status, items: purchaseItems })

    })
    .then(() => {
        providePurchases();
        document.getElementById("addPurchaseForm").reset();
    });
});
document.addEventListener("DOMContentLoaded", providePurchases);