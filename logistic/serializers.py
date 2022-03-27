from rest_framework import serializers
from rest_framework.response import Response

from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = ['title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    # настройте сериализатор для склада
    class Meta:
        model = Stock
        fields = ['address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        for position in positions:
            StockProduct(
                stock=stock,
                product=position['product'],
                quantity=position['quantity'],
                price=position['price']
            ).save()

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        stocks_positions = StockProduct.objects.all().filter(stock_id=instance.id)
        for position in positions:
            for stock_pos in stocks_positions:
                if position['product'].id == stock_pos.product_id:
                    stock_pos.quantity = position['quantity']
                    stock_pos.price = position['price']
                    stock_pos.save()

        return stock
