$(document).ready(function(e) {
    function updateCart(){
        let url = $(this).closest('form').attr('action')
        let data1 = $(this).closest('form').serialize();
        let dataArray = data1.split('&');
        let dataObj = {};
        for (let i = 0; i < dataArray.length; i++) {
            let pair = dataArray[i].split('=');
            let key = decodeURIComponent(pair[0]); 
            let value = decodeURIComponent(pair[1]); 
            dataObj[key] = value; 
        }
        
        $.ajax({
            url: url,
            method:'post',
            data: data1,
            beforeSend: function(){
              $('.loading-here').addClass("bg-loading")
              $(".loading-here").html(`<div class="spinner-border text-primary" role="status">
              <span class="sr-only">Loading...</span>
            </div>`)
            },
            complete: function(){
              $('.loading-here').removeClass("bg-loading")
              $('.loading-here').empty()
            },
            success: function(data){
                let cart_items_html = data.cart_items.map(item => `
                <div class="px-4 py-5 px-md-6 border-bottom">
              <div class="media">
              <a href="/shop/product/${item.product.slug}/" class="d-block"><img src="${item.product.image}" width="120" class="img-fluid" alt="image-description"></a>
               <div class="media-body ml-4d875">
              <div class="text-primary text-uppercase font-size-1 mb-1 text-truncate"><a href="/shop/product/${item.product.slug}/">SÁCH</a></div>
              <h2 class="woocommerce-loop-product__title h6 text-lh-md mb-1 text-height-2 crop-text-2">
              <a href="/shop/product/${item.product.slug}/" class="text-dark">${item.product.name}</a>
              </h2>
              <div class="font-size-2 mb-1 text-truncate">
                ${item.product.authors.map(author => `
                    <a href="/shop/author/${author.slug}/" class="text-gray-700">${author.name}</a>
                    `).join(', ')}
              </div>
              <div class="price d-flex align-items-center font-weight-medium font-size-3">
              <span class="woocommerce-Price-amount amount">${item.quantity} x ${new Intl.NumberFormat("vi-VN", {style: "currency", currency: "VND"}).format(item.product.price)}</span>
              </div>
              </div>
              <form action='/cart/' method='post' class="mt-3 ml-3">
                <input type="hidden" name="csrfmiddlewaretoken" value="${dataObj['csrfmiddlewaretoken']}"/>
                <input type="hidden" name="product_slug" value="${item.product.slug}"/>
                <input type="hidden" name="operation" value="remove"/>
                <input type="hidden" name="type" value="ajax"/>
              <div class="btn text-dark remove-from-cart"><i class="fas fa-times"></i></div>
              </form>
              </div>
              </div>
                `).join('')

                let html = `${cart_items_html}
            <div class="px-4 py-5 px-md-6 d-flex justify-content-between align-items-center font-size-3">
              <h4 class="mb-0 font-size-3">Tổng cộng:</h4>
              <div class="font-weight-medium">${new Intl.NumberFormat("vi-VN", {style: "currency", currency: "VND"}).format(data.cart_subtotal)}</div>
            </div>
            <div class="px-4 mb-8 px-md-6">
              <a href="/cart/" class="btn btn-block py-4 rounded-0 btn-outline-dark mb-4">Xem giỏ hàng</a>
              <a href="/payment/checkout/" class="btn btn-block py-4 rounded-0 btn-dark">Thanh toán</a>
            </div>`
                $("#cart_items_count").html(`<i class="flaticon-icon-126515 mr-3 font-size-5"></i>Giỏ hàng của bạn (${data.cart_items_count})`)
                $('#cart_items_content').html(html)
                $('.remove-from-cart').click(updateCart)
                $('#cart_subtotal_header').text(`${new Intl.NumberFormat("vi-VN", {style: "currency", currency: "VND"}).format(data.cart_subtotal)}`)
                $('#cart_items_count_header').text(`${data.cart_items_count}`)
                $('#sidebarNavToggler1').click()
            }
        })
    }
    $('.add-to-cart').click(updateCart)
    $('.remove-from-cart').click(updateCart)
})