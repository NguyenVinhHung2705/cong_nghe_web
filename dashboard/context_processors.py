def account_context(request):
    if not request.session.get('account_id'):
        return {}
    from .models import Account
    account = Account.objects.get(id=request.session['account_id'])

    return {
        'account': account,
        'balance': account.wallet.balance,
        'total_cart_item': account.cart.quantity
    }