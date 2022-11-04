import csv
from django.core.management import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = "Loads products and product categories from CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        with open(file_path, "r") as csv_file:
            data = list(csv.reader(csv_file, delimiter=","))
            for row in data[1:]:
                product_category = ProductCategory.objects.get_or_create(name=row[3], code=row[4])
                Product.objects.create(
                    name=row[0],
                    code=row[1],
                    price=row[2],
                    product_category=product_category[0]
                )
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )