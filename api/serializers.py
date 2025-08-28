# from rest_framework import serializers
# from .models import GoldTransaction
# from decimal import Decimal

# class GoldTransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GoldTransaction
#         # We only need user_name and weight for input
#         fields = [
#             'transaction_id',
#             'user_name',
#             'gold_rate_per_gram_usd',
#             'weight_in_grams',
#             'total_price_usd',
#             'timestamp'
#         ]
#         # These fields are calculated or set by the server, not provided by the client
#         read_only_fields = [
#             'transaction_id',
#             'gold_rate_per_gram_usd',
#             'total_price_usd',
#             'timestamp'
#         ]

from rest_framework import serializers
from .models import GoldTransaction
from decimal import Decimal

class GoldTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldTransaction
        fields = '__all__'
        read_only_fields = ['transaction_id', 'timestamp', 'gold_rate_per_gram_usd', 'total_price_usd']

    def create(self, validated_data):
        # Step 1: Fetch/calculate gold rate
        gold_rate = Decimal("75.50")  # (in real app: fetch from API or DB)

        # Step 2: Calculate total price
        weight = validated_data["weight_in_grams"]
        total_price = gold_rate * weight

        # Step 3: Add these fields to validated_data
        validated_data["gold_rate_per_gram_usd"] = gold_rate
        validated_data["total_price_usd"] = total_price

        # Step 4: Save and return
        return super().create(validated_data)
