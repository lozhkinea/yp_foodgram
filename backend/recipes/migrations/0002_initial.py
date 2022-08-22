# Generated by Django 4.1 on 2022-08-22 09:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribe',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='subscribe',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subscriber',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.recipe',
            ),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                through='recipes.IngredientsAmount', to='recipes.ingredient'
            ),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.tag'),
        ),
        migrations.AddField(
            model_name='ingredientsamount',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.ingredient',
            ),
        ),
        migrations.AddField(
            model_name='ingredientsamount',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.recipe',
            ),
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=models.Index(fields=['name'], name='name_idx'),
        ),
        migrations.AddField(
            model_name='favotites',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.recipe',
            ),
        ),
        migrations.AddField(
            model_name='favotites',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.UniqueConstraint(
                fields=('user', 'author'), name='unique_subscribe)'
            ),
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.CheckConstraint(
                check=models.Q(('user', models.F('author')), _negated=True),
                name='self_subscribe',
            ),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping)'
            ),
        ),
        migrations.AddConstraint(
            model_name='favotites',
            constraint=models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favotites)'
            ),
        ),
    ]
