const body = document.querySelector("body");
const darkLight = document.querySelector("#darkLight");
const navbar = document.querySelector(".navbar");
const content = document.querySelector(".content");
darkLight.addEventListener("click", () => {
  body.classList.toggle("dark");
  navbar.classList.toggle("dark");
  content.classList.toggle("dark");
  if (body.classList.contains("dark")) {
    darkLight.classList.replace("bx-sun", "bx-moon");
  } else {
    darkLight.classList.replace("bx-moon", "bx-sun");
  }
});

const navLinks = document.querySelectorAll(".nav_link");
navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.forEach((link) => link.classList.remove("active"));
    link.classList.add("active");
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('accountModal');
  const openBtn = document.getElementById('addAccountBtn');
  const closeBtn = document.querySelector('.close-btn');
  openBtn.addEventListener('click', () => {
    modal.style.display = 'flex';
  });
  closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
  });
  window.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const addAccountBtn = document.getElementById('addAccountBtn');
  const sidebarLinks = document.querySelectorAll('.nav_link');
  addAccountBtn.style.display = 'none';
  sidebarLinks.forEach(link => {
      link.addEventListener('click', (e) => {
          e.preventDefault(); 
          if (link.id === 'balancesLink') {
            addAccountBtn.style.display = 'block';
          } else {
            addAccountBtn.style.display = 'none';
          }
      });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.nav_link');
  const dashboardContent = document.getElementById('dashboardContent');
  dashboardContent.classList.remove('visible');
  dashboardContent.style.display = 'none';
  sidebarLinks.forEach(link => {
      link.addEventListener('click', () => {
          sidebarLinks.forEach(link => link.classList.remove('active'));
          link.classList.add('active');
          if (link.id === 'balancesLink') {
              dashboardContent.style.display = 'block';
              dashboardContent.classList.add('visible');
          } else {
              dashboardContent.classList.remove('visible');
              dashboardContent.style.display = 'none';
          }
      });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const deleteButtons = document.querySelectorAll('.delete-btn');
  deleteButtons.forEach(button => {
    button.addEventListener('click', event => {
      const row = event.target.closest('tr');
      const cardNumber = row.dataset.cardNumber;
      if (confirm("Are you sure you want to delete this account?")) {
        fetch(`/delete_account/${cardNumber}`, { method: 'POST' })
          .then(response => {
            if (response.ok) {
              row.remove();
              alert("Account deleted successfully!");
            } else {
              alert("Failed to delete account.");
            }
          })
          .catch(error => {
            console.error("Error deleting account:", error);
            alert("An error occurred while deleting the account.");
          });
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const content = document.querySelector('.content');
  sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      content.classList.toggle('with-sidebar');
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.nav_link');
  const transactionContent = document.getElementById('transactionContent');
  transactionContent.classList.remove('visible');
  transactionContent.style.display = 'none';
  sidebarLinks.forEach(link => {
      link.addEventListener('click', () => {
          sidebarLinks.forEach(link => link.classList.remove('active'));
          link.classList.add('active');
          if (link.id === 'transactionsLink') {
              transactionContent.style.display = 'block';
              transactionContent.classList.add('visible');
          } else {
              transactionContent.classList.remove('visible');
              transactionContent.style.display = 'none';
          }
      });
  });
});

function openTransactionModal() {
  document.getElementById("transactionModalWindow").style.display = "block";
}
function closeTransactionModal() {
  document.getElementById("transactionModalWindow").style.display = "none";
}

window.onclick = function(event) {
  const modal = document.getElementById("transactionModalWindow");
  if (event.target === modal) {
      modal.style.display = "none";
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const addTransactionBtn = document.getElementById('openTransactionModalBtn');
  const transactionContent = document.getElementById('transactionContent');
  const sidebarLinks = document.querySelectorAll('.nav_link');
  addTransactionBtn.style.display = 'none';
  transactionContent.style.display = 'none';
  sidebarLinks.forEach(link => {
      link.addEventListener('click', () => {
          if (link.id === 'transactionsLink') {
              addTransactionBtn.style.display = 'block';
              transactionContent.style.display = 'block';
          } else {
              addTransactionBtn.style.display = 'none';
              transactionContent.style.display = 'none';
          }
      });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const deleteButton = document.querySelector('.delete-button');
  const transactionTable = document.querySelector('#transactionsTable tbody');
  if (transactionTable && transactionTable.children.length === 0) {
    deleteButton.style.display = 'none';
  }
  const observer = new MutationObserver(() => {
    if (transactionTable.children.length === 0) {
      deleteButton.style.display = 'none';
    } else {
      deleteButton.style.display = 'block';
    }
  });
  if (transactionTable) {
    observer.observe(transactionTable, { childList: true });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.nav_link');
  const expensesContent = document.getElementById('expensesContent');
  expensesContent.style.display = 'none';
  sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
      sidebarLinks.forEach(link => link.classList.remove('active'));
      link.classList.add('active');
      if (link.id === 'expensesLink') {
        expensesContent.style.display = 'block';
        expensesContent.classList.add('fade-in');
      } else {
        expensesContent.classList.remove('fade-in');
        expensesContent.style.display = 'none';
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.nav_link');
  const goalModal = document.getElementById('goalModal');
  goalModal.style.display = 'none';
  sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
      sidebarLinks.forEach(link => link.classList.remove('active'));
      link.classList.add('active');
      if (link.id === 'goalsLink') {
        goalModal.style.display = 'block';
        goalModal.classList.add('fade-in');
      } else {
        goalModal.classList.remove('fade-in');
        goalModal.style.display = 'none';
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const transactionsTable = document.getElementById('transactionsTable');
  const selectAllCheckbox = document.getElementById('selectAll');
  const deleteButton = document.querySelector('.delete-button');
  if (transactionsTable) {
    const transactionRows = transactionsTable.querySelectorAll('tbody tr');
    const transactionCheckboxes = transactionsTable.querySelectorAll('tbody input[type="checkbox"]');
    selectAllCheckbox.addEventListener('click', () => {
      const isChecked = selectAllCheckbox.checked;
      transactionCheckboxes.forEach(checkbox => {
        checkbox.checked = isChecked;
      });
    });
    deleteButton.addEventListener('click', event => {
      event.preventDefault();
      const selectedIds = Array.from(transactionCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
      if (selectedIds.length === 0) {
        alert("Please select at least one transaction to delete.");
        return;
      }
      if (confirm("Are you sure you want to delete the selected transactions?")) {
        fetch(`/delete_selected_transactions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({ transaction_ids: selectedIds }),
        })
          .then(response => {
            if (response.ok) {
              transactionRows.forEach(row => {
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox && selectedIds.includes(checkbox.value)) {
                  row.remove();
                }
              });
              alert("Selected transactions deleted successfully!");
            } else {
              alert("Failed to delete transactions. Please try again.");
            }
          })
          .catch(error => {
            console.error("Error deleting transactions:", error);
            alert("An error occurred while deleting transactions.");
          });
      }
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const sidebarLinks = document.querySelectorAll('.nav_link');
  const billsLink = document.getElementById('billsLink');
  const billContent = document.getElementById('billContent');
  const billModal = document.getElementById('billModal');
  const addBillBtn = document.getElementById('addBillBtn');
  const closeModalBtn = document.querySelector('.close-btn');
  billContent.classList.remove('visible');
  billModal.classList.remove('visible');
  addBillBtn.classList.remove('visible');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (link !== billsLink) {
        billContent.classList.remove('visible');
        billModal.classList.remove('visible');
        addBillBtn.classList.remove('visible');
      }
    });
  });
  billsLink.addEventListener('click', () => {
    billContent.classList.add('visible');
    addBillBtn.classList.add('visible');
  });
  addBillBtn.addEventListener('click', () => {
    billModal.classList.add('visible');
  });
  closeModalBtn.addEventListener('click', () => {
    billModal.classList.remove('visible');
  });
  window.addEventListener('click', event => {
    if (event.target === billModal) {
      billModal.classList.remove('visible');
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const notificationBell = document.getElementById("notificationBell");
  const notificationModal = document.getElementById("notificationModal");
  const closeModal = document.getElementById("closeModal");
  const billDetails = document.getElementById("billDetails");
  function fetchBillDetails() {
      fetch('/get_upcoming_bills')
          .then(response => response.json())
          .then(data => {
              billDetails.innerHTML = "";
              if (data.bills.length > 0) {
                  data.bills.forEach(bill => {
                      const listItem = document.createElement("li");
                      listItem.textContent = `Bill: ${bill.bill_name}, Amount: $${bill.amount}, Due: ${bill.due_date}`;
                      billDetails.appendChild(listItem);
                  });
              } else {
                  const noBills = document.createElement("li");
                  noBills.textContent = "No upcoming bills";
                  billDetails.appendChild(noBills);
              }
          })
          .catch(error => {
              console.error("Error fetching bill details:", error);
          });
  }
  notificationBell.addEventListener("click", function () {
      fetchBillDetails();
      notificationModal.style.display = "block";
  });
  closeModal.addEventListener("click", function () {
      notificationModal.style.display = "none";
  });
  window.addEventListener("click", function (event) {
      if (event.target === notificationModal) {
          notificationModal.style.display = "none";
      }
  });
});
window.addEventListener('load', function () {
  document.body.classList.add('sidebar-open'); // Open the sidebar by default
  const dashboardLink = document.querySelector('#dashboardLink');
  if (dashboardLink) {
      dashboardLink.classList.add('active'); // Add 'active' class to the dashboard link
  }
});
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.querySelector('.sidebar');
  const content = document.querySelector('.content');
  sidebar.classList.add('open');  // Add the 'open' class to open the sidebar
  content.classList.add('with-sidebar');  // Adjust content layout accordingly
});
