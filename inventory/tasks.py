from celery import shared_task
from django.core.mail import send_mail
from .models import Product, Supplier
from django.contrib.auth.models import User
import csv
from io import StringIO
from django.db import models
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_csv(file_data, user_email):
    errors = []
    success_count = 0
    file = StringIO(file_data)
    reader = csv.DictReader(file)

    for row in reader:
        try:
            # Validate required fields
            if not all(key in row for key in ['name', 'description', 'price', 'supplier']):
                errors.append(f"Missing required fields in row: {row}")
                continue

            # Get or create the supplier
            supplier, created = Supplier.objects.get_or_create(
                name=row['supplier'],
                user=User.objects.get(email=user_email)
            )

            # Create the product
            Product.objects.create(
                name=row['name'],
                description=row['description'],
                price=float(row['price']),  # Ensure price is a float
                supplier=supplier,
                user=User.objects.get(email=user_email)
            )
            success_count += 1
        except Exception as e:
            errors.append(f"Error processing row {row}: {str(e)}")
            logger.error(f"Error processing row {row}: {str(e)}")

    # Send email with results
    send_mail(
        'CSV Processing Complete',
        f"Successfully processed {success_count} records. Errors: {errors}",
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )


@shared_task
def generate_inventory_report(user_email):
    from .models import Inventory
    from django.template.loader import render_to_string
    from django.core.mail import EmailMessage
    print(f"processing in inventory report: {user_email}")
    low_stock = Inventory.objects.filter(quantity__lt=10, user__email=user_email)
    supplier_performance = Supplier.objects.annotate(total_products=models.Count('product')).filter(user__email=user_email)

    report = render_to_string('inventory/inventory_report.html', {
        'low_stock': low_stock,
        'supplier_performance': supplier_performance,
    })

    print(f"inventory report: {report}")

    email = EmailMessage(
        'Inventory Report',
        report,
        settings.EMAIL_HOST_USER,
        [user_email],
    )
    print(f"email processing in inventory report: {email}")
    email.content_subtype = "html"
    email.send()