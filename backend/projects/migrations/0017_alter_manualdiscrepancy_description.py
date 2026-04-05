from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_update_discrepancy_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manualdiscrepancy',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ] 