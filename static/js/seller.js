console.log("Hello World")

////////////////////////// Notification //////////////////////////
const notiBtn = document.querySelector("#noti-btn");
const closeBtn = document.querySelector(".close-notification");
const notiOverlay = document.querySelector(".notification-overlay");
const notiDOM = document.querySelector(".notification");

notiBtn.addEventListener("click", function(){
    notiOverlay.classList.add('transparentBcg');
    notiDOM.classList.add('showCart');
})

closeBtn.addEventListener("click", function(){
    notiOverlay.classList.remove('transparentBcg');
    notiDOM.classList.remove('showCart');
})

// notiOverlay.addEventListener("click", function(){
//     notiOverlay.classList.remove('transparentBcg');
//     notiDOM.classList.remove('showCart');
// })
// End of Notification



////////////////////////// Total Price of the orders //////////////////////////
individualOrderItemPrice = document.getElementsByClassName("orderItemPrice")
var total = 0

for (var i = 0; i < individualOrderItemPrice.length; i++) {
    total += Number(individualOrderItemPrice[i].innerHTML.replace(/[^0-9.-]+/g,""))
}
// Fix two decimal points. And, Put comma after thousands place. 
document.getElementById("totalPrice").innerHTML = "$ " + total.toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); + " /-"
// The END
