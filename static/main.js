const form = document.getElementById("giftForm")
const giftsContainer = document.getElementById("gifts");

async function loadGifts() {
    try {
        const response = await fetch('/gifts');
        if (!response.ok) {
            console.error('Failed to load gifts:', response.status);
            return;
        }
        const gifts = await response.json();
        console.log('Loaded gifts:', gifts);
        
        giftsContainer.innerHTML = '';
        gifts.forEach(gift => {
            const item = document.createElement("div");
            item.style.marginBottom = "10px";
            item.style.padding = "10px";
            item.style.border = "1px solid #ccc";
            item.style.borderRadius = "5px";
            
            const text = document.createElement("p");
            text.style.margin = "0 0 5px 0";
            text.textContent = `Gift for ${gift.name}: ${gift.gift}`;
            
            if (gift.completed) {
                text.style.textDecoration = "line-through";
                text.style.color = "#888";
            }
            
            const button = document.createElement("button");
            button.textContent = gift.completed ? "✓ Completed" : "Mark Complete";
            button.style.padding = "5px 10px";
            button.style.cursor = "pointer";
            button.disabled = gift.completed;
            
            button.addEventListener("click", async () => {
                const password = prompt("Enter password to mark as complete:");
                if (password) {
                    await fetch(`/gifts/${gift.id}`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ password })
                    });
                    await loadGifts();
                }
            });
            
            item.appendChild(text);
            item.appendChild(button);
            giftsContainer.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading gifts:', error);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = form.elements.name.value;
    const gift = form.elements.gift.value;
    const password = form.elements.password.value;

    try {
        const response = await fetch('/gifts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, gift, password })
        });

        if (response.ok) {
            form.reset();
            await loadGifts();
        } else {
            alert('Error adding gift. Check your password and try again.');
            console.error('Error response:', response.status);
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('Error adding gift');
    }
});

loadGifts();
