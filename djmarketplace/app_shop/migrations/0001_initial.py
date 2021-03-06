# Generated by Django 4.0 on 2022-06-25 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, error_messages={'invalid': 'Введите допустимое значение', 'required': 'Это поле является обязательным'}, max_length=100, verbose_name='item title')),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.TextField(blank=True, error_messages={'invalid': 'Введите допустимое значение', 'required': 'Это поле является обязательным'}, verbose_name='item description ')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='create date')),
                ('update_at', models.DateTimeField(auto_now_add=True, verbose_name='update date')),
                ('image', models.ImageField(blank=True, null=True, upload_to='item_image/%Y/%m/%d', verbose_name='item image')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='price')),
                ('discount', models.PositiveIntegerField(verbose_name='discount')),
                ('stock', models.PositiveIntegerField(verbose_name='quantity')),
                ('available', models.BooleanField(default=True, verbose_name='available')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
                'db_table': 'app_items',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Category')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('image', models.ImageField(blank=True, default='static/img/default_category.jpg', null=True, upload_to='item_category/%Y/%m/%d', verbose_name='item image')),
            ],
            options={
                'verbose_name': 'Item category',
                'verbose_name_plural': 'Item categories',
                'db_table': 'app_item_category',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShopCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Shop category')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='category description ')),
                ('icon', models.ImageField(blank=True, default='static/img/default_category.jpg', null=True, upload_to='shop_category/', verbose_name='Shop avatar')),
            ],
            options={
                'verbose_name': 'Shop category',
                'verbose_name_plural': 'Shop categories',
                'db_table': 'app_shop_category',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Shop name')),
                ('slug', models.SlugField(max_length=100, null=True, unique=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='Shop description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('image', models.ImageField(blank=True, default='static/img/default_shop.jpg', null=True, upload_to='shop_avatar/%Y/%m/%d/', verbose_name='Shop avatar')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shops', to='app_shop.shopcategory', verbose_name='category')),
            ],
            options={
                'verbose_name': 'Shop',
                'verbose_name_plural': 'Shops',
                'db_table': 'app_shop',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='RepostList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='quantity item')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_shop.item', verbose_name='item')),
            ],
            options={
                'verbose_name': 'Sale report',
                'verbose_name_plural': 'Sale reports',
                'db_table': 'app_report_list',
                'ordering': ('quantity',),
            },
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app_shop.itemcategory', verbose_name='category'),
        ),
        migrations.AddField(
            model_name='item',
            name='shop',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app_shop.shop', verbose_name='seller'),
        ),
        migrations.AlterIndexTogether(
            name='item',
            index_together={('id', 'slug')},
        ),
    ]
