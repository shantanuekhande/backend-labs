from django.core.management.base import (
    BaseCommand
)

from payments.services.reconciliation_service import (
    ReconciliationService
)


class Command(BaseCommand):

    help = (
        "Reconcile stale payments"
    )

    def handle(self, *args, **kwargs):

        self.stdout.write(
            "Starting reconciliation..."
        )

        ReconciliationService\
            .reconcile_pending_payments()

        self.stdout.write(
            self.style.SUCCESS(
                "Reconciliation completed"
            )
        )