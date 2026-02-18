from django.db import migrations


def update_status_forward(apps, schema_editor):
    ManualDiscrepancy = apps.get_model('projects', 'ManualDiscrepancy')
    ManualDiscrepancy.objects.filter(status='resolved').update(status='solved')
    ManualDiscrepancy.objects.filter(status='unresolved').update(status='unsolved')


def update_status_backward(apps, schema_editor):
    ManualDiscrepancy = apps.get_model('projects', 'ManualDiscrepancy')
    ManualDiscrepancy.objects.filter(status='solved').update(status='resolved')
    ManualDiscrepancy.objects.filter(status='unsolved').update(status='unresolved')


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_remove_manualdiscrepancy_label_counts_and_more'),
    ]

    operations = [
        migrations.RunPython(update_status_forward, update_status_backward),
    ] 