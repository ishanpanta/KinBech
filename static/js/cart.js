var updateBtns = document.getElementsByClassName("update-cart")

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log("Product ID: ", productId, "Action: ", action)
        console.log("User: ", user)

        if (user==="AnonymousUser"){
            addCookieItem(productId, action)
        } else {
            updateUserOrder(productId, action)
        }
    })
}

function addCookieItem(productId, action) {
    console.log("Not logged in...",)

    if (action == 'add') {
        if (cart[productId] == null) {
            cart[productId] = {'quantity':1}

        }else{
            cart[productId]['quantity'] += 1  
        }
    }

    if (action == 'remove') {
        cart[productId]['quantity'] -= 1
        
        if (cart[productId]['quantity'] <= 0) {
            console.log("Item has been deleted")
            delete cart[productId]
        }
    }
    
    // +2 day from now
    let date = new Date(Date.now() + (86400e3 * 2))
    date = date.toUTCString()

    // updating the broswer cookie
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/; expires=" + date;

    location.reload()
}

function updateUserOrder(productId, action) {
    console.log("User is logged in, sending data...")

    // this is where we want to send data
    var url = "/update_item/"

    fetch(url, {
        method: 'POST',       // POST is used to send data to the server.
        headers:{             // we need to tell fetch, we are going to be passing JSON
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'action':action})      // we cannot send object to the backend we need to send it as the string
    })

    // return a promise. We will get the response after we send the data to the views
    .then((response) => {
        return response.json()       // converted response to the json value
    })

    // print data to console
    .then((data) => {
        console.log('data:', data)
        location.reload()
    })
}