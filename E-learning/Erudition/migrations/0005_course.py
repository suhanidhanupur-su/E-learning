"""Generated migration for Course model."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Erudition', '0004_liveclass'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True, blank=True)),
                ('short_description', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('course_image', models.ImageField(blank=True, null=True, upload_to='courses/')),
                ('instructor_name', models.CharField(max_length=255, blank=True)),
                ('duration', models.CharField(max_length=50, blank=True)),
                ('price', models.DecimalField(decimal_places=2, default='0.00', max_digits=8)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='courses', to='Erudition.category')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
