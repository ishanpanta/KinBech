var updateBtns = document.getElementsByClassName("update-cart")

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        // updateBtns[i].innerText = "IN CART"
        // updateBtns[i].disabled = true
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log("Product ID: ", productId, "Action: ", action)
        console.log("User: ", user)

        if (user==="AnonymousUser"){
            console.log("Not logged in")
        } else {
            updateUserOrder(productId, action)
        }
    })
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
