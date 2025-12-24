from django.urls import path
from .views import  *

urlpatterns = [
    path('', dashboard, name='dashboard'),  # URL rỗng trong app
    path('admin-page/', to_admin_page, name='to_admin_page'),  # URL cho trang admin
    path('view_cart/', to_view_cart, name='to_view_cart'),
    path('login/', to_login_page, name='to_login_page'),
    path('register/', to_register_page, name='to_register_page'),
    path('logout/', logout, name='logout'),
    path('profile/', to_profile_page, name='to_profile_page'),
    path('cart/add/<int:product_id>/<int:quantity>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_cart_item, name='remove_cart_item'),
    path('cart/checkout-selected/', checkout_selected, name='checkout_selected'),
    path('user/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('toggle/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('product/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('users/add/', add_user, name='add_user'),
    path('product/detail/<int:product_id>/', view_product_detail, name = 'view_product_detail'),
    path('checkout/', checkout_selected, name='checkout_selected'),
    path('order/place/', place_order, name='place_order'),
]