from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from inventory.models import Product


class Command(BaseCommand):
    help = "Create demo users and sample products."

    def handle(self, *args, **options):
        User = get_user_model()

        # Demo admin account
        admin, _ = User.objects.get_or_create(
            username="demo_admin",
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("DemoAdmin-123")
        admin.save()

        # Demo shopper account
        shopper, _ = User.objects.get_or_create(
            username="shopper",
        )
        shopper.set_password("ShopperDemo-123")
        shopper.is_staff = False
        shopper.is_superuser = False
        shopper.save()

        # Sample products
        products = [
            {
                "name": "Wireless Mouse",
                "sku": "DEMO-MOU-001",
                "description": "Wireless optical mouse",
                "price": "25.90",
                "stock": 100,
                "is_active": True,
            },
            {
                "name": "Gaming Keyboard",
                "sku": "DEMO-KEY-001",
                "description": "Mechanical gaming keyboard",
                "price": "79.90",
                "stock": 30,
                "is_active": True,
            },
            {
                "name": "USB-C Hub",
                "sku": "DEMO-HUB-001",
                "description": "Multi-port USB-C hub",
                "price": "39.90",
                "stock": 0,
                "is_active": True,
            },
        ]

        for product_data in products:
            Product.objects.update_or_create(
                sku=product_data["sku"],
                defaults=product_data,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data ready!\n"
                "Admin: demo_admin / DemoAdmin-123\n"
                "Shopper: shopper / ShopperDemo-123"
            )
        )