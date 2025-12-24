from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib import messages
from .models import  *
from datetime import date
# Create your views here.
def dashboard(request):
    products = Product.objects.select_related('category').all()

    if not request.session.get('account_id'):
        return render(request, 'dashboard/dashboard.html', {
            'products': products
        })

    account_id = request.session.get('account_id')
    account = Account.objects.get(id=account_id)

    return render(request, 'dashboard/dashboard.html', {
        'account': account,
        'balance': account.wallet.balance,
        'total_cart_item': account.cart.quantity,
        'products': products
    })

def to_admin_page(request):
    users = Account.objects.all().order_by('id')
    products = Product.objects.all().order_by('product_id')
    categories = Category.objects.all().order_by('category_id')
    return render(request, 'dashboard/admin_page.html', {
        'users': users,
        'products' : products
    })

def to_view_cart(request):
    if not request.session.get('account_id'):
        return render(request, 'dashboard/login_page.html')

    account_id = request.session.get('account_id')
    account = Account.objects.get(id=account_id)
    cart = account.cart
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
    return render(request, 'dashboard/view_cart.html', {
        'cart_items': cart_items,
    })

def to_login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = Account.objects.filter(username=username, password=password).first()
        if user:
            if user.status != "normal":
                error_message = "Tài khoản đang bị khóa, vui lòng liên hệ admin để biết thêm chi tiết"
                return render(request, 'dashboard/login_page.html', {'error_message': error_message})
            else:        
                request.session['account_id'] = user.id
                request.session['username'] = user.username
                request.session['password'] = user.password
                request.session['role'] = user.role
                request.session['status'] = user.status
                return redirect('dashboard')
        else:
            error_message = "Tên đăng nhập hoặc mật khẩu không đúng."
            return render(request, 'dashboard/login_page.html', {'error_message': error_message})
    return render(request, 'dashboard/login_page.html')

def to_register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if(password != confirm_password):
            error_message = "Mật khẩu không trùng nhau"
            return render(request, 'dashboard/register_page.html', {'error_message': error_message})
        if Account.objects.filter(username=username).exists():
            error_message = "Tên đăng nhập đã tồn tại."
            return render(request, 'dashboard/register_page.html', {'error_message': error_message})
        account = Account.objects.create(
            username = username,
            password = password,
        )

        AccountProfile.objects.create(
            account = account,
            full_name = "Chưa có",
            date_of_birth = date(2025, 1, 1),
            email = f"this is {username}@gmail.com",
            phone_number = "0123456789"
        )

        Cart.objects.create(
            account = account
        )

        Wallet.objects.create(
            account = account
        )
        return render(request, 'dashboard/register_page.html', {'success_message': "Đăng kí thành công. Vui lòng đăng nhập."})
    return render(request, 'dashboard/register_page.html')

def logout(request):
    request.session.flush()   
    return render(request, 'dashboard/dashboard.html')

def to_profile_page(request):
    return render(request, 'dashboard/profile_page.html')

def add_to_cart(request, product_id, quantity):
    if not request.session.get('account_id'):
        return render(request, 'dashboard/login_page.html')

    account_id = request.session.get('account_id')
    account = Account.objects.get(id=account_id)
    cart = account.cart
    product = get_object_or_404(Product, product_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        # đã tồn tại → tăng số lượng
        cart_item.quantity += quantity
        cart_item.save()
    else:
    # 5. Tăng tổng quantity của cart
        cart.quantity += 1
        cart.save()

    return redirect('to_view_cart')

def remove_cart_item(request, item_id):
    if request.method == 'GET':
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = cart_item.cart

        # trừ tổng quantity của cart
        cart.quantity -= 1
        cart.save()

        cart_item.delete()

    return redirect('to_view_cart')

def checkout_selected(request):
    if request.method != "POST":
        return redirect("to_view_cart")

    account_id = request.session.get("account_id")
    if not account_id:
        return redirect("to_login_page")

    selected_ids = request.POST.getlist("selected_items")
    if not selected_ids:
        # thích thì dùng messages hoặc SweetAlert ở frontend
        return redirect("to_view_cart")

    account = Account.objects.select_related("cart").get(id=account_id)
    cart = account.cart

    # CHỈ lấy những item thuộc cart của user
    items = (CartItem.objects
             .filter(cart=cart, id__in=selected_ids)
             .select_related("product"))

    if not items.exists():
        return redirect("to_view_cart")

    # Tính tổng
    total = 0
    for item in items:
        item.subtotal = item.product.price * item.quantity
        total += item.product.price * item.quantity

    return render(request, "dashboard/checkout.html", {
        "items": items,
        "total": total
    })
    

def delete_user(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    user.delete()
    return redirect('to_admin_page')

def toggle_user_status(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    user.status = not user.status
    user.save()
    return redirect('to_admin_page')

def delete_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product.delete()
    return redirect('to_admin_page')

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        # tạo user
        Account.objects.create(
            username=username,
            password=password,  # mã hóa mật khẩu
            role=role,
        )

        messages.success(request, 'Thêm người dùng thành công')
        return redirect('to_admin_page')
    
def view_product_detail(request, product_id):
    product = get_object_or_404(Product, product_id = product_id)
    return render(request, 'dashboard/product_detail.html', {
        'product' : product
    })

def place_order(request):
    if request.method != "POST":
        return redirect("to_view_cart")

    account_id = request.session.get("account_id")
    if not account_id:
        return redirect("to_login_page")

    receiver_name = (request.POST.get("receiver_name") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    address = (request.POST.get("address") or "").strip()
    note = (request.POST.get("note") or "").strip()

    selected_ids = request.POST.getlist("selected_items")
    if not selected_ids:
        return redirect("to_view_cart")

    # TODO: lọc CartItem theo cart của user rồi tạo Order + OrderItem
    # TODO: trừ tiền ví nếu có wallet
    # TODO: xoá các CartItem đã checkout

    return redirect("dashboard")



