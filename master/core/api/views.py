from django.http import JsonResponse, HttpRequest
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404

from .serializers import *
from .paginations import *
from ..models import Cart


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductSetPagination
    queryset = Product.objects.select_related('category').filter(is_active=True).order_by('-id')


class ProductDetailAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related('category').filter(is_active=True)
    serializer_class = ProductSerializer


class CategoryListAPIView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).order_by('-id')

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = CategorySerializer(queryset, many=True)

        data = serializer.data
        response = {
            'status': True,
            'data': data
        }
        return Response(response)


class CategoryDetailAPIView(RetrieveAPIView):
    serializer_class = CategoryDetailsSerializer
    queryset = Category.objects.filter(is_active=True).order_by('-id')

    def retrieve(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        response = {
            'status': True,
            'data': data
        }
        return Response(response)


def add_to_cart_api(request: HttpRequest, id: int) -> JsonResponse:
    item = get_object_or_404(Product, id=id)
    if not item:
        return JsonResponse({'status': False, 'message': 'Product not found'}, safe=True)
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'Please login to continue'}, safe=True)
    if Cart.objects.filter(user=request.user, product=item).exists():
        cart = Cart.objects.get(user=request.user, product=item)
        cart.quantity += 1
        cart.save()
    else:
        Cart.objects.create(user=request.user, product=item, quantity=1)

    cart_total_items = Cart.objects.filter(user=request.user).count()

    return JsonResponse({'status': True, 'product_price': item.price, 'cart_total_items': cart_total_items,
                         'message': 'Successfully added to cart'},
                        safe=True)


def remove_from_cart(request: HttpRequest, id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'Please login to continue'}, safe=True)
    try:
        item = Cart.objects.get(id=id)
        item.delete()
        return JsonResponse({'status': True, 'message': 'Item removed from cart'}, safe=True)
    except:
        return JsonResponse({'status': False, 'message': 'Item not found'}, safe=True)


def remove_quantity_from_cart(request: HttpRequest, id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'message': 'Please login to continue'}, safe=True)
    cart_item = get_object_or_404(Cart, id=id)
    # if quantity is 1 and we still need to decrease qty, then we will remove the item from cart
    if cart_item.quantity == 1:
        cart_item.delete()

        cart_total_items = Cart.objects.filter(user=request.user).count()
        return JsonResponse({
            'status': True,
            'product_price': cart_item.product.price,
            'cart_total_items': cart_total_items,
            'message': 'Successfully removed quantity from the cart'
        }, safe=True)
    # decreasing quantity
    cart_item.quantity -= 1
    cart_item.save()

    cart_total_items = Cart.objects.filter(user=request.user).count()

    return JsonResponse({
        'status': True,
        'product_price': cart_item.product.price,
        'cart_total_items': cart_total_items,
        'message': 'Successfully removed quantity from the cart'
    }, safe=True)
