# Generated manually - Add project_version field to Label model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("labels", "0016_segmentation"),
    ]

    operations = [
        migrations.AddField(
            model_name="boundingbox",
            name="project_version",
            field=models.IntegerField(
                default=1, 
                help_text="Version of the project when this annotation was created"
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="project_version",
            field=models.IntegerField(
                default=1, 
                help_text="Version of the project when this annotation was created"
            ),
        ),
        migrations.AddField(
            model_name="relation",
            name="project_version",
            field=models.IntegerField(
                default=1, 
                help_text="Version of the project when this annotation was created"
            ),
        ),
        migrations.AddField(
            model_name="segmentation",
            name="project_version",
            field=models.IntegerField(
                default=1, 
                help_text="Version of the project when this annotation was created"
            ),
        ),
        migrations.AddField(
            model_name="span",
            name="project_version",
            field=models.IntegerField(
                default=1, 
                help_text="Version of the project when this annotation was created"
            ),
        ),
        migrations.AddField(
            model_name="textlabel",
            name="project_version",
            field=models.IntegerField(
                default=1, 
                help_text="Version of the project when this annotation was created"
            ),
        ),
    ] 